# tests/integration/test_filesystem_routes.py
from fastapi.testclient import TestClient
import pytest

def test_full_lifecycle(client):
    # Create drive
    response = client.post("api/v1/drives/mainfull")
    assert response.status_code == 200
    assert response.json()["path"] == "/mainfull/"
    
    # Create folder
    response = client.post("api/v1/folders/mainfull/documents")
    assert response.status_code == 200

    
    # Create file
    response = client.post("api/v1/files/mainfull/documents/report.txt")
    assert response.status_code == 200
    assert response.json()["path"] == "/mainfull/documents/report.txt"

    # add content to file
    response = client.put("api/v1/files/mainfull/documents/report.txt/content?content=hiiii")
    assert response.status_code == 200

     # Verify structure
    response = client.get("api/v1/structure")
    assert any(e["path"] == "/mainfull/documents/report.txt" 
               for e in response.json()[0]["children"][0]["children"])
    
    # Create folder 2
    response = client.post("api/v1/folders/mainfull/documents2")
    assert response.status_code == 200
    
    # Move file
    response = client.put("/api/v1/entities/mainfull/documents/report.txt/move/mainfull/documents2/report.txt")
    # /api/v1/entities/Drive1/folder1/file1.txt%20/move/Drive1/folder2/file1.txt
    assert response.status_code == 200
    
    # Cleanup
    response = client.delete("api/v1/entities/mainfull")
    assert response.status_code == 200

def test_error_handling(client):
    
    # Move to invalid location
    client.post("api/v1/drives/move_test")
    response = client.put("api/v1/entities/move_test/file.txt/move/invalid/path")
    assert response.status_code == 400

def test_direct_drive_files(client):
    # Create file directly in drive root
    client.post("api/v1/drives/root_drive")
    response = client.post("api/v1/files/root_drive/direct_file.txt")
    assert response.status_code == 200
    assert response.json()["path"] == "/root_drive/direct_file.txt"
    
    # Verify through structure endpoint
    response = client.get("api/v1/entity/root_drive/direct_file.txt")
    assert response.status_code == 200
    assert response.json()["type"] == "file"

def test_edge_cases(client):
    # Empty path
    response = client.post("api/v1/folders/")
    assert response.status_code == 400
    
    # Long drive names
    long_name = "a" * 255
    response =  client.post(f"api/v1/drives/{long_name}")
    # response = client.post(f"/files/{long_name}/test.txt")
    assert response.status_code == 200
    