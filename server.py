#!/usr/bin/env python3
"""
Local / Raspberry Pi web server for magda-schwerzmann.ch.
Serves the static site and provides POST /api/save for the /admin/ editor,
automatically rebuilding all static HTML pages when content is saved.
"""

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import build

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "content.json"


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path == "/api/save":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                parsed = json.loads(raw)
                DATA_FILE.write_text(
                    json.dumps(parsed, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                build.build_all()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"))
        else:
            self.send_error(404, "Not found")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    build.build_all()
    server = ThreadingHTTPServer(("127.0.0.1", port), SiteHandler)
    print(f"Serving magda-schwerzmann.ch at http://localhost:{port}/")
    print(f"Admin editor available at       http://localhost:{port}/admin/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
