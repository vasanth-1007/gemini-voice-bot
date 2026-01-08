"""
Gemini-based SOP Processor
Uses Gemini 2.0 to intelligently extract and process text from SOPs
"""
import base64
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger
import time

try:
    import google.generativeai as genai
except ImportError:
    logger.error("google-generativeai not installed")


@dataclass
class ProcessedContent:
    """Represents processed content from Gemini"""
    text: str
    summary: str
    key_points: List[str]
    topics: List[str]
    source: str
    page_number: Optional[int] = None
    metadata: Optional[Dict] = None


class GeminiSOPProcessor:
    """
    Process SOP documents using Gemini 2.0
    Extracts, structures, and enhances text content
    """
    
    def __init__(
        self, 
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize Gemini SOP Processor
        
        Args:
            api_key: Google API key
            model_name: Gemini model to use
        """
        if not api_key:
            raise ValueError("API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        logger.info(f"Initialized GeminiSOPProcessor with model: {model_name}")
    
    def process_document(
        self,
        file_path: Path,
        batch_pages: bool = True
    ) -> List[ProcessedContent]:
        """
        Process entire document through Gemini
        
        Args:
            file_path: Path to document file
            batch_pages: Whether to process pages in batches
            
        Returns:
            List of ProcessedContent objects
        """
        logger.info(f"Processing document with Gemini: {file_path.name}")
        
        file_type = file_path.suffix.lower()
        
        if file_type == '.pdf':
            return self._process_pdf(file_path, batch_pages)
        elif file_type == '.docx':
            return self._process_docx(file_path)
        elif file_type == '.txt':
            return self._process_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return []
    
    def _process_pdf(
        self,
        pdf_path: Path,
        batch_pages: bool = True
    ) -> List[ProcessedContent]:
        """Process PDF using Gemini's multimodal capabilities"""
        processed_content = []
        
        try:
            # Upload PDF to Gemini
            logger.info(f"Uploading PDF to Gemini: {pdf_path.name}")
            uploaded_file = genai.upload_file(path=str(pdf_path))
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                logger.debug("Waiting for file processing...")
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise ValueError(f"File processing failed: {uploaded_file.state}")
            
            logger.info(f"✅ File uploaded successfully: {uploaded_file.name}")
            
            # Extract content using Gemini
            if batch_pages:
                # Process entire document at once
                content = self._extract_full_document(uploaded_file, pdf_path.name)
                if content:
                    processed_content.extend(content)
            else:
                # Process page by page (for very large documents)
                content = self._extract_page_by_page(uploaded_file, pdf_path.name)
                if content:
                    processed_content.extend(content)
            
            # Clean up uploaded file
            genai.delete_file(uploaded_file.name)
            logger.info(f"Cleaned up uploaded file")
            
        except Exception as e:
            logger.error(f"Error processing PDF with Gemini: {e}")
            raise
        
        return processed_content
    
    def _extract_full_document(
        self,
        uploaded_file,
        source_name: str
    ) -> List[ProcessedContent]:
        """Extract content from entire document at once"""
        
        prompt = """Analyze this SOP (Standard Operating Procedure) document comprehensively.

Extract and structure ALL information including:
1. Text content from all pages
2. Information from tables, charts, and diagrams
3. Key procedures and processes
4. Important policies and guidelines
5. Contact information and references

Format your response as follows:

=== FULL TEXT CONTENT ===
[Provide complete text content, maintaining structure and organization]

=== SUMMARY ===
[Provide a comprehensive summary of the entire document]

=== KEY POINTS ===
- [List all important points, procedures, and policies]
- [One point per line]

=== TOPICS COVERED ===
- [List main topics/sections covered]
- [One topic per line]

Be thorough and extract ALL information, including details from images, charts, and tables.
Maintain original terminology and specific details.
"""
        
        try:
            logger.info("Extracting full document content with Gemini...")
            
            response = self.model.generate_content(
                [prompt, uploaded_file],
                safety_settings=self.safety_settings,
                generation_config={"temperature": 0.1}  # Low temperature for accuracy
            )
            
            if not response.text:
                logger.warning("No text in response")
                return []
            
            # Parse response
            content = self._parse_gemini_response(
                response.text,
                source_name,
                page_number=None
            )
            
            logger.info(f"✅ Extracted full document content")
            return [content] if content else []
            
        except Exception as e:
            logger.error(f"Error extracting full document: {e}")
            return []
    
    def _extract_page_by_page(
        self,
        uploaded_file,
        source_name: str
    ) -> List[ProcessedContent]:
        """Extract content page by page (for very large documents)"""
        
        # This is a simplified version
        # For true page-by-page, you'd need PyMuPDF to split pages
        logger.warning("Page-by-page extraction not fully implemented")
        return self._extract_full_document(uploaded_file, source_name)
    
    def _process_docx(self, docx_path: Path) -> List[ProcessedContent]:
        """Process DOCX file"""
        try:
            # Read DOCX content
            from docx import Document as DocxDocument
            
            doc = DocxDocument(docx_path)
            full_text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # Process with Gemini
            content = self._enhance_text_with_gemini(
                text=full_text,
                source_name=docx_path.name
            )
            
            return [content] if content else []
            
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            return []
    
    def _process_txt(self, txt_path: Path) -> List[ProcessedContent]:
        """Process TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Process with Gemini
            content = self._enhance_text_with_gemini(
                text=text,
                source_name=txt_path.name
            )
            
            return [content] if content else []
            
        except Exception as e:
            logger.error(f"Error processing TXT: {e}")
            return []
    
    def _enhance_text_with_gemini(
        self,
        text: str,
        source_name: str
    ) -> Optional[ProcessedContent]:
        """Enhance plain text using Gemini"""
        
        prompt = f"""Analyze this SOP (Standard Operating Procedure) text.

TEXT:
{text}

Extract and structure the information:

=== FULL TEXT CONTENT ===
[Provide cleaned and well-structured text content]

=== SUMMARY ===
[Provide a comprehensive summary]

=== KEY POINTS ===
- [List all important points]
- [One point per line]

=== TOPICS COVERED ===
- [List main topics]
- [One topic per line]

Be thorough and maintain all important details.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config={"temperature": 0.1}
            )
            
            if not response.text:
                return None
            
            return self._parse_gemini_response(
                response.text,
                source_name,
                page_number=None
            )
            
        except Exception as e:
            logger.error(f"Error enhancing text: {e}")
            return None
    
    def _parse_gemini_response(
        self,
        response_text: str,
        source_name: str,
        page_number: Optional[int]
    ) -> Optional[ProcessedContent]:
        """Parse Gemini's structured response"""
        
        try:
            # Split response into sections
            sections = {
                'text': '',
                'summary': '',
                'key_points': [],
                'topics': []
            }
            
            current_section = None
            lines = response_text.split('\n')
            
            for line in lines:
                line_lower = line.lower().strip()
                
                # Detect section headers
                if '=== full text content ===' in line_lower:
                    current_section = 'text'
                    continue
                elif '=== summary ===' in line_lower:
                    current_section = 'summary'
                    continue
                elif '=== key points ===' in line_lower:
                    current_section = 'key_points'
                    continue
                elif '=== topics covered ===' in line_lower:
                    current_section = 'topics'
                    continue
                
                # Collect content
                if current_section == 'text':
                    sections['text'] += line + '\n'
                elif current_section == 'summary':
                    sections['summary'] += line + '\n'
                elif current_section == 'key_points':
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        sections['key_points'].append(line.strip().lstrip('-•').strip())
                elif current_section == 'topics':
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        sections['topics'].append(line.strip().lstrip('-•').strip())
            
            # Create ProcessedContent object
            content = ProcessedContent(
                text=sections['text'].strip(),
                summary=sections['summary'].strip(),
                key_points=sections['key_points'],
                topics=sections['topics'],
                source=source_name,
                page_number=page_number,
                metadata={
                    'processed_by': 'gemini',
                    'model': self.model_name
                }
            )
            
            logger.debug(f"Parsed content: {len(content.text)} chars, "
                        f"{len(content.key_points)} key points, "
                        f"{len(content.topics)} topics")
            
            return content
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return None
    
    def create_vector_chunks(
        self,
        processed_content: ProcessedContent,
        chunk_size: int = 1000,
        include_summary: bool = True
    ) -> List[Dict]:
        """
        Convert processed content into chunks for vector database
        
        Args:
            processed_content: ProcessedContent object
            chunk_size: Maximum chunk size
            include_summary: Whether to include summary as context
            
        Returns:
            List of chunks ready for vector DB
        """
        chunks = []
        
        # Main text content (chunked)
        text = processed_content.text
        
        # Add summary as context prefix if requested
        if include_summary and processed_content.summary:
            context_prefix = f"[Document Summary: {processed_content.summary}]\n\n"
        else:
            context_prefix = ""
        
        # Split text into chunks
        words = text.split()
        current_chunk = []
        current_length = len(context_prefix)
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size:
                # Create chunk
                chunk_text = context_prefix + ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'source': processed_content.source,
                    'page_number': processed_content.page_number,
                    'metadata': {
                        'type': 'main_content',
                        'processed_by_gemini': True,
                        'has_summary': include_summary,
                        **processed_content.metadata
                    }
                })
                
                # Start new chunk
                current_chunk = [word]
                current_length = len(context_prefix) + word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Add last chunk
        if current_chunk:
            chunk_text = context_prefix + ' '.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'source': processed_content.source,
                'page_number': processed_content.page_number,
                'metadata': {
                    'type': 'main_content',
                    'processed_by_gemini': True,
                    'has_summary': include_summary,
                    **processed_content.metadata
                }
            })
        
        # Add key points as separate searchable chunk
        if processed_content.key_points:
            key_points_text = "KEY POINTS:\n" + '\n'.join(
                f"• {point}" for point in processed_content.key_points
            )
            chunks.append({
                'content': key_points_text,
                'source': processed_content.source,
                'page_number': processed_content.page_number,
                'metadata': {
                    'type': 'key_points',
                    'processed_by_gemini': True,
                    **processed_content.metadata
                }
            })
        
        # Add topics
        if processed_content.topics:
            topics_text = "TOPICS COVERED:\n" + '\n'.join(
                f"• {topic}" for topic in processed_content.topics
            )
            chunks.append({
                'content': topics_text,
                'source': processed_content.source,
                'page_number': processed_content.page_number,
                'metadata': {
                    'type': 'topics',
                    'processed_by_gemini': True,
                    **processed_content.metadata
                }
            })
        
        logger.info(f"Created {len(chunks)} chunks from processed content")
        return chunks
