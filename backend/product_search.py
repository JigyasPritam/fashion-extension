import os
from google.cloud import vision
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import io
import logging
import json
from PIL import Image
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List, Dict, Any
from google.oauth2 import service_account

class ProductSearchExtension:
    def __init__(self):
        """
        Initialize the product search extension with Google Cloud Vision API
        """
        # Load the credentials from the environment variable
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_path:
            raise ValueError("Google Cloud credentials path is not set in the environment variable.")
        
        # Load the credentials from the file
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        
        # Initialize the Vision API client with the credentials
        self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        
        # Set up logging
        self.logger = self._setup_logger()
        
        # Configure product search parameters
        self.product_categories = ['apparel', 'homegoods', 'electronics', 'toys']
        self.max_results = 10
        self.min_score = 0.5  # Minimum confidence score for results

    def _setup_logger(self) -> logging.Logger:
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('ProductSearch')

    def process_image(self, image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        Process and prepare image for search
        
        Args:
            image_input: Image as file path, bytes, or PIL Image
            
        Returns:
            Processed PIL Image
        """
        try:
            # Handle different input types
            if isinstance(image_input, str):
                image = Image.open(image_input)
            elif isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input))
            elif isinstance(image_input, Image.Image):
                image = image_input
            else:
                raise ValueError("Unsupported image input type")

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if too large
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.LANCZOS)

            return image

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise

    def search_similar_products(self, image_data: Image.Image) -> List[Dict[str, Any]]:
        """
        Search for similar products using Google Cloud Vision API
        
        Args:
            image_data: Processed PIL Image
            
        Returns:
            List of similar products with details
        """
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image_data.save(img_byte_arr, format='JPEG')
            content = img_byte_arr.getvalue()

            # Prepare the image for Vision API
            image = vision_v1.types.Image(content=content)

            # Perform both product search and web detection in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                product_future = executor.submit(self._search_products, image)
                web_future = executor.submit(self._detect_web_entities, image)

                products = product_future.result()
                web_entities = web_future.result()

            # Combine and enhance results
            enhanced_results = self._enhance_results(products, web_entities)
            
            return enhanced_results

        except Exception as e:
            self.logger.error(f"Error in product search: {str(e)}")
            return []

    def _search_products(self, image: vision_v1.types.Image) -> List[Dict[str, Any]]:
        """Perform product search using Vision API"""
        try:
            # Create product search request
            request = vision_v1.types.ProductSearchParams(
                product_categories=self.product_categories,
                filter=''  # Add filters if needed
            )

            # Create context with product search params
            context = vision_v1.types.ImageContext(
                product_search_params=request
            )

            # Perform the search
            response = self.vision_client.product_search(
                image=image,
                image_context=context
            )

            return self._process_product_results(response)

        except Exception as e:
            self.logger.error(f"Error in product search: {str(e)}")
            return []

    def _detect_web_entities(self, image: vision_v1.types.Image) -> List[Dict[str, Any]]:
        """Perform web detection for additional context"""
        try:
            response = self.vision_client.web_detection(image=image)
            entities = []

            for entity in response.web_detection.web_entities:
                if entity.score > self.min_score:
                    entities.append({
                        'description': entity.description,
                        'score': round(entity.score * 100, 2)
                    })

            return entities

        except Exception as e:
            self.logger.error(f"Error in web detection: {str(e)}")
            return []

    def _process_product_results(self, response) -> List[Dict[str, Any]]:
        """Process and format product search results"""
        products = []
        
        try:
            for result in response.product_search_results.results:
                if result.score < self.min_score:
                    continue

                product = {
                    'title': result.product.display_name,
                    'description': result.product.description,
                    'price': self._extract_price(result.product),
                    'score': round(result.score * 100, 2),
                    'labels': self._extract_labels(result.product),
                    'url': self._extract_product_url(result.product),
                    'website': self._extract_website(result.product)
                }

                if self._validate_product(product):
                    products.append(product)

                if len(products) >= self.max_results:
                    break

        except Exception as e:
            self.logger.error(f"Error processing results: {str(e)}")

        return products

    def _enhance_results(self, products: List[Dict[str, Any]], 
                        web_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance product results with web entities information"""
        try:
            # Add relevant web entities to each product
            for product in products:
                relevant_entities = [
                    entity['description'] for entity in web_entities
                    if entity['description'].lower() in product['title'].lower()
                ]
                product['related_terms'] = relevant_entities

            # Sort by score
            return sorted(products, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            self.logger.error(f"Error enhancing results: {str(e)}")
            return products

    def _extract_price(self, product) -> str:
        """Extract price from product data"""
        try:
            for label in product.product_labels:
                if label.key == 'price':
                    return f"${float(label.value):.2f}"
        except:
            return "Price not available"

    def _extract_labels(self, product) -> List[str]:
        """Extract product labels/categories"""
        try:
            return [label.value for label in product.product_labels 
                   if label.key == 'category']
        except:
            return []

    def _extract_product_url(self, product) -> Union[str, None]:
        """Extract product URL"""
        try:
            for label in product.product_labels:
                if label.key == 'product_url':
                    return label.value
        except:
            return None

    def _extract_website(self, product) -> str:
        """Extract website name from product data"""
        try:
            for label in product.product_labels:
                if label.key == 'website':
                    return label.value
        except:
            return "Unknown"

    def _validate_product(self, product: Dict[str, Any]) -> bool:
        """Validate product data"""
        required_fields = ['title', 'price', 'url']
        return all(product.get(field) for field in required_fields)

    def extract_product_info(self, url: str) -> Dict[str, Any]:
        """
        Extract additional product information from store pages
        
        Args:
            url: Product page URL
            
        Returns:
            Dictionary containing additional product information
        """
        try:
            # Make request to product page
            response = requests.get(url, timeout=10)
            
            # Use Vision API to analyze product page screenshot
            # This is a placeholder - implement based on your needs
            return {
                'available': True,
                'additional_images': [],
                'specifications': {},
                'reviews': []
            }

        except Exception as e:
            self.logger.error(f"Error extracting product info: {str(e)}")
            return {}

    def close(self):
        """Clean up resources"""
        # No cleanup needed for Vision API client
        pass
