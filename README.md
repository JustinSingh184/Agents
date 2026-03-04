# Compare Tool Agent

A professional desktop-style web application for comparing Excel and CSV files. It identifies row-level and cell-level differences using a deterministic diff engine enhanced by local LLM intelligence.

## Architecture

```text
[ Browser UI ] <--> [ FastAPI Backend ]
                          |
            ------------------------------
            |                            |
    [ Agent Pipeline ]           [ Ollama LLM ]
    (Normalize -> Diff)          (Smart Mapping)
    
```

## Features
- **Deterministic Diff**: Precise identification of added, removed, and modified rows.
- **LLM Intelligence**: Uses Ollama for semantic header mapping and plain-English summaries.
- **Side-by-Side View**: Visual highlights for easy comparison (Green for File 1, Red for File 2).
- **Responsive Design**: Support for light and dark modes with accessible contrast.
- **Safe Shutdown**: Built-in "Kill Server" button to manage backend processes.

## Setup Instructions

### 1. Install Dependencies
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Ollama
Pull the required model:
```bash
ollama pull qwen2.5:7b
```

### 3. Environment Setup
Copy `.env.example` to `.env` and adjust if necessary.
```bash
cp .env.example .env
```
*Note: The .env file now includes an `ADMIN_TOKEN` for securing the shutdown feature.*

### 4. Run the Application
Ensure your virtual environment is activated, then run:
```bash
source venv/bin/activate
python3 app.py
```
Open `http://localhost:8000` in your browser.

## Freeing Port 8000 and Stopping the Server Cleanly

Development servers sometimes get stuck, leaving port 8000 occupied ("Address already in use"). This section explains how to handle this on any operating system.

### Why Ports Get Stuck
- **Hung Processes**: If you close the terminal without stopping the app, the process may persist in the background.
- **Reloaders**: Tools like `uvicorn --reload` spawn child processes. Killing the parent might leave the child running (orphaned).
- **Crashes**: A hard crash can sometimes leave the socket open for a short timeout period.

### The Correct Way to Stop
Always try to stop the server by pressing `Ctrl+C` in the terminal where it is running. This sends a `SIGINT` signal, allowing the application to clean up resources and close the port gracefully.

### How to Identify and Kill "Stuck" Processes

#### macOS and Linux

**1. Identify the Process**
Use `lsof` (List Open Files) to see what is listening on port 8000.
```bash
lsof -i :8000
```
*Output Example:*
```text
COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
Python  12345   user    3u  IPv4 0x...      0t0  TCP *:8000 (LISTEN)
```
Here, `12345` is the PID (Process ID).

**2. Kill the Process**
Once you have the PID:
```bash
kill 12345
```
If it refuses to close, force kill it (use with caution):
```bash
kill -9 12345
```

**3. The "One-Liner" Solution**
To find and kill the process on port 8000 in one command:
```bash
lsof -t -i:8000 | xargs kill -9
```

**4. Verify**
Run `lsof -i :8000` again. It should return nothing.

#### Windows

**1. Identify the Process**
Use `netstat` to find the PID.
```cmd
netstat -ano | findstr :8000
```
*Output Example:*
```text
  TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       12345
```
The number at the end (`12345`) is the PID.

**2. Kill the Process**
Use `taskkill` to forcefully terminate it.
```cmd
taskkill /PID 12345 /F
```

#### Safe Restart Recipe
If you encounter "Address already in use":
1.  **Stop**: Run the "One-Liner" (Mac/Linux) or `taskkill` (Windows).
2.  **Verify**: Check that the port command returns no output.
3.  **Run**: Start your app again (`python3 app.py`).

## Admin API & Security
The app exposes admin endpoints to manage the server state.
- **Authorization**: Protected by `X-ADMIN-TOKEN` header (configured in `.env`).
- **Shutdown**: `POST /admin/shutdown` triggers a self-termination signal.

## Troubleshooting
- **Permission Denied (lsof/kill)**: You may need to run commands with `sudo` if the process was started by another user.
- **Firewall Rules**: If `lsof` shows the port is free but you cannot access `localhost:8000`, check your firewall settings.
