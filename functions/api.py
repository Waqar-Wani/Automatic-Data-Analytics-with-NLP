from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs, urlparse
import traceback

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your main application logic
from main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Create a mock request context
            with app.test_request_context(
                path=path,
                query_string=parsed_url.query,
                method='GET',
                headers=dict(self.headers)
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
        except Exception as e:
            print(f"Error in GET request: {str(e)}")
            print(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
            return

    def do_POST(self):
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Create a mock request context
            with app.test_request_context(
                path=path,
                data=post_data,
                method='POST',
                content_type=self.headers.get('Content-Type', 'application/x-www-form-urlencoded'),
                headers=dict(self.headers)
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
        except Exception as e:
            print(f"Error in POST request: {str(e)}")
            print(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
            return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return 