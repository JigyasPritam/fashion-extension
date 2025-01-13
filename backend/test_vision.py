import os
from google.cloud import vision
import io

def test_vision_api():
    # Initialize the client
    client = vision.ImageAnnotatorClient()

    # Path to test image
    file_path = r"E:\Me\Om sai Ram\HelperExt\backend\testimage.jpg"

    # Load image
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()

    # Create image object
    image = vision.Image(content=content)

    try:
        # Perform a simple label detection
        response = client.label_detection(image=image)
        labels = response.label_annotations

        print("Vision API Test Results:")
        for label in labels:
            print(f"- {label.description} ({label.score:.2%} confidence)")
        
        print("\nAPI connection successful!")
        
    except Exception as e:
        print(f"Error testing Vision API: {str(e)}")

if __name__ == "__main__":
    test_vision_api()