import pytest
import os
import tempfile
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test if the API is accessible"""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_task_invalid_file():
    """Test creating task with non-PDF file"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(b"test content")
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, "rb") as f:
            response = client.post(
                "/api/tasks",
                data={"description": "Test task"},
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]
    finally:
        os.unlink(tmp_file_path)

def test_create_task_missing_file():
    """Test creating task without file"""
    response = client.post(
        "/api/tasks",
        data={"description": "Test task"}
    )
    assert response.status_code == 422  # Validation error

def test_create_task_missing_description():
    """Test creating task without description"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"fake pdf content")
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, "rb") as f:
            response = client.post(
                "/api/tasks",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 422  # Validation error
    finally:
        os.unlink(tmp_file_path)

def test_get_nonexistent_task():
    """Test getting a task that doesn't exist"""
    response = client.get("/api/tasks/nonexistent-id")
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

def test_get_nonexistent_report():
    """Test getting a report that doesn't exist"""
    response = client.get("/api/reports/nonexistent-id")
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
