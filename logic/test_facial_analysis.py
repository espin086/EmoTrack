"""
Unit tests for facial_analysis module

Run with: pytest logic/test_facial_analysis.py -v
"""
import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from logic.facial_analysis import detect_emotion


@pytest.mark.unit
class TestDetectEmotion:
    """Tests for detect_emotion function"""

    @pytest.fixture
    def sample_frame(self):
        """Create a sample image frame"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)
        return frame

    @pytest.fixture
    def mock_rekognition_happy(self):
        """Mock AWS Rekognition response with HAPPY emotion"""
        return {
            "FaceDetails": [
                {
                    "Emotions": [
                        {"Type": "HAPPY", "Confidence": 98.5},
                        {"Type": "SAD", "Confidence": 1.2},
                        {"Type": "CALM", "Confidence": 0.3}
                    ]
                }
            ]
        }

    @pytest.fixture
    def mock_rekognition_multiple_emotions(self):
        """Mock AWS Rekognition response with multiple emotions"""
        return {
            "FaceDetails": [
                {
                    "Emotions": [
                        {"Type": "SURPRISED", "Confidence": 85.3},
                        {"Type": "HAPPY", "Confidence": 10.2},
                        {"Type": "CONFUSED", "Confidence": 4.5}
                    ]
                }
            ]
        }

    @pytest.fixture
    def mock_rekognition_no_face(self):
        """Mock AWS Rekognition response with no face detected"""
        return {"FaceDetails": []}

    def test_detect_emotion_success(self, sample_frame, mock_rekognition_happy):
        """Test successful emotion detection returns highest confidence emotion"""
        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_rekognition_happy):
            emotion = detect_emotion(sample_frame)
            assert emotion == "HAPPY"

    def test_detect_emotion_multiple_emotions(self, sample_frame, mock_rekognition_multiple_emotions):
        """Test that detect_emotion returns the emotion with highest confidence"""
        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_rekognition_multiple_emotions):
            emotion = detect_emotion(sample_frame)
            assert emotion == "SURPRISED"

    def test_detect_emotion_no_face(self, sample_frame, mock_rekognition_no_face):
        """Test emotion detection when no face is detected"""
        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_rekognition_no_face):
            emotion = detect_emotion(sample_frame)
            assert emotion == "NO FACE"

    def test_detect_emotion_encoding_failure(self):
        """Test emotion detection with invalid frame that fails encoding"""
        # Create an invalid frame that will fail encoding
        invalid_frame = np.array([])

        # cv2.imencode raises cv2.error for invalid frames
        with pytest.raises((ValueError, cv2.error)):
            detect_emotion(invalid_frame)

    def test_detect_emotion_aws_error(self, sample_frame):
        """Test emotion detection when AWS service fails"""
        with patch("logic.facial_analysis.client.detect_faces", side_effect=Exception("AWS Service Error")):
            with pytest.raises(Exception, match="AWS Service Error"):
                detect_emotion(sample_frame)

    def test_detect_emotion_aws_throttling(self, sample_frame):
        """Test emotion detection when AWS throttles requests"""
        from botocore.exceptions import ClientError

        error_response = {
            'Error': {
                'Code': 'ProvisionedThroughputExceededException',
                'Message': 'Rate exceeded'
            }
        }

        with patch("logic.facial_analysis.client.detect_faces",
                   side_effect=ClientError(error_response, 'DetectFaces')):
            with pytest.raises(ClientError):
                detect_emotion(sample_frame)

    def test_detect_emotion_invalid_credentials(self, sample_frame):
        """Test emotion detection with invalid AWS credentials"""
        from botocore.exceptions import NoCredentialsError

        with patch("logic.facial_analysis.client.detect_faces",
                   side_effect=NoCredentialsError()):
            with pytest.raises(NoCredentialsError):
                detect_emotion(sample_frame)

    def test_detect_emotion_all_supported_emotions(self, sample_frame):
        """Test detection of all supported AWS Rekognition emotions"""
        supported_emotions = [
            "HAPPY", "SAD", "ANGRY", "CONFUSED",
            "DISGUSTED", "SURPRISED", "CALM", "FEAR"
        ]

        for emotion_type in supported_emotions:
            mock_response = {
                "FaceDetails": [
                    {
                        "Emotions": [
                            {"Type": emotion_type, "Confidence": 99.0}
                        ]
                    }
                ]
            }

            with patch("logic.facial_analysis.client.detect_faces", return_value=mock_response):
                detected = detect_emotion(sample_frame)
                assert detected == emotion_type

    def test_detect_emotion_frame_encoding(self, sample_frame):
        """Test that frame is properly encoded to JPEG bytes"""
        mock_response = {
            "FaceDetails": [
                {"Emotions": [{"Type": "HAPPY", "Confidence": 95.0}]}
            ]
        }

        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_response) as mock_detect:
            detect_emotion(sample_frame)

            # Verify detect_faces was called
            assert mock_detect.called
            call_args = mock_detect.call_args

            # Verify Image parameter with Bytes was passed
            assert "Image" in call_args[1]
            assert "Bytes" in call_args[1]["Image"]
            assert isinstance(call_args[1]["Image"]["Bytes"], bytes)

            # Verify EMOTIONS attribute was requested
            assert "Attributes" in call_args[1]
            assert "EMOTIONS" in call_args[1]["Attributes"]

    def test_detect_emotion_with_real_colored_frame(self):
        """Test emotion detection with a realistic colored frame"""
        # Create a more realistic frame with colors
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        # Add a "face-like" oval shape in skin tone
        cv2.ellipse(frame, (100, 100), (50, 70), 0, 0, 360, (180, 150, 120), -1)
        # Add "eyes"
        cv2.circle(frame, (85, 90), 8, (50, 50, 50), -1)
        cv2.circle(frame, (115, 90), 8, (50, 50, 50), -1)
        # Add "mouth"
        cv2.ellipse(frame, (100, 120), (20, 10), 0, 0, 180, (100, 50, 50), -1)

        mock_response = {
            "FaceDetails": [
                {"Emotions": [{"Type": "CALM", "Confidence": 87.5}]}
            ]
        }

        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_response):
            emotion = detect_emotion(frame)
            assert emotion == "CALM"

    def test_detect_emotion_empty_emotions_list(self, sample_frame):
        """Test emotion detection when face is detected but no emotions returned"""
        mock_response = {
            "FaceDetails": [
                {"Emotions": []}
            ]
        }

        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_response):
            # This should raise an IndexError since we try to access Emotions[0]
            with pytest.raises(IndexError):
                detect_emotion(sample_frame)

    def test_detect_emotion_multiple_faces(self, sample_frame):
        """Test that only the first face's emotion is returned when multiple faces detected"""
        mock_response = {
            "FaceDetails": [
                {"Emotions": [{"Type": "HAPPY", "Confidence": 95.0}]},
                {"Emotions": [{"Type": "SAD", "Confidence": 90.0}]}
            ]
        }

        with patch("logic.facial_analysis.client.detect_faces", return_value=mock_response):
            emotion = detect_emotion(sample_frame)
            # Should return first face's emotion
            assert emotion == "HAPPY"


@pytest.mark.integration
@pytest.mark.aws
class TestDetectEmotionIntegration:
    """Integration tests for detect_emotion (requires AWS credentials)"""

    @pytest.mark.skip(reason="Requires AWS credentials and incurs API costs")
    def test_detect_emotion_real_aws_call(self):
        """Test emotion detection with real AWS Rekognition call"""
        # Create a simple test frame
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)

        # This would make a real API call
        emotion = detect_emotion(frame)

        # Should return either an emotion or "NO FACE"
        valid_emotions = [
            "HAPPY", "SAD", "ANGRY", "CONFUSED",
            "DISGUSTED", "SURPRISED", "CALM", "FEAR", "NO FACE"
        ]
        assert emotion in valid_emotions
