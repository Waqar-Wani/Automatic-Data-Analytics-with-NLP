#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p public
mkdir -p functions

# Copy static files to public directory
cp -r backend/static/* public/ 2>/dev/null || :

# Copy templates to functions directory
mkdir -p functions/templates
cp -r backend/templates/* functions/templates/ 2>/dev/null || :

# Create a simple index.html if it doesn't exist
if [ ! -f public/index.html ]; then
    echo "<!DOCTYPE html>
<html>
<head>
    <title>Data Analytics App</title>
    <meta http-equiv=\"refresh\" content=\"0; url=/.netlify/functions/api/\" />
</head>
<body>
    <p>Redirecting to the application...</p>
</body>
</html>" > public/index.html
fi 