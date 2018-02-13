import SocketServer
import SimpleHTTPServer
import urllib2
import pickle

PORT = 12345

STORAGE = {}

def cache(n, k):
    STORAGE["1"] = n
    STORAGE["2"] = k

def returncache():
    return STORAGE["2"]

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "http://localhost:20000/2.txt":
            a = returncache()
            self.copyfile(self.path, a)

        else:
            n = self.path
            k = urllib2.urlopen(self.path)
            self.copyfile(n, k)
            cache(n, k)

    def __init__(self, *args, **kwargs):

        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)




httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print "serving at port", PORT
httpd.serve_forever()
