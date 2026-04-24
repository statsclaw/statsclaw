"""Shared fixtures for paper-ingestion script tests."""

import sys
from pathlib import Path

# Add scripts directory to sys.path so we can import extract_elements
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
