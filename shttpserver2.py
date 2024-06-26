from handlers.httphandler import *
from http.server import HTTPServer
import ssl

shttpserv = HTTPServer((SERVER_ADDR, 8686), CustomHandler)

shttpserv.socket = ssl.wrap_socket(shttpserv.socket, keyfile='cert/other/key.pem', certfile='cert/other/cert.pem', server_side=True)

print("Starting HTTPS2 server...")
shttpserv.serve_forever()
