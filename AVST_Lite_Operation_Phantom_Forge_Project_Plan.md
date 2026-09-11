# AVST-Lite: Operation Phantom Forge (16-Hour Hackathon Plan)

## AI-Powered Cyber Operations Center for CTF Generation and Training

**Optimized 16-Hour Hackathon Execution Plan**  
*Target Environment: Single Laptop | Local AI: Ollama 2B Models (Qwen2.5 1.5B / Gemma 2B / Llama 3.2 1B-3B)*

---

# Executive Summary

AVST-Lite is a streamlined, high-impact version of the AVST research platform tailored for an intensive **16-hour hackathon**. 

It focuses on one core end-to-end mission loop:

$$\text{CVE / Cyber Scenario} \longrightarrow \text{2B AI Mission Brief} \longrightarrow \text{Docker Sandbox} \longrightarrow \text{Evidence Scanner Verification} \longrightarrow \text{AI Tactical Debrief}$$

By shifting from an 8B model to ultra-fast **2B LLMs** (e.g., `qwen2.5:1.5b` or `gemma:2b`) and omitting heavy RAG databases (ChromaDB), AVST-Lite achieves **sub-second AI response times**, negligible VRAM usage, and rock-solid demo reliability.

---

# Why 2B Models & 16-Hour Optimization?

## 1. 2B Model Advantages
- **Sub-Second Inference**: Instant generation of mission lore, tactical intel, and hints on any standard GPU/CPU.
- **Micro Memory Footprint**: Uses under 1.5GB of RAM/VRAM, leaving maximum system memory for Docker containers and Next.js/FastAPI.
- **Reliable JSON Formatting**: Modern 2B models (like `qwen2.5:1.5b-instruct`) excel at structured JSON output when given concise system prompts.

## 2. 16-Hour Scope Refinements
- **No Heavy Vector DBs**: Replaced ChromaDB with structured in-memory prompt injection.
- **Pre-Baked Containers + Dynamic AI Lore**: Pre-package 3 resilient challenge environments (Web, IoT, Forensics) while using the 2B AI to dynamically wrap them in unique mission briefs, target specs, and secret flag variants.

---

# Core Mission Loop

```
[ Mission Briefing (Ollama 2B) ]
               ↓
[ Deploy Sandbox (Docker) ]
               ↓
[ Solve & Submit Flag ]
               ↓
[ Evidence Scanner (Log & HTTP Trace) ]
               ↓
[ AI Tactical Debrief (Ollama 2B) ]
```

---

# Main Features

## 1. Classified Mission Generator (2B LLM Powered)
Transforms generic CTF titles into immersive SOC operations.
- *Input*: Vulnerability type (e.g., SQLi, IoT MQTT, Stego)
- *2B AI Output (JSON)*:
  - Code Name (e.g., `Operation Crimson Gateway`)
  - Target Profile & Lore
  - Tactical Objectives
  - Dynamic Flag Hash (`flag{phantom_...}`)

## 2. Evidence Scanner (Signature Feature)
Inspired by AVST's Flag Provenance System. Instead of a simple `Correct` response, the system displays full provenance tracking:

| Evidence Type | Verification Method | Status |
|---|---|:---:|
| HTTP Response Log | Server Log Match | `VERIFIED` |
| Binary Hash Check | Flag String Trace | `GROUNDED` |
| Payload Signature | Heuristic Check | `CLAIMED` |

*Confidence Levels*: `VERIFIED` (Full Proof), `GROUNDED` (Partial Match), `CLAIMED` (Unverified).

## 3. AI Mission Commander (Fast 2B Chatbot)
Acts as a SOC Commander providing hint tiers without leaking solutions:

| Hint Tier | Cost | AI Behavior |
|---|---|---|
| **Gentle** | 5 XP | Vague directional advice |
| **Tactical** | 10 XP | Specific tool/parameter guidance |
| **Technique** | 20 XP | Conceptual breakdown of the flaw |

## 4. Cyber Operations Dashboard
High-tech SOC interface built with Next.js & Tailwind:
- Animated Threat Map
- Active Mission Dossier
- Web Terminal (xterm.js)
- Evidence Scanner Output
- Live Commander Chat

---

# Challenge Categories (Pre-Baked Containers)

1. **Web Exploitation (`/challenges/web`)**
   - *Scenario*: Vulnerable Employee Portal (SQLi / XSS).
   - *Container*: Lightweight Alpine Nginx + Python Flask app.

2. **IoT & Smart Infrastructure (`/challenges/iot`)**
   - *Scenario*: Compromised ESP32 Irrigation Controller.
   - *Container*: Eclipse Mosquitto MQTT Broker + simulated pump telemetry.
   - *Flag Example*: `flag{pump_override_detected}`

3. **Digital Forensics / Steganography (`/challenges/forensic`)**
   - *Scenario*: Intercepted covert transmission image.
   - *Container*: Static file server containing metadata & hidden binary payloads.

---

# Simplified Technology Stack

| Layer | Technology | 16-Hour Choice Rationale |
|---|---|---|
| **Frontend** | Next.js + Tailwind | Fast UI iteration, dark cyberpunk aesthetic |
| **Backend** | FastAPI (Python) | Async endpoints for Docker & Ollama API |
| **AI Engine** | Ollama | Zero external API latency, 100% local |
| **Model** | `qwen2.5:1.5b` or `gemma:2b` | Fast inference (<1s), ultra-low RAM (<1.5GB) |
| **Context System** | In-Memory Prompt Injection | Replaces ChromaDB to save 3 hours of dev time |
| **Containers** | Docker (Docker SDK for Python) | Isolated, repeatable sandbox execution |
| **Terminal** | `xterm.js` | Embedded terminal experience in browser |

---

# 16-Hour Hourly Execution Timeline

```
[H00-H03] Core Setup & SOC UI Skeleton
[H03-H06] Docker Sandbox & FastAPI Backend
[H06-H09] Ollama 2B Integration & Prompt Engineering
[H09-H12] Evidence Scanner & Provenance Tracking Engine
[H12-H14] UI Polish, Terminal & SFX Audio
[H14-H16] Testing, Dry Run & Presentation Script
```

### Hours 00 – 03: Scaffolding & SOC UI Skeleton
- Initialize Next.js app with TailwindCSS.
- Build dark-mode SOC layout (Header status, Threat map widget, Mission Dossier card).
- Initialize FastAPI project with `/health` and `/api/missions` routes.

### Hours 03 – 06: Docker Sandbox Engine & FastAPI Backend
- Write lightweight `Dockerfile` definitions for Web, IoT, and Forensics challenges.
- Implement Python `docker` SDK integration to start/stop containers dynamically.
- Build flag verification endpoint (`/api/verify`).

### Hours 06 – 09: Ollama 2B Integration & Prompt Engineering
- Pull `qwen2.5:1.5b-instruct` or `gemma:2b` in Ollama.
- Write structured system prompts forcing JSON output for Mission Briefings & Hints.
- Implement FastAPI endpoints for Commander chat (`/api/commander/chat`).

### Hours 09 – 12: Signature Feature — Evidence Scanner UI
- Build the Evidence Scanner component in Next.js with step-by-step verification animations.
- Connect server log capture to display real HTTP/binary provenance badges (`VERIFIED`, `GROUNDED`).
- Implement XP calculation and unlock system.

### Hours 12 – 14: Polish, Terminal UI & Audio Visuals
- Embed `xterm.js` for in-browser CLI access to the target sandbox.
- Add sound effects (cyber clicks, mission unlock alerts) and glowing UI indicators.
- End-to-end integration bug fixing.

### Hours 14 – 16: Demo Prep, Testing & Pitch Dry Runs
- Conduct full dry-run walkthroughs of the 3-minute pitch script.
- Pre-warm Ollama cache and pre-pull all Docker images.
- Prepare demo fallback state (hardcoded JSON snapshots if Ollama fails).

---

# Demo Script (3-Minute Hackathon Pitch)

1. **0:00 - 0:30 (The Hook)**: Show SOC Dashboard & threat map. "Cybersecurity training is either boring quizzes or black-box CTFs. Meet Operation Phantom Forge."
2. **0:30 - 1:15 (Mission Launch)**: Click *Generate Mission*. Ollama 2B creates *Operation Crimson Gateway* in under 1 second. Deploy Docker sandbox.
3. **1:15 - 2:00 (Exploitation & Hint)**: Show xterm.js terminal. Ask AI Commander for a hint (`Tactical` hint costs 10 XP). Solve the challenge.
4. **2:00 - 2:40 (The Wow Factor - Evidence Scanner)**: Submit flag. Show Evidence Scanner verifying HTTP response logs & binary hash (`VERIFIED` provenance).
5. **2:40 - 3:00 (Conclusion)**: Highlight local 2B model efficiency, zero cloud cost, and instant forensic feedback.

---

# Final Thoughts & Hackathon Strategy

1. **2B Models Are the Secret Weapon**: They respond instantly during a live pitch, ensuring zero awkward waiting screens while judges watch.
2. **Focus on Visuals & Provenance**: The Evidence Scanner visually proves the project's technical depth beyond standard CTF frameworks.
3. **Preparedness Wins**: Pre-pulling Docker images and pre-warming Ollama guarantees a smooth 3-minute demo.
