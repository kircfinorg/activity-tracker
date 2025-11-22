"""
Pytest configuration and fixtures for tests

This file sets up mocking for Firebase services to allow tests to run
without requiring actual Firebase credentials.
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Firebase Admin SDK at module level before any imports
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()
sys.modules['firebase_admin.auth'] = MagicMock()


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest settings"""
    config.option.asyncio_default_fixture_loop_scope = "function"
