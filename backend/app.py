from flask import Flask, request, jsonify
from flask_cors import CORS
from product_search import ProductSearchExtension
import base64
import io
from PIL import Image
from io import BytesIO
import logging
import os



app = Flask(__name__)
# Enable CORS for all routes with specific origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "chrome-extension://*",  # Allow Chrome extensions
            "moz-extension://*",     # Allow Firefox extensions
            "http://localhost:5000/*"     # Allow local development
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/search', methods=['POST'])
def search_products():
    try:
        logger.info("Received search request")
        
        # Get base64 image from request
        data = request.json
        if not data or 'image' not in data:
            logger.error("No image data received")
            return jsonify({'error': 'No image data received'}), 400

        try:
            # Split base64 string if it contains data URI
            image_data = data['image']
            if ',' in image_data:
                image_data = image_data.split(',')[1]

            # Decode the base64 image data into bytes
            image_bytes = base64.b64decode(image_data)
            
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            return jsonify({'error': 'Invalid image data'}), 400

        # Initialize product search
        try:
            # Ensure that the environment variable for Google Cloud credentials is set
            google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not google_credentials_path:
                logger.error("Google Cloud credentials path is not set in the environment variables.")
                return jsonify({'error': 'Google Cloud credentials path is not set in environment variables'}), 500
            
            # Initialize the product search extension
            extension = ProductSearchExtension()  # Credentials will be automatically loaded from environment
            processed_image = extension.process_image(io.BytesIO(image_bytes))  # Pass bytes as a stream
            results = extension.search_similar_products(processed_image)
            extension.close()
        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
            return jsonify({'error': 'Error processing image'}), 500

        return jsonify(results)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test_connection():
    """Test endpoint to verify server is running"""
    return jsonify({'status': 'Server is running'})

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)
