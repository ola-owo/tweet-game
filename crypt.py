#!/usr/bin/python
from Crypto.Cipher import AES
import base64

#import modules
PADDING = '{'
BLOCK_SIZE = 32
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
KEY = '1337133713371337'

#prepare crypto method
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def encode(text):
    cipher = AES.new(KEY)
    encoded = EncodeAES(cipher, text)
    return encoded

def decode(text):
    cipher = AES.new(KEY)
    decoded = DecodeAES(cipher, text)
    return decoded
