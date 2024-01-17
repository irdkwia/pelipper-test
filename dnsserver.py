from socketserver import DatagramRequestHandler, UDPServer

from structure.database import *

class CustomHandler(DatagramRequestHandler):
    def handle(self):
        rq = bytearray(self.rfile.read())
        off = 13
        toresolve = bytearray()
        while rq[off]!=0:
            toresolve += bytes([rq[off]])
            off += 1
        toresolve = bytes([x if x>0x20 else 0x2E for x in toresolve]).decode("ascii")
        #print("Resolve:",toresolve)
        rq[2:4] = b'\x85\x80'
        rq[6:8] = b'\x00\x01'
        rip = bytes([int(x) for x in RESOLVER.get(toresolve, '8.8.8.8').split(".")])
        self.wfile.write(bytes(rq)+b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x20\x00\x04'+rip)
        
            
dnsserv = UDPServer((SERVER_ADDR, 53), CustomHandler)

print("Starting DNS server...")
dnsserv.serve_forever()
