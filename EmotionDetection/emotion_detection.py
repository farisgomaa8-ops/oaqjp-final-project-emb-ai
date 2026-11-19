"""Detect emotions through the Watson NLP service supplied by Skills Network."""

import json
import math

import requests


EMOTION_URL = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
EMOTION_HEADERS = {
    "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
}
EMOTION_NAMES = ("anger", "disgust", "fear", "joy", "sadness")
REQUEST_TIMEOUT_SECONDS = 30


class EmotionServiceError(RuntimeError):
    """Signal a transport, HTTP, or response-format failure from Watson NLP."""


def emotion_detector(text_to_analyze):
    """Return five emotion scores and the highest-scoring emotion.

    Watson HTTP 400 responses produce the six-key ``None`` result required by
    the lab. Service failures are raised separately, so an unavailable service
    cannot be mistaken for invalid text. No scores are estimated locally.
    """
    if not isinstance(text_to_analyze, str):
        raise TypeError("text_to_analyze must be a string")

    try:
        response = requests.post(
            EMOTION_URL,
            headers=EMOTION_HEADERS,
            json={"raw_document": {"text": text_to_analyze}},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as error:
        raise EmotionServiceError("Could not reach the Watson emotion service") from error

    if response.status_code == 400:
        return dict.fromkeys((*EMOTION_NAMES, "dominant_emotion"))
    if response.status_code != 200:
        raise EmotionServiceError(
            f"Watson emotion service returned HTTP {response.status_code}"
        )

    try:
        response_data = json.loads(response.text)
        raw_scores = response_data["emotionPredictions"][0]["emotion"]
        scores = {name: raw_scores[name] for name in EMOTION_NAMES}
        if any(
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(score)
            for score in scores.values()
        ):
            raise ValueError("Emotion scores must be finite numbers")
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise EmotionServiceError("Watson returned an invalid emotion response") from error

    scores["dominant_emotion"] = max(scores, key=scores.get)
    return scores
