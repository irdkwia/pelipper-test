# WARNING!!! This is only available up to Python 3.3.5
# You need python 3.3.5 to run an HTTPS with low encryption settings
# If you can't downgrade to 3.3.5, use shttpserver2.py instead
# which provides minimal support to run a WFC server with
# now prohibited encryption settings

import ssl
from http.server import HTTPServer

from handlers.httphandler import *

context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
context.set_ciphers("RC4-SHA")
context.load_cert_chain(certfile="./cert/server.chain.crt", keyfile="./cert/server.key")
shttpserv = HTTPServer((SERVER_ADDR, 443), CustomHandler)

shttpserv.socket = context.wrap_socket(shttpserv.socket, server_side=True)

print("Starting HTTPS server...")
shttpserv.serve_forever()
