from handlers.tcphandler import *
from socketserver import ThreadingMixIn

def idle(obj):
    return

CustomHandler.requestchallenge = idle

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

tcpserv = ThreadedTCPServer((SERVER_ADDR, 29901), CustomHandler)
tcpserv.timeout = 5

print("Starting TCP2 server...")
tcpserv.serve_forever()
