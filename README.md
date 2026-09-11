<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# AVST-Lite: Operation Phantom Forge 🎯

AI-Powered Cyber Operations Center for CTF Generation and Training.

---

## Basic Details

### Team Name: AVST Cyber

### Project Description
AVST-Lite is a miniature, high-impact cyber training platform where users become **Cyber Operatives** completing classified missions. It combines real-world vulnerability scenarios, dynamic AI mission briefs, isolated Docker sandboxes, evidence-based flag provenance verification, and a local AI Cyber Commander.

### The Problem (that doesn't exist)
Current cybersecurity learning platforms suffer from static, repetitive challenges, ungrounded AI tutors that leak answers directly, and flag verification systems that offer zero forensic explanation of why a submission is trustworthy.

### The Solution (that nobody asked for)
AVST-Lite replaces standard CTF quizzes with a full Security Operations Center (SOC) workflow:

$$\text{Mission Briefing} \longrightarrow \text{Docker Sandbox} \longrightarrow \text{Exploitation} \longrightarrow \text{Evidence Scanner} \longrightarrow \text{AI Debrief}$$

Instead of displaying a generic `Correct`, the **Evidence Scanner** inspects HTTP response logs, server binary traces, and payload signatures to establish provenance (`VERIFIED`, `GROUNDED`, `CLAIMED`).

---

## Technical Details

### Technologies Used

#### Software:
- **Languages**: Python 3.11+, JavaScript (HTML5/ES6)
- **Backend Framework**: FastAPI, Uvicorn
- **AI / LLM Engine**: Ollama (Qwen 2.5 1.5B / 3B) with automatic canned fallback
- **Containerization**: Docker & Docker SDK for Python
- **Frontend / UI**: Next.js / Tailwind CSS / xterm.js

---

## Structure & Architecture

- `frontend/index.html` — Tactical SOC dashboard (Tailwind CDN, interactive terminal, threat map, evidence scanner).
- `backend/main.py` — FastAPI application managing mission generation, Docker sandbox lifecycle, flag verification (Evidence Scanner), hints, and AI Commander chat.
- `backend/docker_manager.py` — Manages per-category sandbox containers (`Web`, `IoT`, `Forensics`) and inspects container logs for provenance tracking.
- `backend/ollama_client.py` — Connects to local Ollama (`qwen2.5:1.5b`) for mission lore and Commander chat (falls back gracefully to pre-built templates if Ollama is offline).
- `backend/challenges/{web,iot,forensic}/` — Sandboxed Dockerfiles and vulnerable applications (SQLi auth bypass, MQTT SCADA pump override, LSB steganography).

---

## Implementation

### Installation

```bash
# Clone the repository
git clone https://github.com/Melvin-svg/danger_mac.git
cd danger_mac/backend

# Create virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Application

```bash
# Start backend server (serves frontend automatically)
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

#### Optional Real Sandbox & Local AI Setup:
- **Docker Desktop**: Backend auto-builds and runs real sandbox containers per mission.
- **Ollama**: Run `ollama pull qwen2.5:1.5b` for live AI mission generation.

---

## Verified End-to-End Test Results

All three mission categories have been verified against live Docker containers:
1. **Web (SQL Injection)**: Authenticated via `' OR 1=1--`, recovered flag, verified via Evidence Scanner (`VERIFIED / GROUNDED / CONFIRMED`).
2. **IoT (MQTT SCADA Override)**: Sent `{"override": true}` to `/scada/pumps/override`, extracted dump flag payload, verified provenance.
3. **Forensics (Steganography)**: Downloaded `transmission.png` from container, decoded LSB red-channel bytes offline, submitted flag and verified.
4. **Negative Test**: Tested incorrect flag (`flag{invalid_submission}`) → correctly rejected across all provenance levels.

---

Made with ❤️ for Hackathons

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
