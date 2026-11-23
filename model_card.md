# Model Card: PawPal+ Reliability System

## Overview
The system adds a validation layer (`validation.py`), logging, and an evaluation harness
(`evaluate.py`) to my Module 2 PawPal+ scheduler. The harness runs 20 checks and
reports 20/20 passing.

## Limitations and Biases
Conflict detection only flags exact date-and-time matches, so overlapping durations are
missed. Times are 24-hour HH:MM only, with no time zones. Data lives in Streamlit session
state and is lost when the app restarts. The harness tests the logic and guardrail layer
but not the Streamlit UI itself, and its random test uses a fixed seed, so it covers one
set of inputs rather than many. The 80-character description limit is an arbitrary choice.

## Could the AI Be Misused, and How Would I Prevent It?
Misuse risk is low. The main concern is someone relying on the schedule for real
medication timing, so the app should say it is a reminder tool, not medical advice. If
persistence were added, owner and pet data would need to be stored privately.

## What Surprised Me While Testing Reliability
My new `test_guardrails.py` file was accidentally created inside `__pycache__`, so
pytest quietly ran only the original 9 tests instead of 14. Nothing failed, which made
it easy to miss, and I only noticed because the test count didn't change. I also found
a stray line reading `python` at the top of `app.py` that would have crashed the app.

## Collaboration with AI
- **How I used AI:** I used Claude in a chat window to plan the reliability layer, draft
  `validation.py`, `evaluate.py`, and the guardrail tests, and to diagnose problems when
  pytest and the editor showed unexpected results.
- **Suggestion I accepted (and how I verified it):** Putting validation in a separate
  `validation.py` that `app.py` calls. I verified it by running `python -m pytest`
  (14 passed), running `python evaluate.py` (20/20), and checking `pawpal.log` after
  trying a valid and an empty task in the app.
- **Suggestion I rejected or revised (and why):** The AI's first plan assumed a
  `pawpal_system.py` with a different API than mine and proposed replacing it. I showed
  it my real `app.py`, and it changed the plan to new separate files that only use
  methods my code already had, so I didn't overwrite working Module 2 code.