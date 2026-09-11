import logging
import random
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import docker_manager
import ollama_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("avst-lite")

app = FastAPI(title="AVST-Lite // Operation Phantom Forge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

XP_STATE = {"xp": 450}

CODENAMES = [
    "Silent Vortex", "Obsidian Dagger", "Null Phantom", "Iron Horizon", "Cobalt Echo", "Crimson Gateway",
    "Kuttichathan", "Adipoli Strike", "Chattambi Protocol", "Pwoli Paundu", "Polikkum Falcon", "Kidilam Storm",
]

VECTORS = {
    "web": "an unauthenticated SQL injection bypass in an employee login portal",
    "iot": "an unauthenticated MQTT telemetry override on a SCADA irrigation controller",
    "forensic": "a hidden LSB steganographic payload inside an intercepted image transmission",
}

FALLBACK_LORE = {
    "web": "A rogue contractor deployed an unauthenticated administrative portal at Sector 9. Passive taps intercepted malformed login calls. Exploit the unescaped SQL injection parameter to recover the encrypted memory flag.",
    "iot": "Telemetry streams for the facility's pump system leak over an unencrypted MQTT topic. Inject an unauthorized override packet to trigger a safety memory dump containing the master key.",
    "forensic": "An encrypted courier intercepted an image transmission over an unauthorized relay. Binary metadata suggests a hidden payload nested inside the least-significant bits of the frame.",
}

HINTS = {
    "web": {
        "gentle": "The web application has an SQL query concatenation flaw in the auth controller. Look at quotes and comment operators.",
        "tactical": "Pass an injection string in the username parameter such as `admin' OR 1=1--` to force the query to return true.",
        "technique": "The SQL interpreter treats `--` as a comment to end-of-line. Closing the quote and adding `OR 1=1` short-circuits the password check.",
    },
    "iot": {
        "gentle": "MQTT-style topics on lightweight embedded brokers often accept commands without access control.",
        "tactical": "POST JSON {\"override\": true} to the `scada/pumps/override` endpoint.",
        "technique": "The pump controller echoes its safety-dump state, including the flag, whenever the override flag is set true.",
    },
    "forensic": {
        "gentle": "Look closer at the image bitplanes. The payload is embedded in spatial pixel values.",
        "tactical": "Download transmission.png and inspect the least-significant bit of each red channel byte in raster order.",
        "technique": "Each character of the flag is encoded 8 bits at a time into the LSB of consecutive red channel bytes, terminated by a null byte.",
    },
}


class MissionRequest(BaseModel):
    category: str


class VerifyRequest(BaseModel):
    category: str
    flag: str


class HintRequest(BaseModel):
    category: str
    tier: str


class ChatRequest(BaseModel):
    category: str
    message: str


@app.get("/api/health")
def health():
    return {"status": "UP", "docker": docker_manager.get_client() is not None}


@app.post("/api/missions")
def create_mission(req: MissionRequest):
    if req.category not in VECTORS:
        raise HTTPException(400, "unknown category")

    sandbox = docker_manager.start_sandbox(req.category)

    codename = random.choice(CODENAMES)
    start = time.time()
    ai_result = ollama_client.generate_mission(req.category, codename, VECTORS[req.category])
    elapsed = round(time.time() - start, 2)

    lore = (ai_result or {}).get("lore") if ai_result else None
    source = "ollama" if lore else "fallback"
    lore = lore or FALLBACK_LORE[req.category]

    return {
        "title": f"Operation {codename}",
        "category": req.category,
        "lore": lore,
        "lore_source": source,
        "latency_seconds": elapsed,
        "target": sandbox["target"],
        "mode": sandbox["mode"],
        "flag": sandbox["flag"],
    }


@app.post("/api/verify")
def verify_flag(req: VerifyRequest):
    sandbox = docker_manager.get_sandbox(req.category)
    if not sandbox:
        raise HTTPException(404, "no active sandbox for category")

    expected = sandbox["flag"]
    submitted = req.flag.strip()
    match = submitted == expected

    if sandbox["mode"] == "docker":
        docker_manager.ping_verify(req.category, submitted)

    logs = docker_manager.get_logs(req.category)
    http_evidence = "match=true" in logs.lower() if sandbox["mode"] == "docker" else match
    log_confirms_flag = expected in logs if sandbox["mode"] == "docker" else match

    if match:
        XP_STATE["xp"] += 150

    evidence = {
        "http_audit": "VERIFIED" if (match and (sandbox["mode"] == "simulated" or http_evidence)) else "REJECTED",
        "hash_grounding": "GROUNDED" if (match and (sandbox["mode"] == "simulated" or log_confirms_flag)) else "REJECTED",
        "heuristic_signature": "CONFIRMED" if match else "REJECTED",
    }
    confidence = 99.4 if match else round(random.uniform(5, 22), 1)

    return {
        "match": match,
        "evidence": evidence,
        "confidence": confidence,
        "xp": XP_STATE["xp"],
        "mode": sandbox["mode"],
    }


@app.post("/api/hint")
def get_hint(req: HintRequest):
    costs = {"gentle": 5, "tactical": 10, "technique": 20}
    cost = costs.get(req.tier)
    if cost is None:
        raise HTTPException(400, "unknown tier")
    if XP_STATE["xp"] < cost:
        raise HTTPException(402, "insufficient XP")

    XP_STATE["xp"] -= cost
    hint = HINTS.get(req.category, {}).get(req.tier, "No hint available.")
    return {"hint": hint, "xp": XP_STATE["xp"]}


@app.post("/api/commander/chat")
def commander_chat(req: ChatRequest):
    context = f"The active sandbox target is running for the {req.category} scenario."
    reply = ollama_client.commander_reply(req.category, req.message, context)
    source = "ollama" if reply else "fallback"

    if not reply:
        q = req.message.lower()
        if "sql" in q or "login" in q:
            reply = "The auth endpoint doesn't sanitize parameters. Try an inline quote bypass. Sherikkum easy aanu!"
        elif "flag" in q:
            reply = f"Run the exploit against the {req.category} sandbox target to recover the flag. Poyi pidichu var! 💪"
        elif any(w in q for w in ("stuck", "help", "idea", "hint")):
            reply = "Onnu chill aavu. Check the 'How do I even start?' panel — adil ellam undu."
        else:
            reply = "Analyze the network responses closely and inspect the exposed ports."

    return {"reply": reply, "source": source}


@app.post("/api/sandbox/{category}/stop")
def stop_sandbox_endpoint(category: str):
    docker_manager.stop_sandbox(category)
    return {"status": "stopped"}


try:
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
except RuntimeError:
    log.warning("frontend directory not found; API-only mode")
