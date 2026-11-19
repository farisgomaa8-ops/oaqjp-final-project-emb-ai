"""Deterministic checks with synthetic responses; these do not verify live Watson."""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import requests

from EmotionDetection import EmotionServiceError, emotion_detector
from EmotionDetection.emotion_detection import EMOTION_HEADERS, EMOTION_URL
from server import app


# Deliberately synthetic scores for testing parsing and formatting only.
SYNTHETIC_SCORES = {
    "anger": 0.1,
    "disgust": 0.2,
    "fear": 0.3,
    "joy": 0.9,
    "sadness": 0.4,
}


def response_with_scores(scores=None):
    """Build a synthetic successful service response in the Watson schema."""
    return SimpleNamespace(
        status_code=200,
        text=json.dumps(
            {"emotionPredictions": [{"emotion": scores or SYNTHETIC_SCORES}]}
        ),
    )


class EmotionDetectorOfflineTests(unittest.TestCase):
    """Check the outbound contract, score parsing, and distinct failure cases."""

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_request_contract_and_success(self, post):
        """Use the required endpoint, model header, body, timeout, and return shape."""
        post.return_value = response_with_scores()
        result = emotion_detector("example text")
        post.assert_called_once_with(
            EMOTION_URL,
            headers=EMOTION_HEADERS,
            json={"raw_document": {"text": "example text"}},
            timeout=30,
        )
        self.assertEqual(result, dict(SYNTHETIC_SCORES, dominant_emotion="joy"))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_highest_score_determines_dominant_emotion(self, post):
        """The dominant emotion must follow the highest score, not a fixed label."""
        scores = dict(SYNTHETIC_SCORES, anger=0.99)
        post.return_value = response_with_scores(scores)
        self.assertEqual(emotion_detector("example")["dominant_emotion"], "anger")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_http_400_returns_all_none(self, post):
        """Invalid-input responses return every required key, even with non-JSON body."""
        post.return_value = SimpleNamespace(status_code=400, text="Bad request")
        self.assertEqual(
            emotion_detector(""),
            dict.fromkeys((*SYNTHETIC_SCORES, "dominant_emotion")),
        )

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_service_http_error_is_not_invalid_text(self, post):
        """A service HTTP error must not become a successful six-None result."""
        post.return_value = SimpleNamespace(status_code=503, text="Unavailable")
        with self.assertRaisesRegex(EmotionServiceError, "HTTP 503"):
            emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_network_failure_is_not_invalid_text(self, post):
        """Connection failures stay distinguishable from Watson input rejection."""
        post.side_effect = requests.ConnectionError("offline test")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_timeout_is_not_invalid_text(self, post):
        """Request timeouts should be reported as service failures."""
        post.side_effect = requests.Timeout("offline test")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_invalid_json(self, post):
        """Reject malformed service JSON rather than inventing emotion scores."""
        post.return_value = SimpleNamespace(status_code=200, text="not json")
        with self.assertRaises(EmotionServiceError):
            emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_missing_response_data(self, post):
        """Reject incomplete response structures."""
        for payload in ({}, {"emotionPredictions": []}, {"emotionPredictions": [{}]}):
            with self.subTest(payload=payload):
                post.return_value = SimpleNamespace(status_code=200, text=json.dumps(payload))
                with self.assertRaises(EmotionServiceError):
                    emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_invalid_scores(self, post):
        """Reject text, booleans, and non-finite numbers in score fields."""
        for score in ("<script>alert(1)</script>", True, float("nan"), float("inf"), None):
            with self.subTest(score=score):
                post.return_value = response_with_scores(dict(SYNTHETIC_SCORES, joy=score))
                with self.assertRaises(EmotionServiceError):
                    emotion_detector("example")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_non_string_input_rejected_before_network(self, post):
        """The Python interface accepts strings only."""
        with self.assertRaises(TypeError):
            emotion_detector(None)
        post.assert_not_called()


class FlaskOfflineTests(unittest.TestCase):
    """Check the Flask response contract without calling the network."""

    def setUp(self):
        """Create an isolated Flask test client."""
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_index_renders_starter_page(self):
        """The home route must serve the supplied template."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NLP - Emotion Detection", response.data)

    @patch("server.emotion_detector")
    def test_success_prose_and_query_parameter(self, detector):
        """Keep the exact lab prose and starter query parameter."""
        detector.return_value = dict(SYNTHETIC_SCORES, dominant_emotion="joy")
        response = self.client.get("/emotionDetector", query_string={"textToAnalyze": "test"})
        detector.assert_called_once_with("test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True),
            "For the given statement, the system response is 'anger': 0.1, "
            "'disgust': 0.2, 'fear': 0.3, 'joy': 0.9 and 'sadness': 0.4. "
            "The dominant emotion is joy.",
        )

    @patch("server.emotion_detector")
    def test_invalid_input_message_is_visible_to_starter(self, detector):
        """Return HTTP 200 for the starter JS to render the invalid-input message."""
        detector.return_value = dict.fromkeys((*SYNTHETIC_SCORES, "dominant_emotion"))
        response = self.client.get("/emotionDetector", query_string={"textToAnalyze": ""})
        detector.assert_called_once_with("")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Invalid text! Please try again!")

    @patch("server.emotion_detector")
    def test_missing_query_becomes_empty_text(self, detector):
        """A missing query uses the same invalid-input path as an empty input."""
        detector.return_value = dict.fromkeys((*SYNTHETIC_SCORES, "dominant_emotion"))
        self.client.get("/emotionDetector")
        detector.assert_called_once_with("")

    @patch("server.emotion_detector")
    def test_service_failure_is_separate(self, detector):
        """Return HTTP 503 rather than calling a network failure invalid text."""
        detector.side_effect = EmotionServiceError("internal failure detail")
        response = self.client.get("/emotionDetector", query_string={"textToAnalyze": "test"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_data(as_text=True),
            "Emotion analysis is temporarily unavailable. Please try again later.",
        )

    @patch("server.emotion_detector")
    def test_input_text_is_not_reflected_in_output(self, detector):
        """Do not put user-controlled markup into the starter's innerHTML target."""
        detector.return_value = dict(SYNTHETIC_SCORES, dominant_emotion="joy")
        response = self.client.get(
            "/emotionDetector",
            query_string={"textToAnalyze": "<script>alert(1)</script>"},
        )
        self.assertNotIn(b"<script>", response.data)


if __name__ == "__main__":
    unittest.main()
