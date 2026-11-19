"""Task 2 checkpoint: return the raw Watson emotion service response text."""

import requests


def emotion_detector(text_to_analyze):
    """Send the input to Watson NLP and return its unformatted response."""
    url = (
        "https://sn-watson-emotion.labs.skills.network/v1/"
        "watson.runtime.nlp.v1/NlpService/EmotionPredict"
    )
    headers = {
        "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
    }
    response = requests.post(
        url,
        headers=headers,
        json={"raw_document": {"text": text_to_analyze}},
        timeout=30,
    )
    return response.text
