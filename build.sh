#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create virtual environment in the project root
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# --- Prepare files for Netlify deployment ---

# The functions directory (containing api.py), main.py, and the backend directory
# are already in the correct source locations at the project root.
# Netlify will pick them up because publish is set to "." in netlify.toml.
# No need to copy these files.

# Create a simple index.html in the public directory to redirect to the function
mkdir -p public
if [ ! -f public/index.html ]; then
    echo "<!DOCTYPE html>\n<html>\n<head>\n    <title>Redirecting...</title>\n    <meta http-equiv=\"refresh\" content=\"0; url=/.netlify/functions/api/\" />\n</head>\n<body>\n    <p>Redirecting to the application...</p>\n</body>\n</html>" > public/index.html
fi

# Deactivate virtual environment (optional but good practice)
deactivate