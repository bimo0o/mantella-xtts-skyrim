"""
uploader.py - tiny stdlib sidecar so Mantella can push a per-Sim custom voice
.wav to a running XTTS instance at runtime (the xtts-api-server has no upload
endpoint; it only reads speaker .wav files from a folder).

Listens on PORT (default 8021). POST /upload?name=<voice> with the raw wav bytes
as the body -> writes <SPEAKERS_DIR>/<voice>.wav. Then synth with
speaker_wav="<voice>.wav" uses that cloned voice. GET /health -> ok.

Pure stdlib (no pip) so it can never break the image build or boot.
"""
import os, re, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("UPLOADER_PORT", "8021"))
SPEAKERS_DIR = os.environ.get("SPEAKERS_DIR", "/app/speakers")
MAX_BYTES = 25 * 1024 * 1024  # 25 MB ceiling per sample

_SAFE = re.compile(r"[^a-zA-Z0-9_-]")


def _safe_name(n):
    n = _SAFE.sub("", (n or "").strip())[:64]
    return n


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/health"):
            return self._json(200, {"ok": True, "dir": SPEAKERS_DIR})
        if self.path.startswith("/list"):
            try:
                files = [f for f in os.listdir(SPEAKERS_DIR) if f.lower().endswith(".wav")]
            except Exception:
                files = []
            return self._json(200, {"voices": files})
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/upload"):
            return self._json(404, {"error": "not found"})
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query)
        name = _safe_name((q.get("name") or [""])[0])
        if not name:
            return self._json(400, {"error": "missing/invalid name"})
        try:
            n = int(self.headers.get("Content-Length", 0))
        except Exception:
            n = 0
        if n <= 0 or n > MAX_BYTES:
            return self._json(400, {"error": "bad content-length"})
        data = self.rfile.read(n)
        try:
            os.makedirs(SPEAKERS_DIR, exist_ok=True)
            with open(os.path.join(SPEAKERS_DIR, name + ".wav"), "wb") as f:
                f.write(data)
        except Exception as e:
            return self._json(500, {"error": str(e)[:160]})
        return self._json(200, {"ok": True, "voice": name + ".wav", "bytes": len(data)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.makedirs(SPEAKERS_DIR, exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
