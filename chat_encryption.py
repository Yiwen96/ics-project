import math
import random

# RSA algorithm 

# Check whether n is a prime number
def prime(n): 
  if n <= 1: 
      return False
  for i in range(2, int(math.sqrt(n)) + 1): 
      if n % i == 0: 
          return False
  return True


# Produce a list of prime numbers below 100
def prime_list():
    prime_l = []
    for i in range(100): 
        if prime(i):
            prime_l.append(i)
    return prime_l


# Find greatest common factor
def gcd(a,b):
    if  a % b == 0:
        return b
    else:
        return gcd(b, a%b)
    
    
# Find the number e that is co-prime to s = (p-1)(q-1)
def co_prime(s):
    while True:
        e = random.choice(range(100))
        if gcd(e,s) == 1: 
        # if greatest common factor is 1, then co-prime
            break
    return e


# Find d according to (e * d) % s = 1
def find_d(e,s):
    for d in range(100000000): 
    # Randomly generate a number to get d is too hard
    # we can find a appropiate d in order
        if (e * d) % s == 1:
            return d

# Generate public and private keys elements
def ppke():
    a = prime_list()
    p = random.choice(a)
    q = random.choice(a)
    # shared number
    n = p * q
    # totient
    s = (p-1)*(q-1)
    #co-prime
    e = co_prime(s)
    d = find_d(e,s)
    print("Public Key:   n = ", n, " e = ",e)
    print("Private Key:   n = ", n, " d = ", d)
    pbvk=(n,e,d)
    return pbvk


# Produce public or private key
# pbvk is the result of ppke, which is (n, e, d)
# t indicate type: t=0 public; t=1 private
def generate_pbk_pvk(pbvk,t):
    pbk = (pbvk[0],pbvk[1]) #public key
    pvk = (pbvk[0],pbvk[2]) #private key
    if t == 0:
        return pbk
    if t == 1:
        return pvk


# Encryption
def encryption(A, key):
    # A is original message
    # key = (n, e)
    # coded message = (original message ^ e) % n
    B = [(pow(ord(i), key[1]) % key[0]) for i in A]
    return B

#
def decode(B, key):
    # B is coded message
    # key is (n. d)
    # original message = (coded message ^ d) % n
    A = [chr(pow(i, key[1]) % key[0]) for i in B]
    return ''.join(A)
    