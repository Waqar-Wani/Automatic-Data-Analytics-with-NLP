from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs, urlparse

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your main application logic
from main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Create a mock request context
        with app.test_request_context(
            path=path,
            query_string=parsed_url.query,
            method='GET'
        ) as ctx:
            # Get the response from Flask
            response = app.full_dispatch_request()
            
            # Set response headers
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.get_data())
            return

    def do_POST(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Create a mock request context
        with app.test_request_context(
            path=path,
            data=post_data,
            method='POST',
            content_type=self.headers.get('Content-Type', 'application/x-www-form-urlencoded')
        ) as ctx:
            # Get the response from Flask
            response = app.full_dispatch_request()
            
            # Set response headers
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.get_data())
            return 