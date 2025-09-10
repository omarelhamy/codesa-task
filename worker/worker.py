import os
import time
import json
import requests
import signal
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Task, SessionLocal

class VirusTotalScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {"x-apikey": api_key}
    
    def upload_file(self, file_path):
        url = f"{self.base_url}/files"
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=self.headers, files=files)
        
        if response.status_code == 200:
            return response.json()["data"]["id"]
        elif response.status_code == 429:
            raise Exception("VirusTotal API quota exceeded")
        else:
            raise Exception(f"Upload failed: {response.text}")
    
    def get_analysis(self, file_id):
        url = f"{self.base_url}/analyses/{file_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Analysis failed: {response.text}")
    
    def scan_file(self, file_path):
        try:
            file_id = self.upload_file(file_path)
            print(f"File uploaded: {file_id}")
            
            while True:
                analysis = self.get_analysis(file_id)
                status = analysis["data"]["attributes"]["status"]
                
                if status == "completed":
                    return analysis
                elif status == "queued":
                    print("Scan queued")
                    time.sleep(15)
                else:
                    print(f"Status: {status}")
                    time.sleep(10)
        
        except Exception as e:
            raise Exception(f"VirusTotal scan failed: {str(e)}")

def process_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        db.close()
        return
    
    try:
        task.status = "RUNNING"
        db.commit()
        
        uploads_dir = os.getenv("UPLOADS_DIR", "../uploads")
        file_path = f"{uploads_dir}/{task_id}_{task.filename}"
        if not os.path.exists(file_path):
            raise Exception("File not found")
        
        if not file_path.endswith('.pdf'):
            raise Exception("File is not a PDF")
        
        api_key = os.getenv("VIRUSTOTAL_API_KEY")
        if not api_key:
            raise Exception("VirusTotal API key not configured")
        
        scanner = VirusTotalScanner(api_key)
        report = scanner.scan_file(file_path)
        
        reports_dir = os.getenv("REPORTS_DIR", "../reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_path = f"{reports_dir}/{task_id}_report.json"
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        task.status = "COMPLETED"
        task.report_path = report_path
        task.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"Task completed: {task_id}")
        
    except Exception as e:
        task.status = "FAILED"
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        db.commit()
        print(f"Task failed: {task_id}")
    
    finally:
        db.close()

def signal_handler(sig, frame):
    print("Shutting down")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    print("Worker started")
    
    while True:
        try:
            db = SessionLocal()
            pending_tasks = db.query(Task).filter(Task.status == "PENDING").all()
            db.close()
            
            for task in pending_tasks:
                process_task(task.task_id)
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
