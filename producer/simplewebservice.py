import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleWebService():
    def __init__(self,address, port, queue):
        self.httpd = HTTPServer((address, port), makeHandlerWithQueue(queue))

    def run(self):
        self.httpd.serve_forever()

def makeHandlerWithQueue(queue):
    class Server(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.queue = queue
            super(Server, self).__init__(*args, **kwargs)

        def do_GET(self):
            product = self.queue.get()
            if product:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(product, default=json_serial).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
    return Server

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))