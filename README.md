# 🌫️👁️ VayuNetra

> **AI-Powered Clean Air Platform**  
> *GDG Indore — Build with AI: Code for Communities (2nd Edition)*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![Google GenAI](https://img.shields.io/badge/Gemini_API-Flash-orange.svg)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg)](https://tailwindcss.com/)

---

## 📌 Overview

Official monitoring stations are sparse across Indian urban clusters—Indore, for instance, operates only 4–6 regulatory AQI monitors across a 500+ sq km footprint. Hyperlocal pollution events such as garbage combustion, construction dust plumes, and vehicular congestion escape official tracking.

**VayuNetra** (*"Netra"* meaning *Eye* in Hindi/Sanskrit) closes this feedback loop. It converts everyday citizen smartphone photos into structured, actionable environmental intelligence via multimodal classification, geospatial mapping, and automated administrative alerts.

---

## 🎯 Architecture & Demo Scope

```text
[ Citizen Photo Upload ] ──► [ Gemini Flash API ] ──► [ Structured JSON Output ]
                                                              │
   ┌──────────────────────────────────────────────────────────┘
   ▼
[ Real-Time Hotspot Map ] ──► [ 24hr Naive Extrapolation ] ──► [ Mock Authority Alert ]
