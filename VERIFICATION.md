# Verification status

## Completed checks

The application dependencies were installed from `requirements.txt` in the
Skills Network cloud lab running Python 3.10.12.

| Check | Actual result |
| --- | --- |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | 16 tests passed in 0.022 seconds |
| `python3 -m unittest test_emotion_detection -v` | All five required live Watson tests passed in 0.594 seconds; `OK` |
| `python -m pylint server.py` | Rated 10.00/10 |
| Python syntax compilation | All five Python files passed under the local Python 3.9 interpreter |
| JavaScript syntax and targeted checks | Passed query encoding, local-variable, HTTP 200/503 response, and generic-error checks |
| Valid-input browser check | `I think I am having fun` produced dominant emotion `joy` with live scores displayed below |
| Blank-input browser check | Displayed exactly `Invalid text! Please try again!` |
| Task 2 raw response | Live output for `I love this new technology.` recorded in `evidence/2b_application_creation.txt` |
| Task 3 formatted output | Live output for `I am so happy I am doing this` returned dominant emotion `joy`; `evidence/3b_formatted_output_test.txt` |
| Task 4 package import and call | Live output for `I hate working long hours` returned dominant emotion `anger`; `evidence/4b_packaging_test.txt` |

The offline tests use Flask's test client and mocked Watson responses. They check
the application logic without making network calls. JavaScript checks used a
small isolated test harness, not a browser.

The live suite called Watson for the five lab statements and verified joy, anger,
disgust, sadness, and fear. A clearly labeled transcription of the verified run
is supplied as `evidence/5b_unit_testing_result.txt`. The authentic terminal
screenshot is retained locally and excluded from the deliverable package.

The task 2, 3, and 4 files contain genuine Python 3 interactive sessions
downloaded from the cloud lab. Only the recording tool's start/end metadata
and CRLF line formatting were removed; the Python banner, `>>>` imports,
function calls, return values, and `exit()` remain unchanged. The raw session
recordings are retained separately. `evidence/8b_static_code_analysis.txt`
was also downloaded from the lab and records the actual 10.00/10 pylint result. The text files preserve the captured outputs.

## Browser evidence

For `I think I am having fun`, the actual displayed scores were:

| Field | Live value |
| --- | --- |
| anger | 0.029103195 |
| disgust | 0.0067921067 |
| fear | 0.027528232 |
| joy | 0.876574 |
| sadness | 0.06151191 |
| dominant_emotion | joy |

The valid-input screenshot is `evidence/6b_deployment_test.png`. The blank-input
screenshot is `evidence/7c_error_handling_interface.png` and shows the exact
required invalid-text message.

PNG copies were converted from the authentic JPEG screenshots without cropping
or content changes. The original JPEGs are retained locally. The two included
browser screenshots preserve their original dimensions of 701 × 852.

The application, live API calls, required unit tests, blank-input handling,
browser behavior, and static analysis have been verified as described above.

Mocked responses in `tests/test_offline.py` are explicitly synthetic and are not
evidence of real Watson predictions. Run the live and browser checks described
in README.md when revalidating the project; scores can differ between service runs.
