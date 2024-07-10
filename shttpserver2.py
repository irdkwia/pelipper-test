from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from handlers.httphandler import *
import ssl

class ThreadedHTTPSServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread for HTTPS."""

shttpserv = ThreadedHTTPSServer((SERVER_ADDR, 8686), CustomHandler)
shttpserv.timeout = 5

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='cert/other/cert.pem', keyfile='cert/other/key.pem')

shttpserv.socket = context.wrap_socket(shttpserv.socket, server_side=True)

print("Starting HTTPS2 server...")
shttpserv.serve_forever()
