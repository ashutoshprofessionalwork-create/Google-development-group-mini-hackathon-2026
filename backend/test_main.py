import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from gemini_client import PollutionReport, analyze_pollution_image
from db import init_db

init_db()
client = TestClient(app)

class TestVayuNetraAPI(unittest.TestCase):

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

    @patch("gemini_client.client")
    def test_analyze_pollution_image_uses_supported_model(self, mock_genai_client):
        mock_response = MagicMock()
        mock_response.text = '{"pollution_type": "Smoke", "severity": 5, "confidence": 0.9, "is_spam": false}'
        mock_genai_client.models.generate_content.return_value = mock_response

        report = analyze_pollution_image(b"test_image", "image/jpeg")

        self.assertEqual(report.pollution_type, "Smoke")
        mock_genai_client.models.generate_content.assert_called_once()
        kwargs = mock_genai_client.models.generate_content.call_args.kwargs
        self.assertEqual(kwargs.get("model"), "gemini-3.6-flash")

if __name__ == "__main__":
    unittest.main()
