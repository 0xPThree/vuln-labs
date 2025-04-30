from flask import (
    Flask, request, render_template, redirect,
    make_response, jsonify
)
import requests
import hashlib
import socket
import urllib.parse
import time
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    if request.cookies.get("uuid_hash") is None:
        return redirect("/login", code=302)
    return render_template("dashboard.html"), 200


@app.route("/api/v3/login", methods=["POST"])
def check_creds():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "user1" and password == "Passw0rd!":
        res = make_response(redirect("/", code=302))
        res.set_cookie(
            "uuid_hash",
            hashlib.sha512(b"5d59daf3-f7cb-4a79-8c69-ec657aebb89a").hexdigest()
        )
        return res
    return "If you use your eyes you'll probably find the creds..", 401


@app.route("/login", methods=["GET"])
def login():
    user_uuid_hash = request.cookies.get("uuid_hash")
    expected_hash = hashlib.sha512(b"5d59daf3-f7cb-4a79-8c69-ec657aebb89a").hexdigest()

    if user_uuid_hash is not None:
        if user_uuid_hash == expected_hash:
            return redirect("/dashboard", code=302)
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    user_uuid_hash = request.cookies.get('uuid_hash')
    expected_hash = hashlib.sha512(b"5d59daf3-f7cb-4a79-8c69-ec657aebb89a").hexdigest()

    if user_uuid_hash is None or user_uuid_hash != expected_hash:
        return redirect("/login", code=302)
    return render_template('dashboard.html')

@app.route("/logout", methods=["GET"])
def logout():
    res = make_response(redirect("/login", code=302))
    res.delete_cookie("uuid_hash")
    return res


@app.route("/api/v3/users", methods=["POST"])
def get_user_files():
    try:
        user_uuid = request.get_json().get("user_uuid")
        if user_uuid == "5d59daf3-f7cb-4a79-8c69-ec657aebb89a":
            files = os.listdir(f"users/{user_uuid}/")
            return jsonify(files)
        return "invalid uuid", 401
    except Exception:
        return "invalid uuid", 401


@app.route("/api/v3/upload", methods=["POST"])
def upload_files_via_url_v3():
    uuid_hash = request.cookies.get("uuid_hash")
    if uuid_hash is None:
        return redirect("/login", code=302)

    file_url = request.form.get("file_url")
    try:
        file_domain = file_url.split("/")[2].split(":")[0]
        request_ip = socket.gethostbyname(file_domain)

        if request_ip.startswith(("127", "0", "192")):
            return "invalid url\n", 403

        file_name = file_url.split("/")[-1]
        file_contents = requests.get(file_url).text
        with open(
            f"users/5d59daf3-f7cb-4a79-8c69-ec657aebb89a/{file_name}", "w"
        ) as fd:
            fd.write(file_contents)
        return file_contents
    except Exception:
        return "invalid url\n", 403


@app.route("/api/v2/upload", methods=["POST"])
def upload_files_via_url_v2():
    uuid_hash = request.cookies.get("uuid_hash")
    if uuid_hash is None:
        return redirect("/login", code=302)

    content_type = request.headers.get("Content-Type")

    if content_type == "application/x-www-form-urlencoded":
        try:
            file_url = request.form.get("file_url")
            file_domain = file_url.split("/")[2].split(":")[0]
            request_ip = socket.gethostbyname(file_domain)

            if request_ip.startswith(("127", "0", "192")):
                return "invalid url\n", 403

            file_name = file_url.split("/")[-1]
            file_contents = requests.get(file_url).text
            with open(
                f"users/5d59daf3-f7cb-4a79-8c69-ec657aebb89a/{file_name}", "w"
            ) as fd:
                fd.write(file_contents)
            return file_contents
        except Exception:
            return "invalid url\n", 403
    else:
        try:
            file_url = urllib.parse.unquote(request.get_json()["file_url"])
            file_domain = file_url.split("/")[2].split(":")[0]
            request_ip = socket.gethostbyname(file_domain)

            if request_ip.startswith(("127", "0", "192")):
                return "requests to localhost not allowed\n", 403

            time.sleep(1)
            headers = {"X-Request-Ip": "127.0.0.1"}
            res = requests.get(file_url, headers=headers)
            return res.text, res.status_code
        except Exception:
            return "requests to localhost not allowed\n", 403


@app.route("/api", methods=["GET", "POST"])
def api_docs():
    request_src_ip = request.headers.get("X-Request-Ip")
    if request_src_ip != "127.0.0.1":
        return "Not Found", 404

    return """/users
/status
/employees
""", 200


@app.route("/api/users", methods=["GET", "POST"])
def get_users_uuids():
    request_src_ip = request.headers.get("X-Request-Ip")
    if request_src_ip != "127.0.0.1":
        return "Not Found", 404

    user_uuid = request.args.get("uuid")
    filename = request.args.get("file")

    if user_uuid:
        user_dir = f"users/{user_uuid}/"
        if filename:
            try:
                file_path = os.path.join(user_dir, filename)
                with open(file_path, "r") as f:
                    return f.read(), 200
            except FileNotFoundError:
                return "file not found", 404
            except Exception:
                return "error reading file", 500
        else:
            try:
                user_files = os.listdir(user_dir)
                return jsonify(user_files)
            except FileNotFoundError:
                return "invalid uuid", 401
    else:
        users = os.listdir("users/")
        return jsonify(users)


@app.route("/api/status", methods=["GET", "POST"])
def get_site_status():
    request_src_ip = request.headers.get("X-Request-Ip")
    if request_src_ip != "127.0.0.1":
        return "Not Found", 404
    return "site is up", 200


@app.route("/api/employees", methods=["GET", "POST"])
def get_employees():
    request_src_ip = request.headers.get("X-Request-Ip")
    if request_src_ip != "127.0.0.1":
        return "Not Found", 404
    return "we currently have 1337 active employees"


@app.errorhandler(404)
def page_not_found(e):
    return "resource not found", 404


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
