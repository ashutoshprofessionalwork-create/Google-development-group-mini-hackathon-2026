from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from db import init_db, get_db
from gemini_client import analyze_pollution_image

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="VayuNetra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health_check():
    return {"status": "VayuNetra Backend is live and DB is initialized"}


@app.post("/report")
@limiter.limit("5/minute")
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

    # 3. Mock Google Cloud Storage URL (to unblock the frontend build)
    mock_image_url = f"https://storage.googleapis.com/vayunetra-mock/{file.filename}"

    # 4. Insert into SQLite
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reports (pollution_type, severity, confidence, lat, lon, image_url, is_spam)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            analysis.pollution_type,
            analysis.severity,
            analysis.confidence,
            lat,
            lon,
            mock_image_url,
            analysis.is_spam,
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
