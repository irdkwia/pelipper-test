# This is used to provide minimal SSLv3 support,
# which was dropped after Python 3.3.5
# If you are in Python 3.3.5 or lower, use shttpserver.py
# which uses the standard ssl package that had this support
# back then, and should theoretically be more stable

import rsa

import socket
from socketserver import BaseRequestHandler, TCPServer
from random import randrange
from base64 import b64decode

from hashlib import sha1, md5

from structure.database import *

with open("cert/server.key", "r") as file:
    privateKey = rsa.PrivateKey.load_pkcs1(file.read())
with open("cert/server.crt", "r") as file:
    cert = file.read()
with open("cert/nwc.crt", "r") as file:
    master = file.read()

# RC4 class implementation from:
# https://github.com/ctz/tls-hacking/blob/master/tls/crypt/rc4.py
class RC4:
    def __init__(self, key):
        self.S = [x for x in range(256)]
        j = 0
        for i in range(256):
            j = (j + self.S[i] + key[i % len(key)]) & 0xff
            self.swap(i, j)
        self.i = 0
        self.j = 0

    def swap(self, i, j):
        self.S[i], self.S[j] = self.S[j], self.S[i]

    def encrypt(self, pt):
        ct = []

        for p in pt:
            self.i = (self.i + 1) & 0xff
            self.j = (self.j + self.S[self.i]) & 0xff
            self.swap(self.i, self.j)
            k = self.S[(self.S[self.i] + self.S[self.j]) & 0xff]
            ct.append(p ^ k)

        return bytes(ct)

    def decrypt(self, ct):
        return self.encrypt(ct)

cert = b64decode(cert.split("-----BEGIN CERTIFICATE-----")[1].split("-----END CERTIFICATE-----")[0])
master = b64decode(master.split("-----BEGIN CERTIFICATE-----")[1].split("-----END CERTIFICATE-----")[0])

def PRF(secret, seed, len_out):
    i = 0
    output = bytearray()
    while len(output)<len_out:
        c = chr(ord("A")+i).encode("ascii")
        output += md5(secret + sha1(c*(i+1)+secret+seed).digest()).digest()
        i += 1
    return bytes(output[:len_out])
    
    
def val(b):
    return int.from_bytes(b, 'big')
def dat(n, l):
    return n.to_bytes(l, 'big')
def parse(b, l):
    x = []
    for i in range(0, len(b), l):
        x.append(val(b[i:i+l]))
    return x

class CustomHandler(BaseRequestHandler):
    def sendmessage(self, data, msgtype):
        self.request.send(dat(msgtype, 1))
        self.request.send(dat(0x300, 2))
        if self.sciphering:
            self.request.send(dat(len(data)+20, 2))
            self.request.send(self.rc4server.encrypt(data+sha1(self.servermackey + b'\\'*40 + sha1(self.servermackey + b'6'*40 + dat(self.sendseq,8) + dat(msgtype, 1) + dat(len(data), 2) + data).digest()).digest()))
        else:
            self.request.send(dat(len(data), 2))
            self.request.send(data)
        self.sendseq += 1
    
    def recvmessage(self):
        msgtype = val(self.request.recv(1))
        if msgtype==0:
            return 0, b''
        self.hchksslv = val(self.request.recv(2))
        #if sslv!=0x300:
        #    return 0, b''
        length = val(self.request.recv(2))
        data = bytearray()
        while len(data)<length:
            data += self.request.recv(length)
        data = bytes(data)
        if self.cciphering:
            data = self.rc4client.decrypt(data)
            mac = data[-20:]
            data = data[:-20]
            assert mac==sha1(self.clientmackey + b'\\'*40 + sha1(self.clientmackey + b'6'*40 + dat(self.recvseq,8) + dat(msgtype, 1) + dat(len(data), 2) + data).digest()).digest()
        self.recvseq += 1
        return msgtype, data
    
    def sendhandshake(self, data, handshaketype):
        hchk = dat(handshaketype, 1)+dat(len(data), 3)+data
        self.sendmessage(hchk, 0x16)
        self.hchksent += hchk
        
    def sendhello(self):
        data = dat(0x300, 2)
        self.servrand = bytes(randrange(256) for i in range(32))
        data += self.servrand # RNG
        self.ssid = bytes(randrange(256) for i in range(32))
        data += dat(32, 1) # SSID
        data += self.ssid
        data += dat(5, 2) # CIPHER
        data += dat(0, 1) # METHOD
        self.sendhandshake(data, 0x02)
    
    def sendcert(self):
        data = dat(len(cert)+len(master)+6, 3)+dat(len(cert), 3)+cert+dat(len(master), 3)+master
        self.sendhandshake(data, 0x0B)
    
    def sendhellodone(self):
        self.sendhandshake(b'', 0x0E)
    
    def sendfinished(self, currentmsg):
        md5_hash = md5(self.master + b'\\'*48 + md5(bytes(self.hchkall+currentmsg) + b'SRVR' + self.master + b'6'*48).digest()).digest()
        sha1_hash = sha1(self.master + b'\\'*40 + sha1(bytes(self.hchkall+currentmsg) + b'SRVR' + self.master + b'6'*40).digest()).digest()
        self.sendhandshake(md5_hash+sha1_hash, 0x14)
        
    def parsemessage(self):
        msgtype, data = self.recvmessage()
        if msgtype==0x00:
            return False
        elif msgtype==0x14:
            self.cciphering = True
            self.recvseq = 0
        elif msgtype==0x15:
            print("ALERT! (%d, %d)" % (data[0], data[1]))
        elif msgtype==0x16:
            self.hchksent = bytearray()
            orgdata = data
            handshaketype = data[0]
            length = val(data[1:4])
            if length!=len(data)-4:
                return False
            if handshaketype==1:
                sslv = val(data[4:6])
                self.clientrand = data[6:38]
                ssid_len = data[38]
                ssid = data[39:39+ssid_len]
                suites_len = val(data[39+ssid_len:39+ssid_len+2])
                suites = parse(data[39+ssid_len+2:39+ssid_len+2+suites_len], 2)
                methods_len = data[39+ssid_len+2+suites_len]
                methods = parse(data[39+ssid_len+2+suites_len+1:39+ssid_len+2+suites_len+1+methods_len], 1)
                if 0 not in methods or 5 not in suites or sslv!=0x300:
                    # Switch protocol, since it's not a Nintendo DS
                    self.underlying = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.underlying.connect((SERVER_ADDR, 8686))
                    self.underlying.send(dat(msgtype, 1)+dat(self.hchksslv, 2)+dat(len(orgdata), 2)+orgdata)
                    self.underlying.setblocking(0)
                    self.request.setblocking(0)
                    while True:
                        try:
                            d = self.request.recv(4096)
                        except Exception as e:
                            d = None
                        if d==b'':
                            break
                        if d is not None:
                            try:
                                self.underlying.send(d)
                            except Exception as e:
                                d = None
                        try:
                            d = self.underlying.recv(4096)
                        except Exception as e:
                            d = None
                        if d==b'':
                            break
                        if d is not None:
                            try:
                                self.request.send(d)
                            except Exception as e:
                                d = None
                        time.sleep(0.001)
                    return False
                else:
                    self.underlying = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.underlying.connect((SERVER_ADDR, 80))
                self.sendhello()
                self.sendcert()
                self.sendhellodone()
            elif handshaketype==16:
                self.premaster = data[4:]
                self.premaster = rsa.decrypt(self.premaster, privateKey)
                self.master = PRF(self.premaster, self.clientrand+self.servrand, 48)
                keyblock = PRF(self.master, self.servrand+self.clientrand, 72)
                self.clientmackey = keyblock[0:20]
                self.servermackey = keyblock[20:40]
                self.clientkey = keyblock[40:56]
                self.serverkey = keyblock[56:72]
                self.rc4client = RC4(self.clientkey)
                self.rc4server = RC4(self.serverkey)
            elif handshaketype==20:
                ref_md5 = data[4:20]
                ref_sha1 = data[20:40]
                md5_hash = md5(self.master + b'\\'*48 + md5(bytes(self.hchkall) + b'CLNT' + self.master + b'6'*48).digest()).digest()
                sha1_hash = sha1(self.master + b'\\'*40 + sha1(bytes(self.hchkall) + b'CLNT' + self.master + b'6'*40).digest()).digest()
                if ref_md5!=md5_hash or ref_sha1!=sha1_hash:
                    return False
                self.sendmessage(b'\x01', 0x14)
                self.sendseq = 0
                self.sciphering = True
                self.sendfinished(orgdata)
            else:
                print("Cannot resolve handshaketype", handshaketype, data[4:])
                return False
            self.hchkall += orgdata
            self.hchkall += self.hchksent
        elif msgtype==0x17:
            self.underlying.send(data)
            full = bytearray()
            b = self.underlying.recv(1024)
            full += b
            while len(b)>0:
                b = self.underlying.recv(1024)
                full += b
            self.sendmessage(bytes(full), 0x17)
            return False
        else:
            print("Unk Specs", msgtype, data)
            return False
        return True
    "One instance per connection.  Override handle(self) to customize action."
    def handle(self):
        self.underlying = None
        try:
            self.hchkall = bytearray()
            self.sciphering = False
            self.cciphering = False
            self.recvseq = 0
            self.sendseq = 0
            # self.request is the client connection
            while self.parsemessage():
                pass
        except Exception as e:
            print(e)
        if self.underlying is not None:
            self.underlying.close()

shttpserv = TCPServer((SERVER_ADDR, 443), CustomHandler)
shttpserv.timeout = 5

print("Starting HTTPS server...")
shttpserv.serve_forever()
