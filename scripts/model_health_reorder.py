#!/usr/bin/env python3
"""Wrapper: run model_health.py with the 'reorder' argument for fallback tuning."""
import subprocess, sys, os

script = os.path.join(os.path.dirname(__file__), "model_health.py")
result = subprocess.run([sys.executable, script, "reorder"], capture_output=True, text=True, timeout=300)
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
