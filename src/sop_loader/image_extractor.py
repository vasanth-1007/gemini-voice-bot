"""
Image extraction and processing for SOP documents
Handles image-heavy PDFs by extracting and analyzing images using Gemini Vision
"""
import io
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import tempfile

try:
    import PyPDF2
    from PIL import Image
    import fitz  # PyMuPDF for better image extraction
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF not installed. Install with: pip install pymupdf")

try:
    import google.generativeai as genai
except ImportError:
    logger.error("google-generativeai not installed")


@dataclass
class ExtractedImage:
    """Represents an extracted image with metadata"""
    image_data: bytes
    page_number: int
    image_index: int
    source_file: str
    width: int
    height: int
    description: Optional[str] = None


class ImageExtractor:
    """Extract and analyze images from SOP documents"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize image extractor
        
        Args:
            api_key: Google API key for Gemini Vision
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            logger.warning("No API key provided, image analysis disabled")
            self.model = None
        
        logger.info(f"Initialized ImageExtractor with model: {model_name}")
    
    def extract_images_from_pdf(self, pdf_path: Path) -> List[ExtractedImage]:
        """
        Extract all images from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of ExtractedImage objects
        """
        if not HAS_PYMUPDF:
            logger.warning("PyMuPDF not available, image extraction limited")
            return []
        
        extracted_images = []
        
        try:
            # Open PDF with PyMuPDF for better image extraction
            pdf_document = fitz.open(str(pdf_path))
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                logger.debug(f"Found {len(image_list)} images on page {page_num + 1}")
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Extract image
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Get image dimensions
                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size
                        
                        # Create ExtractedImage object
                        extracted_img = ExtractedImage(
                            image_data=image_bytes,
                            page_number=page_num + 1,
                            image_index=img_index,
                            source_file=pdf_path.name,
                            width=width,
                            height=height
                        )
                        
                        extracted_images.append(extracted_img)
                        logger.debug(f"Extracted image {img_index} from page {page_num + 1}: {width}x{height}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
                        continue
            
            pdf_document.close()
            logger.info(f"Extracted {len(extracted_images)} images from {pdf_path.name}")
            
        except Exception as e:
            logger.error(f"Error extracting images from {pdf_path.name}: {e}")
        
        return extracted_images
    
    def analyze_image_with_gemini(
        self,
        image: ExtractedImage,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Analyze image using Gemini Vision API
        
        Args:
            image: ExtractedImage object
            context: Optional context about the document
            
        Returns:
            Description of the image content
        """
        if not self.model:
            logger.warning("Gemini model not initialized, skipping image analysis")
            return None
        
        try:
            # Convert image bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image.image_data))
            
            # Create prompt for image analysis
            prompt = """Analyze this image from an SOP (Standard Operating Procedure) document.
            
Please describe:
1. What is shown in the image (diagrams, flowcharts, tables, screenshots, etc.)
2. Key information or instructions visible
3. Any text content in the image
4. Important details that would help answer questions about procedures

Provide a clear, detailed description that captures all important information."""

            if context:
                prompt += f"\n\nDocument context: {context}"
            
            # Generate description
            response = self.model.generate_content([prompt, pil_image])
            
            if response.text:
                description = response.text.strip()
                logger.info(f"Generated description for image from page {image.page_number}")
                logger.debug(f"Description: {description[:100]}...")
                return description
            else:
                logger.warning(f"No description generated for image on page {image.page_number}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing image from page {image.page_number}: {e}")
            return None
    
    def process_document_images(
        self,
        pdf_path: Path,
        context: Optional[str] = None,
        max_images: Optional[int] = None
    ) -> List[Dict]:
        """
        Extract and analyze all images from a document
        
        Args:
            pdf_path: Path to PDF file
            context: Optional context about the document
            max_images: Maximum number of images to process (None = all)
            
        Returns:
            List of dicts with image info and descriptions
        """
        # Extract images
        extracted_images = self.extract_images_from_pdf(pdf_path)
        
        if not extracted_images:
            logger.info(f"No images found in {pdf_path.name}")
            return []
        
        # Limit number of images if specified
        if max_images:
            extracted_images = extracted_images[:max_images]
            logger.info(f"Processing first {max_images} images only")
        
        # Filter out very small images (likely logos/icons)
        min_size = 100  # minimum width or height
        filtered_images = [
            img for img in extracted_images 
            if img.width >= min_size and img.height >= min_size
        ]
        
        logger.info(f"Filtered to {len(filtered_images)} significant images (>={min_size}px)")
        
        # Analyze each image
        processed_images = []
        
        for img in filtered_images:
            description = self.analyze_image_with_gemini(img, context)
            
            image_info = {
                'page_number': img.page_number,
                'image_index': img.image_index,
                'source_file': img.source_file,
                'width': img.width,
                'height': img.height,
                'description': description or f"Image on page {img.page_number}",
                'has_description': description is not None
            }
            
            processed_images.append(image_info)
        
        logger.info(f"Successfully processed {len(processed_images)} images from {pdf_path.name}")
        return processed_images
    
    def create_image_text_chunks(self, processed_images: List[Dict], source: str) -> List[Dict]:
        """
        Create text chunks from image descriptions for RAG indexing
        
        Args:
            processed_images: List of processed image dicts
            source: Source file name
            
        Returns:
            List of document chunks with image content
        """
        chunks = []
        
        for img in processed_images:
            if img.get('description'):
                # Create a chunk for this image
                chunk = {
                    'content': f"[IMAGE from page {img['page_number']}]: {img['description']}",
                    'source': source,
                    'page_number': img['page_number'],
                    'metadata': {
                        'type': 'image',
                        'image_index': img['image_index'],
                        'dimensions': f"{img['width']}x{img['height']}",
                        'has_description': img['has_description']
                    }
                }
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} text chunks from images")
        return chunks
    
    def get_extraction_stats(self, processed_images: List[Dict]) -> Dict:
        """Get statistics about extracted images"""
        return {
            'total_images': len(processed_images),
            'images_with_descriptions': sum(1 for img in processed_images if img.get('has_description')),
            'pages_with_images': len(set(img['page_number'] for img in processed_images)),
            'avg_width': sum(img['width'] for img in processed_images) / len(processed_images) if processed_images else 0,
            'avg_height': sum(img['height'] for img in processed_images) / len(processed_images) if processed_images else 0
        }
