# PowerShell script to start the Django project
# Author: Cascade
# Date: 2025-03-20

# Set error action preference to stop on error
$ErrorActionPreference = "Stop"

# Define colors for output
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red
$CYAN = [ConsoleColor]::Cyan

# Function to display colored messages
function Write-ColoredMessage {
    param (
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if a command exists
function Test-CommandExists {
    param (
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

# Check if Python is installed
Write-ColoredMessage "Checking if Python is installed..." $CYAN
if (-not (Test-CommandExists "python")) {
    Write-ColoredMessage "Python is not installed. Please install Python 3.8 or higher." $RED
    exit 1
}

# Check Python version
$pythonVersion = (python --version) 2>&1
Write-ColoredMessage "Found $pythonVersion" $GREEN

# Check if pip is installed
Write-ColoredMessage "Checking if pip is installed..." $CYAN
if (-not (Test-CommandExists "pip")) {
    Write-ColoredMessage "pip is not installed. Please install pip." $RED
    exit 1
}

# Create virtual environment if it doesn't exist
$venvPath = ".venv"
if (-not (Test-Path $venvPath)) {
    Write-ColoredMessage "Creating virtual environment..." $CYAN
    python -m venv $venvPath
    if (-not $?) {
        Write-ColoredMessage "Failed to create virtual environment." $RED
        exit 1
    }
    Write-ColoredMessage "Virtual environment created successfully." $GREEN
} else {
    Write-ColoredMessage "Virtual environment already exists." $GREEN
}

# Activate virtual environment
Write-ColoredMessage "Activating virtual environment..." $CYAN
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
try {
    & $activateScript
    Write-ColoredMessage "Virtual environment activated." $GREEN
} catch {
    Write-ColoredMessage "Failed to activate virtual environment: $_" $RED
    exit 1
}

# Install dependencies
Write-ColoredMessage "Installing dependencies..." $CYAN
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if (-not $?) {
        Write-ColoredMessage "Failed to install dependencies." $RED
        exit 1
    }
    Write-ColoredMessage "Dependencies installed successfully." $GREEN
} else {
    Write-ColoredMessage "requirements.txt not found. Installing Django..." $YELLOW
    pip install django
    if (-not $?) {
        Write-ColoredMessage "Failed to install Django." $RED
        exit 1
    }
    Write-ColoredMessage "Django installed successfully." $GREEN
}

# Create static directory if it doesn't exist
$staticPath = "static"
if (-not (Test-Path $staticPath)) {
    Write-ColoredMessage "Creating static directory..." $CYAN
    New-Item -ItemType Directory -Path $staticPath | Out-Null
    Write-ColoredMessage "Static directory created." $GREEN
}

# Run migrations
Write-ColoredMessage "Running migrations..." $CYAN
python manage.py migrate
if (-not $?) {
    Write-ColoredMessage "Failed to run migrations." $RED
    exit 1
}
Write-ColoredMessage "Migrations completed successfully." $GREEN

# Collect static files
Write-ColoredMessage "Collecting static files..." $CYAN
python manage.py collectstatic --noinput
if (-not $?) {
    Write-ColoredMessage "Failed to collect static files." $YELLOW
    Write-ColoredMessage "This is not critical, continuing..." $YELLOW
}

# Create a superuser if none exists
Write-ColoredMessage "Checking if superuser exists..." $CYAN
$superuserExists = python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(is_superuser=True).exists())
"

if ($superuserExists -eq "False") {
    Write-ColoredMessage "No superuser found. Would you like to create one? (y/n)" $YELLOW
    $createSuperuser = Read-Host
    if ($createSuperuser -eq "y") {
        python manage.py createsuperuser
    }
}

# Start development server
Write-ColoredMessage "Starting development server..." $CYAN
Write-ColoredMessage "The server will be available at http://127.0.0.1:8000/" $GREEN
Write-ColoredMessage "Press Ctrl+C to stop the server." $YELLOW
python manage.py runserver
