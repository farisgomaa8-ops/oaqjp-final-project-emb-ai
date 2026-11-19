# Final project

Emotion detection application for the IBM / Skills Network Python and Flask lab.

## Project layout

- `EmotionDetection/emotion_detection.py`: sends text to Watson NLP, formats five
  scores, selects the dominant emotion, and handles upstream HTTP 400 responses.
- `EmotionDetection/__init__.py`: exposes the reusable package interface.
- `server.py`: serves the starter page and the `GET /emotionDetector` endpoint.
- `test_emotion_detection.py`: the five required tests against the **live** API.
- `tests/test_offline.py`: independent tests with **synthetic mocked** responses.
- `templates/index.html`: the unchanged official starter template.
- `static/mywebscript.js`: the starter script with query encoding, local variable
  declarations, text-only rendering, and visible service-error handling added.

Official starter: <https://github.com/ibm-developer-skills-network/oaqjp-final-project-emb-ai>

## Set up and run

Use Python 3.9 or newer in the provided Skills Network lab or another environment
that can reach the lab's Watson endpoint.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

Open `http://localhost:5000`. In the hosted Skills Network lab, use its application
launcher for port 5000. Flask listens on port 5000 with debugging disabled.

The browser sends `GET /emotionDetector?textToAnalyze=...`. The server returns the
five scores and dominant emotion in the exact prose required by the lab.
The script URL-encodes the input so characters such as `&`, `+`, and `#` remain
part of the analyzed text. It renders responses as text rather than HTML, and
keeps the original endpoint, input ID, result ID, and button handler.

## Watson API contract

- URL: `https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict`
- Method: `POST`
- Header: `grpc-metadata-mm-model-id: emotion_aggregated-workflow_lang_en_stock`
- JSON body: `{"raw_document": {"text": "text to analyze"}}`
- Scores: `emotionPredictions[0].emotion`, containing `anger`, `disgust`, `fear`,
  `joy`, and `sadness`.
- Python return value: those five scores plus `dominant_emotion`, the name with
  the highest score.

The detector parses the service's response text with `json.loads`. It never
generates fallback scores. Only finite numeric scores are accepted.

An upstream HTTP 400 produces all six keys with `None` values. The Flask endpoint
then returns `Invalid text! Please try again!` with HTTP 200, preserving the lab's
invalid-input message and the original starter's response contract.

Connection failures, timeouts, other HTTP errors, and malformed responses raise
`EmotionServiceError`. Flask translates these into HTTP 503. They are not treated
as blank input. The updated script displays that service-availability message;
other unsuccessful requests show a generic error instead of leaving an old result.

## Verification commands

Offline tests make **no network calls** and use explicitly synthetic fixtures:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

Run the required live API tests separately:

```sh
python -m unittest test_emotion_detection -v
```

These check the exact lab statements for joy, anger, disgust, sadness, and fear.
A service connection failure causes a test error; it is not skipped or presented
as a pass.

Check source quality:

```sh
python -m pylint server.py
```

Verified in the Skills Network cloud lab with Python 3.10.12 after installing
`requirements.txt`: **16 offline tests passed in 0.022 seconds**, and
**pylint rated `server.py` 10.00/10**. The **five required live Watson tests also
passed in 0.594 seconds**. Browser checks confirmed a valid statement returns
`joy` and blank input displays `Invalid text! Please try again!`.
See `VERIFICATION.md` for the exact scope of the checks.

## Evidence

Browser evidence is available in `evidence/6b_deployment_test.png` and
`evidence/7c_error_handling_interface.png`. These are format-only conversions of
the authentic screenshots. Actual cloud outputs for tasks 2, 3, 4, and 8 are
supplied as text files in `evidence/`. The verified live unit-test result has a
clearly labeled text transcription in `evidence/5b_unit_testing_result.txt`.
The source files and captured evidence cover the lab project tasks.
Offline fixtures are kept separate from live prediction evidence.

The final package contains the formatted implementation. The earlier raw-response
version is supplied separately in `evidence/task2/emotion_detection.py`; it is
separate from the final formatted package. Its live output is recorded in
`evidence/2b_application_creation.txt`.


The official starter's license is retained in `LICENSE`.
