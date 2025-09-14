"""
Test configuration and setup for backend tests.
"""

import os
import sys
from pathlib import Path

# Set test environment before importing any modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-schema-tests")

# Add src directory to Python path for imports
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Pytest configuration
pytest_plugins = []

# Test markers configuration is in pyproject.toml