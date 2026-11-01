These UI tests describe the former profile dictation interface. Profile dictation is temporarily disabled at the user's request. They are retained as historical coverage and are not part of the current test run. Re-enabling that feature requires adapting it and these tests to the three birth-date controls.

Current coverage: `tests/profile_controls_smoke.py` checks the new birth-date UI and the absence of profile dictation. `tests/voice_smoke.py` and `tests/capture_smoke.py` cover active diary dictation.
