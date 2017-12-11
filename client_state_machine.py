# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import chat_encryption as encrypt
M_UNDEF     = '0'
M_LOGIN     = '1'
M_CONNECT   = '2'
M_EXCHANGE  = '3'
M_LOGOUT    = '4'
M_DISCONNECT= '5'
M_SEARCH    = '6'
M_LIST      = '7'
M_POEM      = '8'
M_TIME      = '9'
M_PROTECT   = 'U'
S_OFFLINE   = 0
S_CONNECTED = 1
S_LOGGEDIN  = 2
S_CHATTING  = 3




class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.public_code=[]      
        self.private_code=[]
        self.peer_key={}
        self.protected=False

    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
        
    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT+'ok'):
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_code, peer_msg):
        # message from user is in my_msg, if it has an argument (e.g. "p 3")
        # the the argument is in my_msg[1:]
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE
                    
                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += "Time is: " + time_in
                            
                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    list_in = myrecv(self.s)
                    self.out_msg += "Here are all the users in the system:\n" + list_in
                    
                            
                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer)==True:
                        self.set_state(S_CHATTING)
                        self.out_msg+="Connected to "+peer+". Chat away!\n\n"
                        if self.protected==False:
                            pbvk = encrypt.ppke()
                            self.public_code=encrypt.generate_pbk_pvk(pbvk, 0)
                            self.private_code=encrypt.generate_pbk_pvk(pbvk, 1)
                            mysend(self.s,M_PROTECT+ self.me +';'+';'.join(map(str,self.public_code)))
                    else:
                        self.out_msg+="Connection unsuccessful"
                
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s,M_SEARCH+term)
                    out = myrecv(self.s)[1:].strip()
                    if (len(out)>0):
                        self.out_msg += out+"\n\n"
                    else:
                        self.out_msg+=term+" not found.\n\n"

                    
                elif my_msg[0] == 'p':
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s,M_POEM +poem_idx)
                    out = myrecv(self.s)[1:].strip()
                    if (len(out)>0):
                        self.out_msg += out+"\n\n"
                    else:
                        self.out_msg+='Sonnet '+"not found.\n\n"
                    
                else:
                    self.out_msg += menu
                    
            if len(peer_msg) > 0:
                if peer_code==M_CONNECT:
                    self.peer=peer_msg
                    self.out_msg+="Request from "+self.peer+"\n"
                    self.out_msg+="You are connected with "+self.peer
                    self.out_msg+= '.Chat away!\n'
                    if self.protected==False:
                            pbvk = encrypt.ppke()
                            self.public_code=encrypt.generate_pbk_pvk(pbvk, 0)
                            self.private_code=encrypt.generate_pbk_pvk(pbvk, 1)
                            mysend(self.s,M_PROTECT+ self.me +';'+';'.join(map(str,self.public_code)))
                    self.set_state(S_CHATTING)
                    
                    
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                for peer in self.peer_key.keys():
                    msg=encrypt.encryption(my_msg,self.peer_key[peer])
                    mysend(self.s, M_EXCHANGE +peer+",[" + self.me + "] " + ' '.join(msg))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            
            if len(peer_msg) > 0:    # peer's stuff, coming in
                if peer_code==M_CONNECT:
                    self.out_msg+="("+peer_msg+ ")"+"joined.\n"
                # when peer_msg is "bye", peer_code will be M_DISCONNECT
                elif peer_msg=="bye":
                    peer_code=M_DISCONNECT
                else:
                    word=peer_msg.split(',')[1]
                    self.out_msg+=encrypt.decode(word,self.private_code)
                    

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.state=S_LOGGEDIN
            # I got others' peer keys          
            if peer_code ==M_PROTECT:
                peer_msg=peer_msg[1:].split(';')
                self.peer_key[peer_msg[0]]=peer_msg[1:]

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state                       
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
            
        return self.out_msg


