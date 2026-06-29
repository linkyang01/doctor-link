from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "app.yml"


def load_config() -> dict[str, str]:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    config: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()
    return config


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        if self.path == "/users":
            config = load_config()
            # Bug: expects users_endpoint but config only defines api_base.
            endpoint = config["users_endpoint"]
            self._json(500, {"error": "missing endpoint", "endpoint": endpoint})
            return
        self._json(404, {"error": "not found"})

    def log_message(self, format: str, *args) -> None:
        return

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 18080) -> None:
    server = HTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run()