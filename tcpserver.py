from handlers.tcphandler import *

tcpserv = TCPServer((SERVER_ADDR, 29900), CustomHandler)

print("Starting TCP server...")
tcpserv.serve_forever()
