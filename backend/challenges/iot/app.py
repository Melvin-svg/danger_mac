import os
import logging
from flask import Flask, request, jsonify

FLAG = os.environ.get("FLAG", "flag{pump_override_detected_missing}")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("phantom-iot")

pump_state = {"override": False}


@app.route("/api/health")
def health():
    return jsonify({"status": "UP", "device": "ESP32-Irrigation-Controller", "broker": "mosquitto-sim"})


@app.route("/scada/pumps/override", methods=["POST"])
def publish_override():
    body = request.get_json(force=True, silent=True) or {}
    override = bool(body.get("override", False))
    pump_state["override"] = override
    log.info("MQTT PUBLISH scada/pumps/override -> %s", body)

    if override:
        log.info("SAFETY MEMORY DUMP TRIGGERED -> issuing flag %s", FLAG)
        return jsonify({"status": "override_accepted", "safety_dump": {"flag": FLAG}})
    return jsonify({"status": "override_cleared"})


@app.route("/api/verify/<candidate>")
def verify(candidate):
    match = candidate.strip() == FLAG
    if match:
        log.info("FLAG VERIFY ATTEMPT match=True flag=%s", FLAG)
    else:
        log.info("FLAG VERIFY ATTEMPT match=False")
    return jsonify({"match": match})


@app.route("/scada/pumps/telemetry")
def telemetry():
    return jsonify({"pump_running": True, "override": pump_state["override"], "flow_rate_lpm": 42.7})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
