#!/bin/bash

# Check if Homebrew is installed (macOS-specific) and install if necessary
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install Python 3 if not installed (needed for PyQt5)
    if ! brew list python &>/dev/null; then
        echo "Installing Python 3..."
        brew install python
    fi

fi

# Create a virtual environment if it doesn't already exist
if [ ! -d "scraper_env" ]; then
    python3 -m venv scraper_env
    echo "Virtual environment 'scraper_env' created."
fi

# Activate the virtual environment
source scraper_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries if not already installed
pip install -r requirements.txt

# Install Playwright and its browser if not installed
if ! python3 -c "import playwright" &>/dev/null; then
    echo "Installing Playwright..."
    pip install playwright
fi
python3 -m playwright install chromium

# Run the scraper
python3 Scrapers.py

# Deactivate the virtual environment after running the script
deactivate
