from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Task
from database import SessionLocal, create_tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

@app.post("/api/tasks")
async def create_task(
    description: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    task_id = str(uuid.uuid4())
    
    uploads_dir = os.getenv("UPLOADS_DIR", "../uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = f"{uploads_dir}/{task_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    db = SessionLocal()
    task = Task(
        task_id=task_id,
        description=description,
        filename=file.filename,
        status="PENDING"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()
    
    return {"task_id": task_id, "status": "PENDING"}

@app.get("/api/tasks")
async def get_tasks():
    db = SessionLocal()
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    db.close()
    
    return [
        {
            "id": task.task_id,
            "description": task.description,
            "filename": task.filename,
            "status": task.status,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "report_path": task.report_path
        }
        for task in tasks
    ]

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    db = SessionLocal()
    task = db.query(Task).filter(Task.task_id == task_id).first()
    db.close()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.task_id,
        "description": task.description,
        "filename": task.filename,
        "status": task.status,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "report_path": task.report_path
    }

@app.get("/api/reports/{task_id}")
async def get_report(task_id: str):
    db = SessionLocal()
    task = db.query(Task).filter(Task.task_id == task_id).first()
    db.close()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.report_path:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    
    # Resolve the path relative to the project root
    if task.report_path.startswith('../'):
        # Get the project root directory (parent of backend directory)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        # Remove '../' and join with project root
        report_path = os.path.join(project_root, task.report_path[3:])
    else:
        report_path = task.report_path
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report file not found: {report_path}")
    
    return FileResponse(report_path, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
