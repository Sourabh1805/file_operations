# tests/unit/models/test_entities.py
from datetime import datetime
from api.models.entities import Drive, Folder, File
import pytest

def test_drive_creation():
    drive = Drive("main")
    assert drive.name == "main"
    assert drive.path() == "/main/"
    assert isinstance(drive.created_at, datetime)
    assert len(drive.children) == 0

def test_folder_hierarchy():
    drive = Drive("main")
    folder = Folder("docs")
    drive.add_child(folder)
    
    assert folder.path() == "/main/docs"
    assert folder.parent == drive
    assert "docs" in drive.children

