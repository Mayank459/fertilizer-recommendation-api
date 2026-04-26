"""
Startup guard: trains models if artefacts are missing.
Run this instead of train.py directly on Render if you want lazy training.
Normally, train.py is called by Render's buildCommand.
"""
import os
import sys

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
REQUIRED = ["preprocessor.pkl", "npk_regressor.pkl", "risk_classifier.pkl"]

missing = [f for f in REQUIRED if not os.path.exists(os.path.join(MODELS_DIR, f))]

if missing:
    print(f"[STARTUP] Missing model artefacts: {missing}. Running train.py ...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=os.path.dirname(__file__),
        capture_output=False,
    )
    if result.returncode != 0:
        print("[STARTUP] Training failed! API may not work correctly.")
        sys.exit(1)
    print("[STARTUP] Training complete.")
else:
    print("[STARTUP] All model artefacts present. Skipping training.")
