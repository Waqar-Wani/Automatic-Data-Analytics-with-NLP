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

# Create a simple index.html if it doesn't exist
if [ ! -f public/index.html ]; then
    echo "<!DOCTYPE html>
<html>
<head>
    <title>Data Analytics App</title>
</head>
<body>
    <h1>Welcome to Data Analytics App</h1>
    <p>API is running on Netlify Functions</p>
</body>
</html>" > public/index.html
fi 