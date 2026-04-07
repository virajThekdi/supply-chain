#!/usr/bin/env python
"""Quick test script to verify dependencies"""

import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}\n")

# Test imports
dependencies = {
    "fastapi": "FastAPI web framework",
    "uvicorn": "ASGI server",
    "pydantic": "Data validation",
    "pandas": "Data processing",
    "numpy": "Numerical computing",
}

print("Checking dependencies:\n")
for package, description in dependencies.items():
    try:
        __import__(package)
        print(f"✓ {package:<20} - {description}")
    except ImportError as e:
        print(f"✗ {package:<20} - NOT INSTALLED ({e})")

# Test app import
print("\n\nTesting app imports:")
try:
    from app.main import app
    print("✓ FastAPI app loaded successfully")
    print(f"  Routes: {len(app.routes)}")
except Exception as e:
    print(f"✗ Failed to load app: {e}")
    import traceback
    traceback.print_exc()
