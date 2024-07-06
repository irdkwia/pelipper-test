from handlers.httphandler import *
from http.server import HTTPServer
import ssl

shttpserv = HTTPServer((SERVER_ADDR, 8686), CustomHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='cert/other/cert.pem', keyfile='cert/other/key.pem')

shttpserv.socket = context.wrap_socket(shttpserv.socket, server_side=True)

print("Starting HTTPS2 server...")
shttpserv.serve_forever()
