import json
import readline  # Enables arrow-key editing in input().
from http.server import BaseHTTPRequestHandler, HTTPServer


class MockLLMHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/chat/":
            self.send_json(404, {"error": "Use POST /chat/"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                raise ValueError("A JSON request body is required")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Request body must be an object")
            message = data.get("message")
            if not isinstance(message, str) or not message.strip():
                raise ValueError("message must be a non-empty string")
        except (ValueError, UnicodeDecodeError) as error:
            self.send_json(400, {"error": str(error)})
            return

        print(f"\nMessage: {message}", flush=True)
        try:
            reply = input("Your response (one line, then Enter): ")
        except EOFError:
            self.send_json(503, {"error": "Terminal input is unavailable"})
            return

        self.send_json(200, {"message": reply})


if __name__ == "__main__":
    with HTTPServer(("127.0.0.1", 8000), MockLLMHandler) as server:
        print("Mock LLM: http://127.0.0.1:8000/chat/", flush=True)
        print("Type replies here. Press Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping mock LLM.", flush=True)
