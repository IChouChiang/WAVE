# PowerShell setup script for Browser Agent
# Usage: .\setup.ps1

Write-Host "🚀 Setting up Browser Agent..." -ForegroundColor Cyan

# Function to print colored messages
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check Python version
Write-Info "Checking Python version..."
$pythonCmd = "python"
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = (python --version 2>&1).ToString()
    Write-Info "Found $pythonVersion"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
    $pythonVersion = (python3 --version 2>&1).ToString()
    Write-Info "Found $pythonVersion"
} else {
    Write-Error "Python not found. Please install Python 3.8 or higher."
    exit 1
}

# Check Python version
$versionMatch = [regex]::Match($pythonVersion, '(\d+)\.(\d+)')
if ($versionMatch.Success) {
    $major = [int]$versionMatch.Groups[1].Value
    $minor = [int]$versionMatch.Groups[2].Value
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Error "Python 3.8 or higher is required. Found $major.$minor"
        exit 1
    }
}

# Create virtual environment
Write-Info "Creating virtual environment..."
if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
    Write-Success "Virtual environment created"
} else {
    Write-Warning "Virtual environment already exists"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
    Write-Success "Virtual environment activated"
} else {
    Write-Error "Could not find virtual environment activation script"
    exit 1
}

# Upgrade pip
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Info "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browser
Write-Info "Installing Playwright browser..."
python -m playwright install chromium

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Info "Creating .env file from template..."
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Success ".env file created from template"
        
        # Check if ds_api.txt exists and update .env with API key
        if (Test-Path "ds_api.txt") {
            Write-Info "Found ds_api.txt, updating .env with API key..."
            try {
                $apiKey = Get-Content "ds_api.txt" -Raw -Encoding UTF8
                $apiKey = $apiKey.Trim()
                # Remove any JSON metadata that might be appended
                if ($apiKey.Contains('{')) {
                    $apiKey = $apiKey.Split('{')[0].Trim()
                }
                
                if ($apiKey -and $apiKey.Length -gt 10) {
                    # Update .env file with API key
                    $envContent = Get-Content ".env" -Raw
                    $envContent = $envContent -replace 'DEEPSEEK_API_KEY=.*', "DEEPSEEK_API_KEY=$apiKey"
                    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
                    Write-Success "✓ API key loaded from ds_api.txt and added to .env"
                } else {
                    Write-Warning "API key in ds_api.txt appears to be invalid or empty"
                    Write-Warning "Please edit .env file to add your DeepSeek API key"
                }
            } catch {
                Write-Warning "Could not read API key from ds_api.txt: $_"
                Write-Warning "Please edit .env file to add your DeepSeek API key"
            }
        } else {
            Write-Warning "Please edit .env file to add your DeepSeek API key"
            Write-Warning "Or create ds_api.txt file with your API key"
        }
    } else {
        Write-Error ".env.example not found"
        exit 1
    }
} else {
    Write-Warning ".env file already exists"
    # Check if .env has API key, if not try to load from ds_api.txt
    $envContent = Get-Content ".env" -Raw
    if (-not ($envContent -match 'DEEPSEEK_API_KEY=\s*[^\s]')) {
        if (Test-Path "ds_api.txt") {
            Write-Info "Found ds_api.txt, updating .env with API key..."
            try {
                $apiKey = Get-Content "ds_api.txt" -Raw -Encoding UTF8
                $apiKey = $apiKey.Trim()
                # Remove any JSON metadata that might be appended
                if ($apiKey.Contains('{')) {
                    $apiKey = $apiKey.Split('{')[0].Trim()
                }
                
                if ($apiKey -and $apiKey.Length -gt 10) {
                    # Update .env file with API key
                    $envContent = $envContent -replace 'DEEPSEEK_API_KEY=.*', "DEEPSEEK_API_KEY=$apiKey"
                    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
                    Write-Success "✓ API key loaded from ds_api.txt and added to .env"
                }
            } catch {
                Write-Warning "Could not read API key from ds_api.txt: $_"
            }
        }
    }
}

# Create necessary directories
Write-Info "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "chrome_user_data" | Out-Null

# Test the setup
Write-Info "Testing the setup..."
try {
    python -c "import playwright, openai, mcp" 2>&1 | Out-Null
    Write-Success "All dependencies installed successfully"
} catch {
    Write-Error "Some dependencies failed to import"
    exit 1
}

# Create a simple test script
$testScript = @'
#!/usr/bin/env python3
"""
Test script to verify the setup.
"""

import sys
from config import config

def main():
    print("Testing Browser Agent setup...")
    
    # Test config loading
    print(f"✓ Config loaded from: {config.PROJECT_ROOT}")
    print(f"✓ Chrome user data: {config.get_chrome_user_data_dir()}")
    print(f"✓ XHS URL: {config.XHS_EXPLORE_URL}")
    
    # Validate config
    if config.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
        sys.exit(1)
    
    print("\n✅ Setup test passed!")
    print("\nNext steps:")
    print("1. Edit .env file to add your DeepSeek API key")
    print("2. Run: python tests/xhs_search_test.py")
    print("3. Run: python deepseek_agent.py (requires API key)")

if __name__ == "__main__":
    main()
'@

Set-Content -Path "test_setup.py" -Value $testScript

Write-Info "Running setup test..."
python test_setup.py

# Clean up test file
Remove-Item -Path "test_setup.py" -Force

Write-Success "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To get started:" -ForegroundColor Cyan
Write-Host "1. Edit .env file and add your DeepSeek API key" -ForegroundColor White
Write-Host "2. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Run tests: python tests/xhs_search_test.py" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Cyan