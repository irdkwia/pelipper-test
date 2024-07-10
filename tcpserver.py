from handlers.tcphandler import *
from socketserver import ThreadingMixIn

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

tcpserv = ThreadedTCPServer((SERVER_ADDR, 29900), CustomHandler)
tcpserv.timeout = 5

print("Starting TCP server...")
tcpserv.serve_forever()
