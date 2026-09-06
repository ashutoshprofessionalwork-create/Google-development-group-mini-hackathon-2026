import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Fallback default API key if GEMINI_API_KEY environment variable is not explicitly set
DEFAULT_API_KEY = "AQ.Ab8RN6LL-K4FErOkevYNdeZXtf-33yhDwVuq62_Od0XPb_SBpw"
api_key = os.getenv("GEMINI_API_KEY", DEFAULT_API_KEY)
client = genai.Client(api_key=api_key)


class PollutionReport(BaseModel):
    pollution_type: str = Field(
        description="Classify the type of pollution (e.g., 'Smoke', 'Construction Dust', 'Vehicle Exhaust'). If none, return 'None'."
    )
    severity: int = Field(description="Estimated severity on a scale of 1 to 10.")
    estimated_aqi: int = Field(
        description="Estimated local Air Quality Index (AQI) based on visual pollution density (50 to 500)."
    )
    confidence: float = Field(
        description="Confidence score of the classification between 0.0 and 1.0."
    )
    is_spam: bool = Field(
        description="True if the image does not show an outdoor environment or is totally irrelevant, False otherwise."
    )


def analyze_pollution_image(image_bytes: bytes, mime_type: str) -> PollutionReport:
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    if not os.getenv("GEMINI_API_KEY") and api_key == DEFAULT_API_KEY:
        # Fallback mock response for offline / unauthenticated local development & testing
        return PollutionReport(
            pollution_type="Smoke (Mocked - Set GEMINI_API_KEY)",
            severity=6,
            estimated_aqi=240,
            confidence=0.88,
            is_spam=False
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            image_part,
            "Analyze this image for air pollution hotspots. Output strictly using the required JSON schema.",
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PollutionReport,
            temperature=0.1,
        ),
    )

    data = json.loads(response.text)
    return PollutionReport(**data)
