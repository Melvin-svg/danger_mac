import os
import sqlite3
import logging
from flask import Flask, request, jsonify

FLAG = os.environ.get("FLAG", "flag{phantom_sqli_bypass_missing}")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("phantom-web")

DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE users (username TEXT, password TEXT, is_admin INTEGER)")
DB.execute("INSERT INTO users VALUES ('admin', 'S3cretHackathonPass!', 1)")
DB.execute("INSERT INTO users VALUES ('guest', 'guest', 0)")
DB.commit()


@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HEY CHELLOM // Web Challenge Target</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes pulseGlow {
            0%, 100% { filter: drop-shadow(0 0 25px rgba(245, 158, 11, 0.6)); }
            50% { filter: drop-shadow(0 0 50px rgba(239, 68, 68, 0.9)); }
        }
        .meme-glow { animation: pulseGlow 3s ease-in-out infinite; }
    </style>
</head>
<body class="min-h-screen w-screen bg-slate-950 text-slate-100 flex flex-col justify-between items-center p-4 font-mono">
    <div class="text-center my-2">
        <h1 class="text-xl font-black text-amber-400">🔥 HEY CHELLOM! 🎯 SQL INJECTION TARGET WEB UI</h1>
        <p class="text-xs text-slate-400">Send POST request to <code class="text-cyan-400">/api/v1/authenticate</code></p>
    </div>
    <div class="flex-1 flex items-center justify-center">
        <div class="meme-glow p-2 bg-black/90 border-4 border-amber-400 rounded-3xl shadow-2xl">
            <img src="http://localhost:8000/assets/chellom_meme.png" alt="Hey Chellom Meme" class="max-h-[75vh] w-auto object-contain rounded-2xl" />
        </div>
    </div>
    <div class="text-xs text-slate-400 my-2">Operation Phantom Forge // AVST-Lite</div>
</body>
</html>"""


@app.route("/api/health")
def health():
    return jsonify({"status": "UP", "cve": "CVE-2024-SQLI", "service": "SQLite-Auth-Portal"})


@app.route("/api/v1/authenticate", methods=["POST"])
def authenticate():
    body = request.get_json(force=True, silent=True) or {}
    username = body.get("username", "")
    password = body.get("password", "")

    # Intentionally vulnerable: raw string interpolation (CTF target).
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    log.info("AUTH QUERY: %s", query)

    try:
        cur = DB.execute(query)
        row = cur.fetchone()
    except sqlite3.Error as exc:
        log.info("SQL ERROR (possible injection probe): %s", exc)
        return jsonify({"authenticated": False, "error": "query failed"}), 400

    if row and row[2] == 1:
        log.info("ADMIN BYPASS DETECTED -> issuing flag %s", FLAG)
        return jsonify({"authenticated": True, "role": "admin", "flag": FLAG})
    if row:
        return jsonify({"authenticated": True, "role": "user"})
    return jsonify({"authenticated": False}), 401


@app.route("/api/verify/<candidate>")
def verify(candidate):
    match = candidate.strip() == FLAG
    if match:
        log.info("FLAG VERIFY ATTEMPT match=True flag=%s", FLAG)
    else:
        log.info("FLAG VERIFY ATTEMPT match=False")
    return jsonify({"match": match})


@app.route("/api/admin/dump")
def admin_dump():
    auth = request.headers.get("Authorization", "")
    if "admin" in auth.lower():
        log.info("ADMIN DUMP ACCESSED -> issuing flag %s", FLAG)
        return jsonify({"flag": FLAG, "note": "server log will record this access"})
    return jsonify({"error": "forbidden"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
