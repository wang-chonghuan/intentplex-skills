"""Local HTTP fixtures with the real CloakBrowser; no public sites or database writes."""

import argparse
import importlib.util
import io
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

os.environ["CLOAKBROWSER_AUTO_UPDATE"] = "false"

spec = importlib.util.spec_from_file_location("cloak_fetch", Path(__file__).with_name("cloak_fetch.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

requests = []


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        requests.append(self.path)
        if self.path == "/redirect" or (self.path == "/challenge" and requests.count("/challenge") > 1):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/destination")
            self.end_headers()
        elif self.path == "/challenge":
            self.send_response(403)
            self.send_header("Content-Type", "text/html")
            self.send_header("cf-mitigated", "challenge")
            self.end_headers()
            self.wfile.write(b"<html><body><script>setTimeout(() => location.reload(), 150)</script></body></html>")
        elif self.path == "/limited":
            self.send_response(429)
            self.send_header("Retry-After", "60")
            self.send_header("Set-Cookie", "private=do-not-output")
            self.end_headers()
            self.wfile.write(b"<html><body>Wait</body></html>")
        elif self.path == "/blocked":
            self.send_response(403)
            self.send_header("cf-mitigated", "challenge")
            self.end_headers()
            self.wfile.write(b"<html><body>Blocked</body></html>")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body>Destination</body></html>")

    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
context = None
try:
    context = module.launch_context(headless=True)
    base = f"http://127.0.0.1:{server.server_port}"
    for path in ("/redirect", "/challenge", "/limited", "/blocked"):
        page = context.new_page()
        try:
            args = argparse.Namespace(url=base + path, timeout=5, wait=2 if path == "/challenge" else 0.2)
            result = module.read_redirect(page, args)
            assert result["url"] == base + path, result
            if path in ("/redirect", "/challenge"):
                assert result["status"] == 302, result
                assert result["headers"]["location"] == base + "/destination", result
            elif path == "/limited":
                assert result["status"] == 429, result
                assert result["headers"] == {"retry-after": "60"}, result
            else:
                assert result["status"] == 403, result
                assert result["headers"] == {"cf-mitigated": "challenge"}, result
        finally:
            page.close()
    assert "/destination" not in requests, requests
    source = io.StringIO("".join(json.dumps({"url": base + path}) + "\n"
                               for path in ("/redirect", "/redirect", "/limited")))
    output = io.StringIO()
    assert module.serve_redirects(context, argparse.Namespace(timeout=5, wait=0.2), source, output) == 0
    messages = [json.loads(line) for line in output.getvalue().splitlines()]
    assert messages[0] == {"event": "ready", "protocol": 1}, messages
    assert [message["status"] for message in messages[1:]] == [302, 302, 429], messages
    assert context.pages == [], context.pages
    assert "/destination" not in requests, requests
    invalid = io.StringIO()
    assert module.serve_redirects(context, argparse.Namespace(timeout=5, wait=0.2),
                                 io.StringIO('{"not-url":true}\n'), invalid) == 1
    assert json.loads(invalid.getvalue().splitlines()[-1]) == {"event": "error", "reason": "invalid-request"}
    print(json.dumps({"event": "cloak-fetch-check.done", "cases": 8, "browserStarts": 1,
                      "destinationRequests": 0, "sessionPagesClosed": True}))
finally:
    if context:
        context.close()
    server.shutdown()
    server.server_close()
