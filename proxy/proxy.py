import SocketServer
import SimpleHTTPServer
import urllib2

PORT = 12345

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print "hey i here ok"
        self.copyfile(urllib2.urlopen(self.path), self.wfile)


httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print "serving at port", PORT
httpd.serve_forever()
