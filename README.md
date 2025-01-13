## Product Search Extension

A browser extension that allows users to search for similar products across multiple e-commerce platforms using image recognition. The extension enables users to upload an image, and it uses advanced image processing and search algorithms to find visually similar products, displaying the results directly in the browser.

## Features

- **Image-based Product Search:** Upload any product image to search for similar products across various e-commerce websites.
- **Multi-platform Support:** Works with websites like Amazon, Flipkart, Myntra, and more.
- **Google Cloud Vision API Integration:** Uses Google Cloud Vision API for enhanced image recognition capabilities.
- **User-friendly Interface:** A simple, intuitive UI to upload images and view search results.
- **Real-time Results:** Displays similar products with product details, price, and a link to purchase.


## Prerequisites

Before you start, make sure you have the following installed:

1. **Python 3.8 or higher** 
2. **Chrome or Firefox browser**
3. Basic knowledge of **Python** and **web development**

### Required Python Packages:

Install the necessary Python packages:

pip install pillow requests opencv-python webdriver_manager flask flask_cors vision BytesIO

### Getting Started

# 1. Clone the repository:

Clone this repository to your local machine:

git clone https://github.com/JigyasPritam/fashion-extension.git
cd fashion-extension

# 2. Backend Setup

Go to the backend folder and install the required Python packages using the following command:

pip install -r requirements.txt

Start the Flask backend server:

cd backend
python app.py

The server will start on http://localhost:5000.

### Files and Folders

# 1. Frontend:

popup.html: The HTML for the extension’s popup.
popup.css: The CSS for styling the popup.
popup.js: JavaScript to handle the image upload and search functionality.
background.js: The background script that interacts with the browser.

# 2. Backend:

app.py: The Flask application that handles incoming requests, processes images, and returns search results.
product_search.py: Contains the logic for searching and retrieving similar products using image recognition techniques.
requirements.txt: Lists the Python dependencies for the backend.

## Error Handling

CORS Errors: Ensure the Flask server is set up to handle cross-origin requests from the extension.
Image Processing Errors: Verify that the image format is valid and meets the size requirements.
Search Failures: Ensure the Google Cloud Vision API and other external services are available.

## Future Improvements

Multiple Language Support: Support multiple languages for product search, making the extension more accessible to global users.

Price Tracking: Implement price tracking features for products over time.

Comparison Features: Allow users to compare similar products across different platforms.

Product Comparison: Enable users to compare multiple products across different e-commerce platforms, showcasing features like price, ratings, and availability.

Image Recognition Enhancement: Use more advanced AI models (such as TensorFlow or PyTorch-based models or FashionClip model) for even better product recognition accuracy, especially for obscure products.

Search Customization: Allow users to set preferred e-commerce platforms, so that the extension prioritizes these platforms in search results.
