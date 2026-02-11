# Check if Docker is running
docker ps
if ($LASTEXITCODE -ne 0) {
    Write-Host "Starting Docker Compose..."
    docker compose up -d
}

# Install Python Deps
Write-Host "Installing Python Dependencies..."
pip install -r requirements.txt

# Start Services in new windows
Write-Host "Starting Services..."

# 1. Collector
Start-Process python -ArgumentList "services/collector/main.py" -WindowStyle Minimized

# 2. Bridge (Data Saver)
Start-Process python -ArgumentList "services/api/bridge.py" -WindowStyle Minimized

# 3. Controller
Start-Process python -ArgumentList "services/controller/main.py" -WindowStyle Minimized

# 4. API Server
Start-Process uvicorn -ArgumentList "services.api.main:app --reload --port 8000"

# 5. AI Engine
Start-Process python -ArgumentList "services/ai_engine/main.py" -WindowStyle Minimized

# 6. Frontend
Write-Host "Starting Frontend..."
Set-Location web/ui
npm install
npm run dev
