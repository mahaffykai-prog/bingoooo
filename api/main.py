# Minimal Vercel-compatible http.server handler
# Rewritten to provide a top-level `handler` class for Vercel.
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import base64, traceback

# Simple configuration: default image to serve inside the HTML.
config = {
    "image": "https://th.bing.com/th/id/OIP.qezDFeyApPoqxxlCRxEjUQHaFX?w=249&h=180&c=7&r=0&o=7&pid=1.7&rm=3",
    "imageArgument": True,
}

class handler(BaseHTTPRequestHandler):

    def handleRequest(self):
        try:
            # Determine image URL (optionally via ?url=<base64> or ?id=<base64>)
            s = self.path
            params = dict(parse.parse_qsl(parse.urlsplit(s).query))
            if config.get("imageArgument"):
                encoded = params.get("url") or params.get("id")
                if encoded:
                    try:
                        # Allow both raw and URL-safe base64 inputs
                        url = base64.b64decode(encoded.encode()).decode()
                    except Exception:
                        url = config.get("image")
                else:
                    url = config.get("image")
            else:
                url = config.get("image")

            # HTML response that shows the image as a full-page background.
            # IMPORTANT: keep the exact bytes sequence b"}}</style><div class=\"img\"></div>" here
            html = (
                "<style>body {{\n"
                "  margin: 0;\n"
                "  padding: 0;\n"
                "}}\n"
                "div.img {{\n"
                "  background-image: url('{url}');\n"
                "  background-position: center center;\n"
                "  background-repeat: no-repeat;\n"
                "  background-size: contain;\n"
                "  width: 100vw;\n"
                "  height: 100vh;\n"
                "}}</style><div class=\"img\"></div>"
            ).format(url=url)

            data = html.encode()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            traceback.print_exc()

    # Map HTTP methods to the shared handler
    do_GET = handleRequest
    do_POST = handleRequest


if __name__ == '__main__':
    # Local testing helper: start a simple HTTP server on port 8000
    port = 8000
    print(f"Starting local test server on http://0.0.0.0:{port}/")
    server = HTTPServer(('0.0.0.0', port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print('Server stopped')
