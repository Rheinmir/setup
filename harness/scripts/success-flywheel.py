#!/usr/bin/env python3
"""success-flywheel — thin shim → flywheel.py --kind success (merged 2026-06-29). Entry point for
existing CLI / fdk-gate. Logic in flywheel.py; success adapter = harness/success-flywheel.config.yaml."""
import os
import sys

_FLYWHEEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flywheel.py")
os.execv(sys.executable, [sys.executable, _FLYWHEEL, "--kind", "success", *sys.argv[1:]])
