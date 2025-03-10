# tests/unit/services/test_filesystem.py
from api.services.filesystem import FileSystemService
from api.models.entities import Drive, Folder, File
import pytest

def test_drive_operations(service):
    # Test creation
    drive = service.create_drive("data")
    assert drive.name == "data"
    
    # Test duplicate drive
    with pytest.raises(ValueError):
        service.create_drive("data")

def test_file_operations(service):
    drive = service.create_drive("main")
    file = service.create_file("log.txt", drive)
    assert isinstance(file, File)
    assert file.path() == "/main/log.txt"

    # Test file in folder
    folder = service.create_folder("logs", drive)
    nested_file = service.create_file("error.log", folder)
    assert nested_file.path() == "/main/logs/error.log"

def test_path_resolution(service):
    service.create_drive("system")
    drive = service.resolve_path("system")
    assert isinstance(drive, Drive)
    
    # Test nested resolution
    folder = service.create_folder("temp", drive)
    file = service.create_file("dummy", folder)
    assert service.resolve_path("system/temp/dummy") == file

def test_move_operations(service):
    drive = service.create_drive("data")
    src = service.create_folder("source", drive)
    file = service.create_file("data.txt", src)
    
    dest = service.create_folder("dest", drive)
    service.move_entity(file, dest, "moved.txt")
    
    assert service.resolve_path("data/dest/moved.txt") == file
    assert file.name == "moved.txt"

def test_invalid_moves(service):
    drive = service.create_drive("main")
    folder = service.create_folder("docs", drive)
    
    with pytest.raises(ValueError):
        service.move_entity(folder, folder, "invalid")

def test_delete_operations(service):
    drive = service.create_drive("temp")
    service.delete_entity(drive)
    assert "temp" not in service.drives