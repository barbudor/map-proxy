"""
MAP-PROXY   Barbudor
-------------------------------------
Simple proxy server to convert map tile request from standard OSM-style to different format
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import requests
import argparse
from sys import exit

#########################################################

__version__ = "0.1.0"

#########################################################
# Command line arguments

parser = argparse.ArgumentParser()

parser.add_argument('-p', '--port', required=False, type=int, default=8888, help='Port for map-proxy web server. Defaults to 8888')
parser.add_argument('-c', '--cfg', required=False, default="map-proxy.json", help="JSON configuration file. Default to 'map-proxy.json'" )

args, unknown = parser.parse_known_args()

maps = None

#########################################################
# HTTP request handler class

class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def handle_map_request(self, map, items):

        if map.get('variables', None) != None:
            items.update(map['variables'])
        if map.get('serverpart', None) != None:
            x = int(items['x'])
            server = x % len(map['serverpart'])
            items['serverpart'] = map['serverpart'][server];

        # print(repr(items))
        url = map['url'].format(**items)
        # print("url=",url)

        r = requests.get(url, headers=map['headers'])

        # print("status_code=", r.status_code)
        # print("headers=", repr(r.headers))

        if r.status_code == 200:
            self.send_response(200)
            for key,val in r.headers.items():
                self.send_header(key,val)
            self.end_headers()
            self.wfile.write(r.content)
        else:
            print("ERR %d url:\"%s\""%(r.status_code, url))
            self.send_response(r.status_code)
            self.end_headers()


    def do_GET(self):

        try:
            (temp,filetype) = self.path.split('.')
            (dummy,path,zoom,x,y) = temp.split('/')
        except ValueError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad request !')
            return

        items = { 'path':path, 'zoom':zoom, 'x':x, 'y':y, 'filetype':filetype }
        # print(items)
        # print("path={path}, zoom={zoom}, x={x}, y={y}, type={filetype}".format(**items))

        for map in maps:
            if map['path'] == path:
                self.handle_map_request(map, items)
                return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not found !')


def main():
    global maps
    # read configuration file
    try:
        with open(args.cfg, "r") as fp:
            maps = json.load(fp)
    except FileNotFoundError:
        print("File %s not found - aborting"%args.cfg)
        exit(1)

    print("map-proxy (v%s) started with configuration file %s on port %d"%(__version__, args.cfg, args.port))

    # launch web server
    httpd = ThreadingHTTPServer(('localhost', args.port), MyHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
