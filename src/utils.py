import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import os
import datetime


def _pad(s):
    bs = AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

def _unpad(s):
    return s[:-ord(s[len(s)-1:])]


class aes:

    @staticmethod
    def encrypt(raw, key):
        raw = _pad(raw.decode('utf-8'))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    @staticmethod
    def decrypt(enc, key):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return _unpad(cipher.decrypt(enc[AES.block_size:]))


epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    global epoch
    return (dt - epoch).total_seconds() * 1000.0


def checksum(_bytes):
    from hashlib import md5
    m = md5()
    m.update(_bytes)
    
    def __reduce_checksum(cs):
        res = 0
        for i in range(0,16,2):
            res += (cs[i] << 8) + cs[i+1]
        return res.to_bytes(3, byteorder='big')[-2:]

    return __reduce_checksum(m.digest())


class ChecksumNotEqual(Exception):
    pass