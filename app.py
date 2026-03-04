import os
import shutil
import signal
import sys
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from diff.agent import CompareAgent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Compare Tool Agent")
agent = CompareAgent()

# Configuration
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me-to-something-secure")
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependencies
async def verify_admin_token(x_admin_token: str = Header(None)):
    """
    Simple security check to prevent unauthorized shutdowns if exposed.
    """
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    Serves the frontend and injects the admin token safely for local usage.
    """
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path) as f:
            content = f.read()
            # Inject token into a global JS variable for the frontend to use
            injection = f'<script>window.ADMIN_TOKEN = "{ADMIN_TOKEN}";</script>'
            return content.replace("</head>", f"{injection}</head>")
    return "Index not found"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if file.filename.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path, nrows=0)
        else:
            import pandas as pd
            df = pd.read_excel(file_path, nrows=0)
        return {"filename": file.filename, "headers": list(df.columns), "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {str(e)}")

@app.post("/compare")
async def compare_files(
    path1: str = Form(...),
    path2: str = Form(...),
    row_key: str = Form(...),
    use_llm: bool = Form(True)
):
    try:
        result = await agent.run(path1, path2, row_key, use_llm)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# --- Admin / System Routes ---

@app.get("/admin/port-status")
async def get_port_status(x_admin_token: str = Header(None)):
    """
    Checks if the server is running and returns the PID.
    """
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")
        
    return {
        "status": "running",
        "pid": os.getpid(),
        "message": "Server is active on this port."
    }

@app.post("/admin/shutdown")
async def shutdown_server(background_tasks: BackgroundTasks, x_admin_token: str = Header(None)):
    """
    Triggers a graceful shutdown of the server process.
    """
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    def _kill():
        import time
        time.sleep(1)
        print(f"Stopping server (PID: {os.getpid()})...")
        os.kill(os.getpid(), signal.SIGTERM)

    background_tasks.add_task(_kill)
    return {"message": "Server is shutting down. Port 8000 should be free in a moment."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
