# Inspired by https://pythonbasics.org/webserver/
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from socketserver import ThreadingMixIn
import threading


HOST_NAME = "localhost"
PORT = 8080


class RequestPath:
    def __init__(self, path, args=[]):
        self.path = path
        self.args = args


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        req = parse_path(self.path)
        print("Processing:", req.path, req.args, threading.currentThread().getName())

        t0 = datetime.now()

        if req.path == "/secs/":
            reqs = process_req(req)
            for req in reqs:
                req.join()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        write(self, f"Elapsed: {get_elapsed(t0)}s\n")


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """
    Taken from https://stackoverflow.com/a/51559006
    """
    pass


def parse_path(path):
    parts = path.split("/")
    if "/secs/" in path:
        return RequestPath("/secs/", parts[-1])
    return RequestPath(path)


def process_req(req, results=[]):
    secs_list = req.args.split(",")
    return [
        launch_request_thread(f"http://httpbin.org/delay/{secs}", results)
        for secs in secs_list
    ]


def perform_request(url, results=[]):
    res = requests.get(url)
    results.append(json.loads(res.text))
    return res


def launch_request_thread(url, results=[]):
    thread = threading.Thread(target=perform_request, args=(url, results))
    thread.start()
    return thread


def get_elapsed(t0):
    return (datetime.now() - t0).total_seconds()


def write(res, text):
    res.wfile.write(bytes(text, "utf-8"))


if __name__ == "__main__":
    webServer = ThreadingSimpleServer((HOST_NAME, PORT), MyServer)
    print("Server started http://%s:%s" % (HOST_NAME, PORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
