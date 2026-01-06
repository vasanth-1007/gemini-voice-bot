"""SOP Document Loader Module"""
from .document_parser import DocumentParser, DocumentChunk

try:
    from .image_extractor import ImageExtractor, ExtractedImage
    __all__ = ['DocumentParser', 'DocumentChunk', 'ImageExtractor', 'ExtractedImage']
except ImportError:
    __all__ = ['DocumentParser', 'DocumentChunk']
