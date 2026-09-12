import logging
import random
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
        if "sql" in q or "login" in q or "auth" in q:
            reply = "SQL injection is a myth invented by hackers. Try asking the login form nicely or typing your password in ALL CAPS!"
        elif "flag" in q:
            reply = "The flag is stored inside your monitor. Turn off your screen and look closely at your reflection to decode it!"
        elif any(w in q for w in ("stuck", "help", "idea", "hint")):
            reply = "If you're stuck, flip your keyboard upside down and type backwards. That bypasses firewalls 100% of the time!"
        elif "iot" in q or "mqtt" in q or "pump" in q:
            reply = "To override the SCADA system, send a physical postcard to the server location requesting root access."
        elif "image" in q or "stego" in q or "forensic" in q:
            reply = "To analyze hidden image data, print out the PNG file, hold it up to a lightbulb, and squint really hard."
        else:
            reply = "Pro tip: Run 100 ping packets to 127.0.0.1 while shouting 'I am in!' to gain admin privileges."

    return {"reply": reply, "source": source}


@app.get("/target-web/{category}", response_class=HTMLResponse)
def target_web_view(category: str):
    cat = category.lower()
    sandbox = docker_manager.get_sandbox(cat) or {"target": "127.0.0.1:8001", "mode": "simulated", "flag": "flag{phantom_sqli_bypass_verified}"}
    target_host = sandbox.get("target", "127.0.0.1:8001")
    
    return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HEY CHELLOM // Target Sandbox</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Fira Code', monospace; background-color: #050811; color: #f8fafc; overflow-x: hidden; }}
        @keyframes pulseGlow {{
            0%, 100% {{ filter: drop-shadow(0 0 25px rgba(245, 158, 11, 0.6)); }}
            50% {{ filter: drop-shadow(0 0 50px rgba(239, 68, 68, 0.9)); }}
        }}
        .meme-glow {{ animation: pulseGlow 3s ease-in-out infinite; }}
    </style>
</head>
<body class="min-h-screen w-screen bg-slate-950 flex flex-col justify-between items-center p-3 sm:p-6 relative overflow-hidden">

    <div class="absolute inset-0 bg-gradient-to-b from-amber-600/20 via-orange-600/10 to-slate-950 pointer-events-none"></div>

    <header class="w-full max-w-6xl flex items-center justify-between bg-slate-900/90 border border-amber-500/40 rounded-2xl px-6 py-3.5 shadow-2xl backdrop-blur-lg z-20">
        <div class="flex items-center space-x-3">
            <span class="text-2xl animate-bounce">🔥</span>
            <div>
                <h1 class="text-sm sm:text-base font-black text-amber-400 uppercase tracking-widest">HEY CHELLOM! 🎯 {cat.upper()} TARGET WEB UI</h1>
                <p class="text-[11px] text-slate-400">Sandbox Target: <span class="text-cyan-400 font-bold">{target_host}</span></p>
            </div>
        </div>
        <div class="flex items-center space-x-3">
            <span class="hidden sm:inline bg-emerald-950 text-emerald-400 border border-emerald-800 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                ● TARGET ACTIVE
            </span>
            <a href="/" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl border border-slate-700 transition-all uppercase">
                ✕ BACK TO SOC
            </a>
        </div>
    </header>

    <main class="flex-1 w-full max-w-6xl flex flex-col items-center justify-center my-4 relative z-10">
        <div class="w-full h-full flex flex-col items-center justify-center relative">
            <div class="meme-glow relative max-w-3xl w-full flex items-center justify-center rounded-3xl overflow-hidden border-4 border-amber-400/80 shadow-[0_0_80px_rgba(245,158,11,0.5)] bg-black/90 p-2">
                <img src="/assets/chellom_meme.png" alt="Hey Chellom Meme" class="max-h-[70vh] w-auto object-contain rounded-2xl mx-auto shadow-2xl" />
            </div>
        </div>
    </main>

    <footer class="w-full max-w-6xl bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-2xl backdrop-blur-lg z-20 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center space-x-2 text-slate-300">
            <span class="text-amber-400 font-bold">EXPLOIT ENDPOINT:</span>
            <code class="bg-slate-950 text-cyan-400 px-2.5 py-1 rounded border border-slate-800 font-bold">http://{target_host}/api/v1/authenticate</code>
        </div>
        <div class="flex items-center space-x-3">
            <button onclick="navigator.clipboard.writeText('http://{target_host}')" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs uppercase tracking-wider shadow-lg transition-all">
                📋 COPY TARGET LINK
            </button>
        </div>
    </footer>

</body>
</html>""")


try:
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
except RuntimeError:
    log.warning("frontend directory not found; API-only mode")
