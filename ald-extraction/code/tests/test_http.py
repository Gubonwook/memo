import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from ald_extract.config import Endpoint
from ald_extract.llm import OpenAICompatLLM, image_message

SEEN = {}


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.update(path=self.path, auth=self.headers.get("Authorization"), body=body)
        out = json.dumps({"choices": [{"message": {"content": '{"ok": true}'}}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)

    def log_message(self, *a):
        pass


def test_openai_compat_roundtrip():
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    llm = OpenAICompatLLM(Endpoint(f"http://127.0.0.1:{srv.server_port}/v1", "m", "KEY"))
    assert llm.chat([{"role": "user", "content": "hi"}], json_mode=True) == '{"ok": true}'
    assert SEEN["path"] == "/v1/chat/completions" and SEEN["auth"] == "Bearer KEY"
    assert SEEN["body"]["response_format"] == {"type": "json_object"}
    llm.chat(image_message("p", b"\x89PNG"))
    assert SEEN["body"]["messages"][0]["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")
    srv.shutdown()
