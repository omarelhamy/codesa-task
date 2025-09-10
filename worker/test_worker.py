import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from worker import VirusTotalScanner, process_task

def test_virustotal_scanner_init():
    """Test VirusTotal scanner initialization"""
    scanner = VirusTotalScanner("test-api-key")
    assert scanner.api_key == "test-api-key"
    assert scanner.base_url == "https://www.virustotal.com/api/v3"
    assert scanner.headers == {"x-apikey": "test-api-key"}

@patch('worker.requests.post')
def test_virustotal_upload_file_success(mock_post):
    """Test successful file upload to VirusTotal"""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"id": "test-file-id"}}
    mock_post.return_value = mock_response
    
    scanner = VirusTotalScanner("test-api-key")
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"fake pdf content")
        tmp_file_path = tmp_file.name
    
    try:
        file_id = scanner.upload_file(tmp_file_path)
        assert file_id == "test-file-id"
        mock_post.assert_called_once()
    finally:
        os.unlink(tmp_file_path)

@patch('worker.requests.post')
def test_virustotal_upload_file_quota_exceeded(mock_post):
    """Test VirusTotal quota exceeded error"""
    # Mock quota exceeded response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_post.return_value = mock_response
    
    scanner = VirusTotalScanner("test-api-key")
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"fake pdf content")
        tmp_file_path = tmp_file.name
    
    try:
        with pytest.raises(Exception) as exc_info:
            scanner.upload_file(tmp_file_path)
        assert "VirusTotal API quota exceeded" in str(exc_info.value)
    finally:
        os.unlink(tmp_file_path)

@patch('worker.requests.get')
def test_virustotal_get_analysis_success(mock_get):
    """Test successful analysis retrieval"""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "attributes": {
                "status": "completed",
                "stats": {
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 0,
                    "harmless": 1
                }
            }
        }
    }
    mock_get.return_value = mock_response
    
    scanner = VirusTotalScanner("test-api-key")
    result = scanner.get_analysis("test-file-id")
    
    assert result["data"]["attributes"]["status"] == "completed"
    mock_get.assert_called_once()

def test_process_task_no_api_key():
    """Test process_task without API key"""
    with patch.dict(os.environ, {}, clear=True):
        with patch('worker.SessionLocal') as mock_session:
            with patch('worker.os.path.exists', return_value=True):
                mock_db = Mock()
                mock_session.return_value = mock_db
                
                mock_task = Mock()
                mock_task.task_id = "test-task-id"
                mock_task.filename = "test.pdf"
                mock_task.status = "PENDING"
                mock_db.query.return_value.filter.return_value.first.return_value = mock_task
                
                process_task("test-task-id")
                
                # Should update task status to FAILED
                assert mock_task.status == "FAILED"
                assert "VirusTotal API key not configured" in mock_task.error_message

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
