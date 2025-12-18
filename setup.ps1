# Copy environment template
Copy-Item .env.example .env

# Install Ollama (if not already installed)
Write-Host "Please ensure Ollama is installed from https://ollama.ai"
Write-Host "After installation, run: ollama pull mistral"
Write-Host ""

# Backend setup
Write-Host "Setting up backend..."
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location ..

# Frontend setup
Write-Host "Setting up frontend..."
Set-Location frontend
npm install
Set-Location ..

Write-Host ""
Write-Host "Setup complete!"
Write-Host ""
Write-Host "To start the application:"
Write-Host "1. Backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload"
Write-Host "2. Frontend: cd frontend && npm run dev"
