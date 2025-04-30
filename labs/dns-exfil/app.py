from flask import Flask, render_template, request
import subprocess
import os
import re

app = Flask(__name__)

blacklisted = [";", "|", "&", "$", "`", ">", "<", "(", ")", "{", "}", "[", "]"]
authorized_ports = list(range(49335, 49355))
ptr = 0

@app.route("/", methods=["GET"])
def main():
    return render_template("check.html", up=None, error=False)

@app.route("/check-status", methods=["POST"])
def check_status():
    global ptr
    site = request.form.get("site")
    pattern = r"^[a-zA-Z0-9\-.]+\.[a-zA-Z]{2,}$"

    match = re.match(pattern, site)
    if match:
        port = authorized_ports[ptr]
        ptr = (ptr + 1) % len(authorized_ports)

        try:
            result = subprocess.run([
                "curl", "--head", "--local-port", str(port),
                "--connect-timeout", "5", site
            ], capture_output=True, text=True).stdout

            is_up = bool(result.strip())
            return render_template("check.html", up=is_up, error=False)

        except Exception as e:
            print("Error checking status:", e)
            return render_template("check.html", up=None, error=True)

    else:
        os.system(f"echo {site}")  # log
        return render_template("check.html", up=None, error=True)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
