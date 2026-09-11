import os
import logging
from flask import Flask, jsonify, send_from_directory

FLAG = os.environ.get("FLAG", "flag{phantom_stego_recovered_missing}")

app = Flask(__name__, static_folder="static")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("phantom-forensic")


@app.route("/api/health")
def health():
    return jsonify({"status": "UP", "service": "Memory-Core-Relay"})


@app.route("/transmission.png")
def transmission():
    log.info("TRANSMISSION IMAGE DOWNLOADED (contains LSB payload)")
    return send_from_directory(app.static_folder, "transmission.png")


@app.route("/api/verify/<candidate>")
def verify(candidate):
    match = candidate.strip() == FLAG
    if match:
        log.info("FLAG VERIFY ATTEMPT match=True flag=%s", FLAG)
    else:
        log.info("FLAG VERIFY ATTEMPT match=False")
    return jsonify({"match": match})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
