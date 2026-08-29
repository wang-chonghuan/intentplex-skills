"""Receives harvested JSON from the page via the window.name bridge.

Three routes out of the page were tried and failed against a live LinkedIn tab:
clipboard writeText (hangs, 45s CDP timeout on a 245KB payload),
execCommand('copy') (returns false even with document focus), and a no-cors
POST to 127.0.0.1 (blocked as mixed content from an https origin).

window.name survives cross-origin navigation. The page stashes the payload
there, the tab navigates here, and this page POSTs it back same-origin.
"""
import http.server, socketserver, sys, pathlib

OUT = pathlib.Path(sys.argv[1])
PORT = int(sys.argv[2])

PAGE = b"""<!doctype html><meta charset=utf-8><title>collect</title>
<body><pre id=o>reading window.name...</pre><script>
(async () => {
  const o = document.getElementById('o');
  const payload = window.name || '';
  if (!payload) { o.textContent = 'EMPTY window.name'; return; }
  const r = await fetch('/save/' + (location.hash.slice(1) || 'payload'),
                        {method:'POST', headers:{'Content-Type':'text/plain'}, body:payload});
  o.textContent = 'POSTED ' + payload.length + ' chars -> ' + r.status;
  window.name = '';
})();
</script></body>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n)
        name = self.path.rsplit('/', 1)[-1] or 'payload'
        target = OUT / f'{name}.json'
        target.write_bytes(body)
        print(f'wrote {target} ({len(body)} bytes)', flush=True)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('127.0.0.1', PORT), H) as srv:
    print(f'receiver on {PORT} -> {OUT}', flush=True)
    srv.serve_forever()
