import os
import math
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from db import init_db, get_db
from gemini_client import analyze_pollution_image

OFFICIAL_STATIONS = [
    {"name": "Chhoti Gwaltoli CPCB Central Station", "lat": 22.7196, "lng": 75.8577, "aqi": 188},
    {"name": "Vijay Nagar MPPCB Station", "lat": 22.7533, "lng": 75.8937, "aqi": 195},
    {"name": "Pithampur Industrial Station", "lat": 22.6148, "lng": 75.6811, "aqi": 245},
    {"name": "Sanwer Road Industrial Station", "lat": 22.7712, "lng": 75.9012, "aqi": 210},
    {"name": "IIT Indore Simrol Baseline Station", "lat": 22.5204, "lng": 75.9207, "aqi": 92}
]


def find_closest_station(lat: float, lon: float):
    best_station = None
    min_dist = float("inf")
    
    for st in OFFICIAL_STATIONS:
        dlat = math.radians(st["lat"] - lat)
        dlon = math.radians(st["lng"] - lon)
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat)) * math.cos(math.radians(st["lat"])) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = 6371.0 * c
        
        if dist_km < min_dist:
            min_dist = dist_km
            best_station = st
            
    return {
        "name": best_station["name"],
        "station_aqi": best_station["aqi"],
        "distance_km": round(min_dist, 1)
    }

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="VayuNetra API")

# Mount mockdatapic directory if it exists
mock_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mockdatapic"))
if os.path.exists(mock_dir):
    app.mount("/mockdatapic", StaticFiles(directory=mock_dir), name="mockdatapic")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class StatusUpdate(BaseModel):
    status: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health_check():
    return {"status": "VayuNetra Backend is live and DB is initialized"}


@app.get("/metrics")
def get_metrics():
    return {
        "aqi": 184,
        "status": "Moderate / Unhealthy for Sensitive Groups",
        "pm25": 88.5,
        "pm10": 142.0,
        "so2": 14.2,
        "no2": 32.8
    }


@app.get("/reports")
def get_reports(sort_by_severity: bool = True):
    conn = get_db()
    cursor = conn.cursor()
    if sort_by_severity:
        cursor.execute("SELECT * FROM reports ORDER BY severity DESC, id DESC")
    else:
        cursor.execute("SELECT * FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    reports = []
    for row in rows:
        lat = row["lat"] if row["lat"] else 22.7196
        lon = row["lon"] if row["lon"] else 75.8577
        est_aqi = row["estimated_aqi"] if ("estimated_aqi" in row.keys() and row["estimated_aqi"]) else (100 + (row["severity"] or 5) * 28)
        rep_count = row["report_count"] if ("report_count" in row.keys() and row["report_count"]) else 1
        raw_status = row["status"] if "status" in row.keys() else "PENDING REVIEW"
        
        # Closest station comparison
        closest = find_closest_station(lat, lon)
        aqi_delta = est_aqi - closest["station_aqi"]
        
        # Verification badge determination rule:
        # 1. Rejected/Spam -> REJECTED
        # 2. Admin verified manually OR >= 50 people reported -> ADMIN VERIFIED
        # 3. < 50 people reported -> AI VERIFIED
        if row["is_spam"] or raw_status == "REJECTED" or raw_status == "REJECTED (SPAM)":
            badge_status = "REJECTED"
        elif raw_status == "ADMIN VERIFIED" or rep_count >= 50:
            badge_status = "ADMIN VERIFIED"
        else:
            badge_status = "AI VERIFIED"

        reports.append({
            "id": row["id"],
            "title": f"{row['pollution_type'] or 'Pollution'} Report (Severity {row['severity']}/10)",
            "type": row["pollution_type"] or "General Emission",
            "desc": f"Confidence: {int((row['confidence'] or 0.8) * 100)}%. Spam: {'Yes' if row['is_spam'] else 'No'}",
            "lat": lat,
            "lng": lon,
            "locationName": "Indore Sector",
            "status": badge_status,
            "raw_status": raw_status,
            "estimated_aqi": est_aqi,
            "report_count": rep_count,
            "closest_station": {
                "name": closest["name"],
                "station_aqi": closest["station_aqi"],
                "distance_km": closest["distance_km"],
                "delta": f"+{aqi_delta}" if aqi_delta > 0 else f"{aqi_delta}"
            },
            "timestamp": "Recent",
            "imageUrl": row["image_url"],
            "analysis": {
                "pollution_type": row["pollution_type"],
                "severity": row["severity"],
                "estimated_aqi": est_aqi,
                "confidence": row["confidence"],
                "is_spam": bool(row["is_spam"])
            }
        })
    return reports


@app.get("/zones")
def get_zones():
    # Official CPCB & MPPCB Monitoring Stations and Industrial Hotspots in Indore
    default_zones = [
        {"id": 1, "name": "Vijay Nagar MPPCB Station", "lat": 22.7533, "lng": 75.8937, "complaints": 52, "type": "CPCB/MPPCB Station", "aqi": 195},
        {"id": 2, "name": "Pithampur Industrial Station", "lat": 22.6148, "lng": 75.6811, "complaints": 84, "type": "CPCB/MPPCB Station", "aqi": 245},
        {"id": 3, "name": "Chhoti Gwaltoli CPCB Central Station", "lat": 22.7196, "lng": 75.8577, "complaints": 45, "type": "CPCB/MPPCB Station", "aqi": 188},
        {"id": 4, "name": "Sanwer Road Industrial Station", "lat": 22.7712, "lng": 75.9012, "complaints": 62, "type": "CPCB/MPPCB Station", "aqi": 210},
        {"id": 5, "name": "Palasia Square Corridor", "lat": 22.7244, "lng": 75.8839, "complaints": 18, "type": "Urban Hotspot", "aqi": 172},
        {"id": 6, "name": "Rau Bypass Corridor", "lat": 22.6321, "lng": 75.8052, "complaints": 31, "type": "Urban Hotspot", "aqi": 165},
        {"id": 7, "name": "IIT Indore Simrol Baseline Station", "lat": 22.5204, "lng": 75.9207, "complaints": 4, "type": "Academic Baseline Station", "aqi": 92}
    ]
    return default_zones


@app.get("/forecast")
def get_forecast():
    # Simple linear extrapolation for 24-hour forecast
    current_aqi = 184
    hourly = []
    for h in range(1, 25):
        # Peak around traffic/evening hours, slight decrease at night
        variation = int(15 * (1 if 8 <= (h % 24) <= 20 else -0.5))
        projected_aqi = max(50, current_aqi + variation + (h % 3) * 2)
        hourly.append({
            "hour": f"+{h}h",
            "aqi": projected_aqi,
            "category": "Moderate" if projected_aqi <= 200 else "Poor"
        })
    return {"current_aqi": current_aqi, "forecast_24h": hourly}


@app.patch("/reports/{report_id}/status")
def update_report_status(report_id: int, body: StatusUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (body.status, report_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Status updated successfully", "report_id": report_id, "status": body.status}


@app.post("/report")
@limiter.limit("10/minute")
async def create_report(
    request: Request,
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
):
    # 1. Read the uploaded file
    image_bytes = await file.read()

    # 2. Pass to Gemini for classification
    analysis = analyze_pollution_image(image_bytes, file.content_type)

    # 3. Save file locally in mockdatapic folder and construct URL
    save_filename = f"upload_{Date_now() if 'Date_now' in globals() else 1000}_{file.filename}"
    save_path = os.path.join(mock_dir, save_filename)
    try:
        with open(save_path, "wb") as f:
            f.write(image_bytes)
        image_url = f"http://localhost:8000/mockdatapic/{save_filename}"
    except Exception:
        image_url = f"https://storage.googleapis.com/vayunetra-mock/{file.filename}"

    # 4. Extract estimated_aqi from analysis or calculate
    est_aqi = getattr(analysis, "estimated_aqi", 100 + (analysis.severity or 5) * 28)

    # 5. Insert into SQLite
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reports (pollution_type, severity, estimated_aqi, report_count, confidence, lat, lon, image_url, is_spam, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            analysis.pollution_type,
            analysis.severity,
            est_aqi,
            1, # Initial report count = 1 (< 50 -> AI VERIFIED badge)
            analysis.confidence,
            lat,
            lon,
            image_url,
            analysis.is_spam,
            "REJECTED (SPAM)" if analysis.is_spam else "PENDING REVIEW"
        ),
    )
    conn.commit()
    report_id = cursor.lastrowid

    return {
        "message": "Report ingested successfully",
        "report_id": report_id,
        "analysis": (
            analysis.model_dump()
            if hasattr(analysis, "model_dump")
            else analysis.dict()
        ),
    }
