"""Serve the lab's emotion detection page and its Watson-backed text endpoint."""

from flask import Flask, render_template, request

from EmotionDetection import EmotionServiceError, emotion_detector


app = Flask(__name__)


@app.route("/")
def render_index_page():
    """Render the HTML template supplied by the official starter repository."""
    return render_template("index.html")


@app.route("/emotionDetector")
def detect_emotion():
    """Analyze the query text and return the message expected by the starter UI."""
    text_to_analyze = request.args.get("textToAnalyze", "")
    try:
        result = emotion_detector(text_to_analyze)
    except EmotionServiceError:
        return "Emotion analysis is temporarily unavailable. Please try again later.", 503

    if result["dominant_emotion"] is None:
        # The unmodified starter JavaScript only displays HTTP 200 responses.
        return "Invalid text! Please try again!"

    return (
        f"For the given statement, the system response is 'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, 'fear': {result['fear']}, "
        f"'joy': {result['joy']} and 'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
