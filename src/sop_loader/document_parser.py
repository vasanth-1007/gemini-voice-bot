"""
Document parser module for loading and processing SOP documents
Supports PDF, DOCX, and TXT formats with image extraction
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger

# Document processing imports
try:
    import PyPDF2
    from docx import Document as DocxDocument
except ImportError as e:
    logger.warning(f"Import error: {e}. Install required packages.")

try:
    from .image_extractor import ImageExtractor
    HAS_IMAGE_EXTRACTOR = True
except ImportError:
    HAS_IMAGE_EXTRACTOR = False
    logger.warning("ImageExtractor not available")


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    content: str
    source: str
    page_number: Optional[int] = None
    metadata: Optional[Dict] = None


class DocumentParser:
    """Parse various document formats from SOP folder"""
    
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt'}
    
    def __init__(self, sop_folder: Path, api_key: Optional[str] = None, extract_images: bool = True):
        """
        Initialize document parser
        
        Args:
            sop_folder: Path to folder containing SOP documents
            api_key: Google API key for image analysis (optional)
            extract_images: Whether to extract and analyze images
        """
        self.sop_folder = Path(sop_folder)
        if not self.sop_folder.exists():
            raise ValueError(f"SOP folder does not exist: {sop_folder}")
        
        self.extract_images = extract_images
        
        # Initialize image extractor if available and enabled
        if extract_images and HAS_IMAGE_EXTRACTOR and api_key:
            self.image_extractor = ImageExtractor(api_key=api_key)
            logger.info("Image extraction enabled")
        else:
            self.image_extractor = None
            if extract_images:
                logger.warning("Image extraction disabled (missing API key or dependencies)")
        
        logger.info(f"Initialized DocumentParser with folder: {self.sop_folder}")
    
    def load_all_documents(self) -> List[DocumentChunk]:
        """
        Load all supported documents from SOP folder
        
        Returns:
            List of DocumentChunk objects (including image descriptions)
        """
        all_chunks = []
        
        # Get all files in SOP folder
        files = [f for f in self.sop_folder.iterdir() if f.is_file()]
        
        if not files:
            logger.warning(f"No files found in {self.sop_folder}")
            return all_chunks
        
        logger.info(f"Found {len(files)} files in SOP folder")
        
        for file_path in files:
            if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    # Parse text content
                    chunks = self._parse_document(file_path)
                    all_chunks.extend(chunks)
                    logger.info(f"Loaded {len(chunks)} text chunks from {file_path.name}")
                    
                    # Extract and analyze images if enabled (for PDFs)
                    if self.image_extractor and file_path.suffix.lower() == '.pdf':
                        image_chunks = self._extract_images_from_document(file_path)
                        all_chunks.extend(image_chunks)
                        logger.info(f"Loaded {len(image_chunks)} image chunks from {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error parsing {file_path.name}: {e}")
            else:
                logger.warning(f"Unsupported format: {file_path.name}")
        
        logger.info(f"Total chunks loaded: {len(all_chunks)}")
        return all_chunks
    
    def _parse_document(self, file_path: Path) -> List[DocumentChunk]:
        """
        Parse a single document based on its format
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of DocumentChunk objects
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._parse_pdf(file_path)
        elif suffix == '.docx':
            return self._parse_docx(file_path)
        elif suffix == '.txt':
            return self._parse_txt(file_path)
        else:
            logger.warning(f"Unsupported format: {suffix}")
            return []
    
    def _parse_pdf(self, file_path: Path) -> List[DocumentChunk]:
        """Parse PDF document"""
        chunks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    
                    if text.strip():
                        chunk = DocumentChunk(
                            content=text.strip(),
                            source=file_path.name,
                            page_number=page_num,
                            metadata={'format': 'pdf', 'total_pages': len(pdf_reader.pages)}
                        )
                        chunks.append(chunk)
        
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path.name}: {e}")
            raise
        
        return chunks
    
    def _parse_docx(self, file_path: Path) -> List[DocumentChunk]:
        """Parse DOCX document"""
        chunks = []
        
        try:
            doc = DocxDocument(file_path)
            
            # Combine all paragraphs
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            
            if full_text:
                chunk = DocumentChunk(
                    content="\n".join(full_text),
                    source=file_path.name,
                    metadata={'format': 'docx', 'paragraphs': len(full_text)}
                )
                chunks.append(chunk)
        
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path.name}: {e}")
            raise
        
        return chunks
    
    def _parse_txt(self, file_path: Path) -> List[DocumentChunk]:
        """Parse TXT document"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if text.strip():
                chunk = DocumentChunk(
                    content=text.strip(),
                    source=file_path.name,
                    metadata={'format': 'txt'}
                )
                chunks.append(chunk)
        
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path.name}: {e}")
            raise
        
        return chunks
    
    def _extract_images_from_document(self, file_path: Path) -> List[DocumentChunk]:
        """
        Extract and analyze images from a document
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of DocumentChunk objects with image descriptions
        """
        if not self.image_extractor:
            return []
        
        try:
            logger.info(f"Extracting images from {file_path.name}...")
            
            # Process images
            processed_images = self.image_extractor.process_document_images(
                pdf_path=file_path,
                context=f"This is from an SOP document: {file_path.name}"
            )
            
            # Get stats
            if processed_images:
                stats = self.image_extractor.get_extraction_stats(processed_images)
                logger.info(f"Image extraction stats: {stats}")
            
            # Convert to DocumentChunk objects
            chunks = []
            for img in processed_images:
                if img.get('description'):
                    chunk = DocumentChunk(
                        content=f"[IMAGE from page {img['page_number']}]: {img['description']}",
                        source=file_path.name,
                        page_number=img['page_number'],
                        metadata={
                            'format': 'pdf',
                            'type': 'image',
                            'image_index': img['image_index'],
                            'dimensions': f"{img['width']}x{img['height']}"
                        }
                    )
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting images from {file_path.name}: {e}")
            return []
    
    def get_document_stats(self) -> Dict:
        """Get statistics about documents in SOP folder"""
        files = list(self.sop_folder.iterdir())
        
        stats = {
            'total_files': len(files),
            'by_format': {},
            'supported_files': 0,
            'unsupported_files': 0,
            'image_extraction_enabled': self.image_extractor is not None
        }
        
        for file_path in files:
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                stats['by_format'][suffix] = stats['by_format'].get(suffix, 0) + 1
                
                if suffix in self.SUPPORTED_FORMATS:
                    stats['supported_files'] += 1
                else:
                    stats['unsupported_files'] += 1
        
        return stats
