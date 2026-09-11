import json
import logging
import time
import urllib.request
import urllib.error
from typing import Optional

log = logging.getLogger("ollama-client")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"
TIMEOUT = 6


def _call(prompt: str, model: str = MODEL) -> Optional[str]:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json"}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        start = time.time()
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read())
        log.info("ollama responded in %.2fs", time.time() - start)
        return body.get("response")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        log.warning("ollama unavailable: %s", exc)
        return None


def generate_mission(category: str, codename: str, vector: str) -> Optional[dict]:
    prompt = (
        "You are a tactical SOC mission writer for a cybersecurity CTF. "
        f'Write a short (2-3 sentence) classified mission briefing for a "{category}" challenge '
        f'code-named "Operation {codename}" involving {vector}. '
        'Respond ONLY as JSON: {"lore": "..."}'
    )
    raw = _call(prompt)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"lore": raw.strip()}


def commander_reply(category: str, question: str, context: str) -> Optional[str]:
    prompt = (
        "You are 'Commander', a terse tactical AI assistant in a cybersecurity training SOC. "
        f"Context: the active challenge is a {category} exploitation scenario. {context} "
        f'The operator asks: "{question}". '
        "Give a short (1-2 sentence) tactical response. Do not reveal the flag directly. "
        'Respond ONLY as JSON: {"reply": "..."}'
    )
    raw = _call(prompt)
    if not raw:
        return None
    try:
        return json.loads(raw).get("reply")
    except json.JSONDecodeError:
        return raw.strip()
