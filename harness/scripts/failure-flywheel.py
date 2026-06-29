#!/usr/bin/env python3
"""failure-flywheel — thin shim → flywheel.py --kind failure (merged 2026-06-29; the two flywheels
shared 11/11 functions). Kept as an entry point for the /failure-flywheel skill + existing CLI.
All logic lives in flywheel.py; the failure adapter is harness/failure-flywheel.config.yaml."""
import os
import sys

_FLYWHEEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flywheel.py")
os.execv(sys.executable, [sys.executable, _FLYWHEEL, "--kind", "failure", *sys.argv[1:]])
