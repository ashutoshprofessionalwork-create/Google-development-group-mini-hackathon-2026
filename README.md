# VayuNetra 🌫️👁️
**AI-Powered Clean Air Platform** — GDG Indore, Build with AI: Code for Communities (2nd Edition)

> "Netra" means eye in Hindi/Sanskrit. VayuNetra is a real-time eye on air quality for Indian cities — fusing citizen reports, satellite data, and sensor readings into verified pollution hotspots and forecasts.

**Problem Statement:** Clear Air and Climate Resilience
**Team:** Harsh Kumar (Lead), Ashutosh Kashyap, Gatik Harpude, Anamika Goswami

---

## ⚠️ Read this first: what we are ACTUALLY building for the demo

India's official AQI stations are sparse (Indore has only 4–6 covering 500+ sq km). We're **not** trying to build the full production platform in this hackathon. We are building exactly this, end to end, live:

```
Citizen uploads photo → Gemini classifies pollution type → shows on a live hotspot map → simple 24hr forecast → mock "alert sent to authority" screen
```

Everything else (Gemini Nano on-device, Federated Learning across states, real ESP32 sensors, WhatsApp/IVR bots, full Vertex AI forecasting) is **roadmap only** — it goes in the slides as future work, not in the code. Do not spend hackathon time on these. If you're unsure whether something is in-scope, check the table below before building it.

| Feature | Status |
|---|---|
| Photo upload + Gemini classification | ✅ Build this |
| Live hotspot map (seeded or real points) | ✅ Build this |
| Simple 24hr forecast (basic extrapolation) | ✅ Build this |
| Mock authority alert screen | ✅ Build this |
| Gemini Nano on-device | ❌ Roadmap only — needs AICore hardware, will not run on demo phones |
| Federated Learning across states | ❌ Roadmap only — not feasible in a hackathon sandbox |
| Real ESP32/PM2.5 sensor hardware | ❌ Roadmap only |
| Apigee API gateway | ❌ Skip — use FastAPI + `slowapi` instead |
| WhatsApp bot / IVR / kiosks | ❌ Roadmap only |

**Rule of thumb:** if it's not in the "Built for this Demo" list above, it's a slide bullet, not a to-do.

---

## 🧱 Tech stack & build order

Build in this order — each step unblocks the next.

### 1. Scaffolding & hosting
- GitHub repo (this one)
- Docker
- Google Cloud Run (backend deployment)

### 2. Backend / API
- FastAPI (Python 3.11+)
- Pydantic (structuring Gemini's output)
- `slowapi` (basic rate limiting)

### 3. Database
- SQLite (fastest to set up) **or** Supabase Postgres if we want it to look production-grade
- PostGIS — optional, only if we have time for real spatial clustering

### 4. AI layer — the centerpiece
- Gemini 1.5/2.x Flash via `google-genai` SDK
- Strict JSON-schema prompt (pollution type, severity, confidence, spam flag)
- Google Earth Engine — optional stretch goal for real satellite overlay

### 5. Storage
- Google Cloud Storage (uploaded photos, signed URLs)

### 6. Frontend — citizen side
- Next.js + Tailwind CSS
- Mapbox GL JS or Google Maps embed for the hotspot map

### 7. Forecast
- Simple linear/seasonal-naive extrapolation in Python — **not** a live-trained model

### 8. Authority side
- Static mock screen showing "alert routed with GPS + photo evidence" — no real dashboard backend needed

### 9. Safety net
- Record a working demo on video before presenting, in case live wifi/API calls fail

---

## 👥 Suggested roles

_(Fill in once assigned — this keeps everyone unblocked and avoids two people building the same thing)_

| Area | Owner |
|---|---|
| Backend (FastAPI, DB, Gemini integration) | |
| Frontend (Next.js upload flow + map) | |
| AI prompt design + testing | |
| Slides, wireframes, demo script, video backup | |

---

## 📁 Suggested repo structure

```
vayunetra/
├── backend/
│   ├── main.py              # FastAPI app, /report endpoint
│   ├── gemini_client.py     # Gemini call + JSON schema prompt
│   ├── db.py                # DB models/connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/ or app/       # Next.js pages (home, upload, map, authority mock)
│   ├── components/
│   └── package.json
├── docs/
│   └── demo-script.md       # Step-by-step for the live demo run-through
└── README.md
```

---

## 🚀 Getting started (backend)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn google-genai pydantic slowapi
uvicorn main:app --reload
```

## 🚀 Getting started (frontend)

```bash
cd frontend
npm install
npm run dev
```

---

## 🎬 Demo script (fill in as we build)

1. Open the app, show current AQI card
2. Tap "Snap & Report," upload a photo of smoke/dust
3. Gemini classifies it live (~1s) — show confidence score
4. Show the point appear on the hotspot map
5. Show the 24hr forecast card
6. Show the mock "alert sent to authority" screen
7. (Backup: cut to recorded video if anything fails live)

---

## 🗺️ Roadmap (post-hackathon — slides only, not code)

- Gemini Nano on-device classification
- Full 72-hour Vertex AI corridor-level forecasting
- Federated Learning layer across state pollution boards
- Real ESP32 + PM2.5/PM10 sensor network
- WhatsApp bot, missed-call/IVR, community kiosks
- Multi-language voice input support

---

## ✅ Hackathon submission checklist

- [ ] Uses at least one Google technology (Gemini ✅)
- [ ] Presentation ≤ 10 slides
- [ ] One project/PPT per team
- [ ] Slides match what's actually demoed (no overclaiming Nano/Federated Learning/Apigee as "current")
- [ ] Backup demo video recorded
