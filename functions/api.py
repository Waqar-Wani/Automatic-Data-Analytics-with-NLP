from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs, urlparse
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Log the current directory and Python path
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

try:
    # Import your main application logic
    from main import app
    logger.info("Successfully imported Flask app")
except Exception as e:
    logger.error(f"Error importing Flask app: {str(e)}")
    logger.error(traceback.format_exc())

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{format % args}")

    def do_GET(self):
        try:
            logger.info(f"Received GET request for path: {self.path}")
            
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            logger.info(f"Parsed path: {path}")
            logger.info(f"Query parameters: {query_params}")
            
            # Create a mock request context
            with app.test_request_context(
                path=path,
                query_string=parsed_url.query,
                method='GET',
                headers=dict(self.headers)
            ) as ctx:
                logger.info("Created test request context")
                
                # Get the response from Flask
                response = app.full_dispatch_request()
                logger.info(f"Got response with status code: {response.status_code}")
                
                # Set response headers
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                
                # Send response body
                response_data = response.get_data()
                logger.info(f"Response data length: {len(response_data)}")
                self.wfile.write(response_data)
                return
        except Exception as e:
            logger.error(f"Error in GET request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
            return

    def do_POST(self):
        try:
            logger.info(f"Received POST request for path: {self.path}")
            
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            logger.info(f"Received POST data length: {len(post_data)}")
            
            # Create a mock request context
            with app.test_request_context(
                path=path,
                data=post_data,
                method='POST',
                content_type=self.headers.get('Content-Type', 'application/x-www-form-urlencoded'),
                headers=dict(self.headers)
            ) as ctx:
                logger.info("Created test request context")
                
                # Get the response from Flask
                response = app.full_dispatch_request()
                logger.info(f"Got response with status code: {response.status_code}")
                
                # Set response headers
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                
                # Send response body
                response_data = response.get_data()
                logger.info(f"Response data length: {len(response_data)}")
                self.wfile.write(response_data)
                return
        except Exception as e:
            logger.error(f"Error in POST request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
            return

    def do_OPTIONS(self):
        logger.info("Received OPTIONS request")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return 