from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from http.client import RemoteDisconnected
import ssl
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

import certifi


DOWNLOADS = {}
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class BatchCallerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/download-csv":
            query = parse_qs(parsed_url.query)
            download_id = query.get("id", [""])[0]
            csv_text = DOWNLOADS.get(download_id)
            if csv_text is None:
                self.send_error(404, "CSV download not found")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="results.csv"')
            self.send_header("Content-Length", str(len(csv_text)))
            self.end_headers()
            self.wfile.write(csv_text)
            return

        super().do_GET()

    def do_POST(self):
        if self.path == "/save-csv":
            content_length = int(self.headers.get("Content-Length", "0"))
            csv_text = self.rfile.read(content_length)
            download_id = uuid4().hex
            DOWNLOADS[download_id] = csv_text
            response_body = f'{{"id":"{download_id}"}}'.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            return

        if self.path != "/proxy-chat-completions":
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        api_url = self.headers.get("X-API-URL", "").strip()
        if not api_url:
            self.send_error(400, "Missing API URL")
            return

        headers = {"Content-Type": "application/json"}
        authorization = self.headers.get("Authorization", "").strip()
        if authorization:
            headers["Authorization"] = authorization

        request = Request(
            api_url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=300, context=SSL_CONTEXT) as response:
                response_body = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(response_body)))
                self.end_headers()
                self.wfile.write(response_body)
        except HTTPError as error:
            error_body = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
        except URLError as error:
            message = f'{{"error":"Could not reach API endpoint: {error.reason}"}}'.encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)
        except RemoteDisconnected:
            message = b'{"error":"API endpoint closed the connection before returning a response."}'
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), BatchCallerHandler)
    print("Open http://127.0.0.1:8000/index.html")
    server.serve_forever()
