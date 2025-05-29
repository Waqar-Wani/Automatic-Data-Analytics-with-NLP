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

# The functions directory is already in the correct source location.
# Netlify will pick it up because publish is set to "." in netlify.toml.

# Copy the main application file and backend directory to the root of the build output.
# These are needed for the function handler (api.py) to import them correctly,
# given that api.py is located in functions/ and imports from the parent directory.
cp main.py .
cp -r backend/ .

# Create a simple index.html in the public directory to redirect to the function
mkdir -p public
if [ ! -f public/index.html ]; then
    echo "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>Redirecting...</title>\\n    <meta http-equiv=\\\"refresh\\\" content=\\\"0; url=/.netlify/functions/api/\\\" />\\n</head>\\n<body>\\n    <p>Redirecting to the application...</p>\\n</body>\\n</html>" > public/index.htmlfi

# Deactivate virtual environment (optional but good practice)
deactivate