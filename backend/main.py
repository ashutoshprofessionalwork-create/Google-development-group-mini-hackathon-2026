import os
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from db import init_db, get_db
from gemini_client import analyze_pollution_image

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
        reports.append({
            "id": row["id"],
            "title": f"{row['pollution_type'] or 'Pollution'} Report (Severity {row['severity']}/10)",
            "type": row["pollution_type"] or "General Emission",
            "desc": f"Confidence: {int((row['confidence'] or 0.8) * 100)}%. Spam: {'Yes' if row['is_spam'] else 'No'}",
            "lat": row["lat"],
            "lng": row["lon"],
            "locationName": "Indore Sector",
            "status": "REJECTED (SPAM)" if row["is_spam"] else row["status"] if "status" in row.keys() else "PENDING REVIEW",
            "timestamp": "Recent",
            "imageUrl": row["image_url"],
            "analysis": {
                "pollution_type": row["pollution_type"],
                "severity": row["severity"],
                "confidence": row["confidence"],
                "is_spam": bool(row["is_spam"])
            }
        })
    return reports


@app.get("/zones")
def get_zones():
    # Base Indore seed zones
    default_zones = [
        {"id": 1, "name": "Vijay Nagar Junction", "lat": 22.7533, "lng": 75.8937, "complaints": 52},
        {"id": 2, "name": "Pithampur Industrial Area", "lat": 22.6148, "lng": 75.6811, "complaints": 84},
        {"id": 3, "name": "Palasia Square", "lat": 22.7244, "lng": 75.8839, "complaints": 18},
        {"id": 4, "name": "Rau Bypass Corridor", "lat": 22.6321, "lng": 75.8052, "complaints": 31},
        {"id": 5, "name": "Bhawarkua Square", "lat": 22.6916, "lng": 75.8672, "complaints": 12}
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

    # 4. Insert into SQLite
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reports (pollution_type, severity, confidence, lat, lon, image_url, is_spam, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            analysis.pollution_type,
            analysis.severity,
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
