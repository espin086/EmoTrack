"""
Comprehensive pytest tests for EmoTrack Backend API

Run with: pytest backend/test_app.py -v
"""
import io
import json
import time
from unittest.mock import patch, MagicMock
import pytest
from fastapi import status


@pytest.mark.unit
class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_returns_success(self, api_client):
        """Test that root endpoint returns successful response"""
        response = api_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert response.json()["message"] == "EmoTrack API is running"


@pytest.mark.unit
class TestHealthCheck:
    """Tests for health check endpoint"""

    def test_health_check_success(self, api_client):
        """Test health check returns healthy status"""
        response = api_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_health_check_with_broken_db(self, api_client, monkeypatch):
        """Test health check with database connection failure"""
        def mock_broken_db():
            raise Exception("Database connection failed")

        # Patch the database connection
        with patch("backend.app.get_db", side_effect=mock_broken_db):
            response = api_client.get("/health")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "unhealthy"
            assert "error" in data


@pytest.mark.aws
@pytest.mark.integration
class TestEmotionDetection:
    """Tests for emotion detection endpoint"""

    def test_detect_emotion_success(self, api_client, sample_jpeg_bytes, mock_rekognition_response):
        """Test successful emotion detection"""
        with patch("backend.app.client.detect_faces", return_value=mock_rekognition_response):
            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = api_client.post("/detect-emotion", files=files)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["emotion"] == "HAPPY"
            assert data["confidence"] == 98.5
            assert "all_emotions" in data
            assert len(data["all_emotions"]) == 3

    def test_detect_emotion_no_face(self, api_client, sample_jpeg_bytes, mock_rekognition_no_face):
        """Test emotion detection when no face is detected"""
        with patch("backend.app.client.detect_faces", return_value=mock_rekognition_no_face):
            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = api_client.post("/detect-emotion", files=files)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["emotion"] == "NO FACE"
            assert data["confidence"] == 0

    def test_detect_emotion_invalid_file(self, api_client):
        """Test emotion detection with invalid image file"""
        invalid_data = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(invalid_data), "text/plain")}

        with patch("backend.app.client.detect_faces", side_effect=Exception("Invalid image")):
            response = api_client.post("/detect-emotion", files=files)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_detect_emotion_missing_file(self, api_client):
        """Test emotion detection without file upload"""
        response = api_client.post("/detect-emotion")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_detect_emotion_aws_error(self, api_client, sample_jpeg_bytes):
        """Test emotion detection when AWS service fails"""
        with patch("backend.app.client.detect_faces", side_effect=Exception("AWS Service Error")):
            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = api_client.post("/detect-emotion", files=files)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.database
@pytest.mark.unit
class TestEmotionBatch:
    """Tests for batch emotion save endpoint"""

    def test_save_batch_success(self, api_client):
        """Test successful batch save"""
        emotions_data = {
            "emotions": [
                {"timestamp": time.time(), "emotion": "HAPPY"},
                {"timestamp": time.time() + 1, "emotion": "SAD"},
                {"timestamp": time.time() + 2, "emotion": "ANGRY"}
            ]
        }

        response = api_client.post("/emotions/batch", json=emotions_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Saved 3 emotions"

    def test_save_batch_empty(self, api_client):
        """Test saving empty batch"""
        emotions_data = {"emotions": []}
        response = api_client.post("/emotions/batch", json=emotions_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Saved 0 emotions"

    def test_save_batch_invalid_data(self, api_client):
        """Test batch save with invalid data structure"""
        invalid_data = {"emotions": [{"timestamp": "invalid", "emotion": "HAPPY"}]}
        response = api_client.post("/emotions/batch", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_save_batch_missing_fields(self, api_client):
        """Test batch save with missing required fields"""
        invalid_data = {"emotions": [{"timestamp": time.time()}]}  # Missing emotion
        response = api_client.post("/emotions/batch", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_save_batch_large_dataset(self, api_client):
        """Test batch save with large number of emotions"""
        current_time = time.time()
        emotions_data = {
            "emotions": [
                {"timestamp": current_time + i, "emotion": "HAPPY"}
                for i in range(1000)
            ]
        }

        response = api_client.post("/emotions/batch", json=emotions_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Saved 1000 emotions"


@pytest.mark.database
@pytest.mark.unit
class TestDailyStats:
    """Tests for daily statistics endpoint"""

    def test_daily_stats_default(self, api_client, populated_test_db):
        """Test daily stats with default 7 days"""
        response = api_client.get("/emotions/daily-stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify structure of first item
        first_item = data[0]
        assert "date" in first_item
        assert "emotion" in first_item
        assert "count" in first_item
        assert "percentage" in first_item
        assert first_item["percentage"] > 0

    def test_daily_stats_custom_days(self, api_client, populated_test_db):
        """Test daily stats with custom day range"""
        response = api_client.get("/emotions/daily-stats?days=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_daily_stats_empty_database(self, api_client):
        """Test daily stats with no emotion data"""
        response = api_client.get("/emotions/daily-stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_daily_stats_invalid_days(self, api_client):
        """Test daily stats with invalid days parameter"""
        response = api_client.get("/emotions/daily-stats?days=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_daily_stats_negative_days(self, api_client):
        """Test daily stats with negative days parameter"""
        response = api_client.get("/emotions/daily-stats?days=-5")
        assert response.status_code == status.HTTP_200_OK
        # Should handle gracefully, likely return empty or all data


@pytest.mark.database
@pytest.mark.unit
class TestEmotionSummary:
    """Tests for emotion summary endpoint"""

    def test_summary_with_data(self, api_client, populated_test_db):
        """Test summary with populated database"""
        response = api_client.get("/emotions/summary")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify structure
        assert "total_emotions_recorded" in data
        assert "emotion_distribution" in data
        assert "most_recent" in data
        assert "date_range" in data

        # Verify content
        assert data["total_emotions_recorded"] > 0
        assert isinstance(data["emotion_distribution"], dict)
        assert len(data["emotion_distribution"]) > 0

        # Verify emotion distribution structure
        for emotion, stats in data["emotion_distribution"].items():
            assert "count" in stats
            assert "percentage" in stats
            assert stats["count"] > 0
            assert 0 <= stats["percentage"] <= 100

        # Verify most recent
        assert data["most_recent"]["emotion"] is not None
        assert data["most_recent"]["timestamp"] is not None

    def test_summary_empty_database(self, api_client):
        """Test summary with empty database"""
        response = api_client.get("/emotions/summary")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_emotions_recorded"] == 0
        assert len(data["emotion_distribution"]) == 0

    def test_summary_percentage_calculation(self, api_client):
        """Test that summary percentages add up to 100%"""
        # Add known emotions
        emotions_data = {
            "emotions": [
                {"timestamp": time.time(), "emotion": "HAPPY"},
                {"timestamp": time.time() + 1, "emotion": "HAPPY"},
                {"timestamp": time.time() + 2, "emotion": "SAD"},
                {"timestamp": time.time() + 3, "emotion": "ANGRY"}
            ]
        }
        api_client.post("/emotions/batch", json=emotions_data)

        response = api_client.get("/emotions/summary")
        data = response.json()

        # Sum all percentages
        total_percentage = sum(
            stats["percentage"] for stats in data["emotion_distribution"].values()
        )

        # Should be approximately 100% (allow for rounding)
        assert 99.9 <= total_percentage <= 100.1


@pytest.mark.database
@pytest.mark.unit
class TestExportEmotions:
    """Tests for emotion export endpoint"""

    def test_export_json_format(self, api_client, populated_test_db):
        """Test exporting emotions in JSON format"""
        response = api_client.get("/emotions/export?format=json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["format"] == "json"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Verify structure of first item
        first_item = data["data"][0]
        assert "timestamp" in first_item
        assert "emotion" in first_item
        assert "created_at" in first_item

    def test_export_csv_format(self, api_client, populated_test_db):
        """Test exporting emotions in CSV format"""
        response = api_client.get("/emotions/export?format=csv")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["format"] == "csv"
        assert "data" in data
        assert isinstance(data["data"], str)
        assert "timestamp,emotion,created_at" in data["data"]  # CSV header

    def test_export_empty_database(self, api_client):
        """Test exporting from empty database"""
        response = api_client.get("/emotions/export?format=json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["format"] == "json"
        assert len(data["data"]) == 0

    def test_export_default_format(self, api_client, populated_test_db):
        """Test export with no format specified defaults to JSON"""
        response = api_client.get("/emotions/export")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["format"] == "json"


@pytest.mark.database
@pytest.mark.unit
class TestClearEmotions:
    """Tests for clear emotions endpoint"""

    def test_clear_without_confirmation(self, api_client):
        """Test that clear fails without confirmation"""
        response = api_client.delete("/emotions/clear")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Confirmation required" in data["detail"]

    def test_clear_with_false_confirmation(self, api_client):
        """Test that clear fails with false confirmation"""
        response = api_client.delete("/emotions/clear?confirm=false")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_clear_with_confirmation(self, api_client, populated_test_db):
        """Test successful clear with confirmation"""
        # Verify data exists
        response = api_client.get("/emotions/summary")
        assert response.json()["total_emotions_recorded"] > 0

        # Clear data
        response = api_client.delete("/emotions/clear?confirm=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cleared" in data["message"].lower()

        # Verify data is gone
        response = api_client.get("/emotions/summary")
        assert response.json()["total_emotions_recorded"] == 0

    def test_clear_empty_database(self, api_client):
        """Test clearing already empty database"""
        response = api_client.delete("/emotions/clear?confirm=true")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests"""

    def test_complete_workflow(self, api_client, sample_jpeg_bytes, mock_rekognition_response):
        """Test complete workflow: detect -> save -> retrieve -> export -> clear"""

        # 1. Detect emotion
        with patch("backend.app.client.detect_faces", return_value=mock_rekognition_response):
            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = api_client.post("/detect-emotion", files=files)
            assert response.status_code == status.HTTP_200_OK
            detected_emotion = response.json()["emotion"]

        # 2. Save batch of emotions
        emotions_data = {
            "emotions": [
                {"timestamp": time.time(), "emotion": detected_emotion},
                {"timestamp": time.time() + 1, "emotion": "SAD"},
                {"timestamp": time.time() + 2, "emotion": "HAPPY"}
            ]
        }
        response = api_client.post("/emotions/batch", json=emotions_data)
        assert response.status_code == status.HTTP_200_OK

        # 3. Get summary
        response = api_client.get("/emotions/summary")
        assert response.status_code == status.HTTP_200_OK
        summary = response.json()
        assert summary["total_emotions_recorded"] == 3

        # 4. Get daily stats
        response = api_client.get("/emotions/daily-stats?days=1")
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert len(stats) > 0

        # 5. Export data
        response = api_client.get("/emotions/export?format=json")
        assert response.status_code == status.HTTP_200_OK
        export = response.json()
        assert len(export["data"]) == 3

        # 6. Clear data
        response = api_client.delete("/emotions/clear?confirm=true")
        assert response.status_code == status.HTTP_200_OK

        # 7. Verify cleared
        response = api_client.get("/emotions/summary")
        assert response.json()["total_emotions_recorded"] == 0

    def test_concurrent_batch_saves(self, api_client):
        """Test multiple concurrent batch saves"""
        current_time = time.time()

        for i in range(5):
            emotions_data = {
                "emotions": [
                    {"timestamp": current_time + i * 10, "emotion": "HAPPY"},
                    {"timestamp": current_time + i * 10 + 1, "emotion": "SAD"}
                ]
            }
            response = api_client.post("/emotions/batch", json=emotions_data)
            assert response.status_code == status.HTTP_200_OK

        # Verify all saved
        response = api_client.get("/emotions/summary")
        summary = response.json()
        assert summary["total_emotions_recorded"] == 10
