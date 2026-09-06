import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from gemini_client import PollutionReport, analyze_pollution_image
from db import init_db

init_db()
client = TestClient(app)

class TestVayuNetraAPI(unittest.TestCase):

    def test_test_jpg_exists_in_expected_locations(self):
        backend_test_jpg = os.path.join(os.path.dirname(__file__), "test.jpg")
        root_test_jpg = os.path.join(os.path.dirname(__file__), "..", "test.jpg")
        self.assertTrue(
            os.path.exists(backend_test_jpg) or os.path.exists(root_test_jpg),
            "test.jpg must exist in backend/ or repository root for upload scripts"
        )

    @patch("main.analyze_pollution_image")
    def test_create_report_success(self, mock_analyze):
        mock_analyze.return_value = PollutionReport(
            pollution_type="Smoke",
            severity=7,
            confidence=0.85,
            is_spam=False
        )

        dummy_image = b"fake-image-binary-data"
        files = {"file": ("test.jpg", dummy_image, "image/jpeg")}
        data = {"lat": 22.7196, "lon": 75.8577}

        response = client.post("/report", files=files, data=data)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["message"], "Report ingested successfully")
        self.assertIn("report_id", json_data)
        self.assertEqual(json_data["analysis"]["pollution_type"], "Smoke")
        self.assertEqual(json_data["analysis"]["severity"], 7)
        self.assertEqual(json_data["analysis"]["confidence"], 0.85)
        self.assertFalse(json_data["analysis"]["is_spam"])

    def test_metrics_endpoint(self):
        response = client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("aqi", data)
        self.assertIn("pm25", data)

    def test_zones_endpoint(self):
        response = client.get("/zones")
        self.assertEqual(response.status_code, 200)
        zones = response.json()
        self.assertIsInstance(zones, list)
        self.assertGreater(len(zones), 0)

    def test_forecast_endpoint(self):
        response = client.get("/forecast")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("forecast_24h", data)
        self.assertEqual(len(data["forecast_24h"]), 24)

    def test_get_reports_endpoint(self):
        response = client.get("/reports")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key_override"})
    @patch("gemini_client.client")
    def test_analyze_pollution_image_uses_supported_model(self, mock_genai_client):
        mock_response = MagicMock()
        mock_response.text = '{"pollution_type": "Smoke", "severity": 5, "confidence": 0.9, "is_spam": false}'
        mock_genai_client.models.generate_content.return_value = mock_response

        report = analyze_pollution_image(b"test_image", "image/jpeg")

        self.assertEqual(report.pollution_type, "Smoke")
        mock_genai_client.models.generate_content.assert_called_once()
        kwargs = mock_genai_client.models.generate_content.call_args.kwargs
        self.assertEqual(kwargs.get("model"), "gemini-2.5-flash")

if __name__ == "__main__":
    unittest.main()
