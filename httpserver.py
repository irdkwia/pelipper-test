from handlers.httphandler import *
from http.server import HTTPServer

httpserv = HTTPServer((SERVER_ADDR, 80), CustomHandler)
httpserv.timeout = 5

print("Starting HTTP server...")
httpserv.serve_forever()
