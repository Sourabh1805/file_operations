# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from api.services.filesystem import FileSystemService
from api.main import app 

@pytest.fixture(autouse=True)
def reset_filesystem():
    """Reset filesystem state before each test"""
    service = FileSystemService()
    service.drives.clear()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def service():
    return FileSystemService()