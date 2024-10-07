from http.server import HTTPServer
from socketserver import ThreadingMixIn

from handlers.httphandler import *


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


httpserv = ThreadedHTTPServer((SERVER_ADDR, 80), CustomHandler)
httpserv.timeout = 5

print("Starting HTTP server...")
httpserv.serve_forever()
