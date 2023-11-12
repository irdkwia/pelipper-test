from handlers.tcphandler import *

def idle(obj):
    return

CustomHandler.requestchallenge = idle
tcpserv = TCPServer((SERVER_ADDR, 29901), CustomHandler)

print("Starting TCP2 server...")
tcpserv.serve_forever()
