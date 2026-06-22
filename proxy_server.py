"""
Proxy server untuk development.
Serve static files dari frontend-dashboard/ dan proxy /api/* ke backend :5000.
"""

import http.server
import urllib.request
import os
import mimetypes

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend-dashboard")
BACKEND_URL = "http://localhost:5000"
PORT = 3000

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/") or self.path.startswith("/api/audio/"):
            self.proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/") or self.path.startswith("/api/audio/"):
            self.proxy_request("POST")
        else:
            self.send_error(405)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self.proxy_request("PUT")
        else:
            self.send_error(405)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self.proxy_request("DELETE")
        else:
            self.send_error(405)

    def proxy_request(self, method):
        url = f"{BACKEND_URL}{self.path}"
        body = None
        headers = {}
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))
        for key in self.headers:
            if key.lower() not in ("host", "connection"):
                headers[key] = self.headers[key]
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            res = urllib.request.urlopen(req, timeout=30)
            self.send_response(res.status)
            for key, val in res.headers.items():
                if key.lower() not in ("transfer-encoding", "content-encoding", "connection"):
                    self.send_header(key, val)
            self.end_headers()
            chunk = res.read(65536)
            while chunk:
                self.wfile.write(chunk)
                chunk = res.read(65536)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, val in e.headers.items():
                if key.lower() not in ("transfer-encoding", "content-encoding", "connection"):
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    print(f"[PROXY] Serve frontend : http://localhost:{PORT}")
    print(f"[PROXY] Proxy /api/* -> {BACKEND_URL}")
    print(f"[PROXY] Ctrl+C untuk berhenti")
    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
