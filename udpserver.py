from socketserver import DatagramRequestHandler, UDPServer, ThreadingMixIn
from random import randrange, choice
from base64 import b64decode, b64encode
from hashlib import md5
from binascii import hexlify

from structure.database import *

class CustomHandler(DatagramRequestHandler):
    def handle(self):
        rq = self.rfile.read()
        mtype = rq[0]
        cid = int.from_bytes(rq[1:5], 'big')
        info = rq[5:].split(b'\x00')
        struct_info = dict()
        for i in range(0, len(info)-1, 2):
            struct_info[info[i].decode("ascii")] = info[i+1].decode("ascii")
        if mtype==9:
            self.wfile.write(b'\xfe\xfd\x09')
            self.wfile.write(cid.to_bytes(4, 'big'))
        elif mtype==8:
            self.wfile.write(b'\xfe\xfd\x08')
            self.wfile.write(cid.to_bytes(4, 'big'))
        elif mtype==3:
            self.wfile.write(b'\xfe\xfd\x01')
            self.wfile.write(cid.to_bytes(4, 'big'))
            self.wfile.write(''.join([choice(TOKENPOOL) for i in range(6)]).encode("ascii"))
            self.wfile.write(b'00')
            localip = hexlify(bytes([int(x) for x in struct_info["localip0"].split(".")]))
            localport = hexlify(int(struct_info["localport"]).to_bytes(2,'big'))
            self.wfile.write(localip)
            self.wfile.write(localport)
            self.wfile.write(bytes(1))
        elif mtype==1:
            self.wfile.write(b'\xfe\xfd\x0a')
            self.wfile.write(cid.to_bytes(4, 'big'))
            self.wfile.write(bytes(11))

class ThreadedUDPServer(ThreadingMixIn, UDPServer):
    pass

udpserv = ThreadedUDPServer((SERVER_ADDR, 27900), CustomHandler)
udpserv.timeout = 5

print("Starting UDP server...")
udpserv.serve_forever()
