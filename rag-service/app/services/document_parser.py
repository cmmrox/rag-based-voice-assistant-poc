import logging
import io
from typing import List, Tuple
from pypdf2 import PdfReader
import markdown

logger = logging.getLogger(__name__)


class DocumentParser:
    """Document parser for PDF, TXT, and MD files"""
    
    @staticmethod
    async def parse_pdf(file_content: bytes) -> str:
        """Parse PDF file and extract text"""
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Parsed PDF: {len(text)} characters")
            return text
        
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def parse_txt(file_content: bytes) -> str:
        """Parse TXT file and extract text"""
        try:
            text = file_content.decode('utf-8')
            logger.info(f"Parsed TXT: {len(text)} characters")
            return text
        
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                text = file_content.decode('latin-1')
                logger.info(f"Parsed TXT (latin-1): {len(text)} characters")
                return text
            except Exception as e:
                logger.error(f"Error parsing TXT: {e}", exc_info=True)
                raise
    
    @staticmethod
    async def parse_markdown(file_content: bytes) -> str:
        """Parse Markdown file and extract text"""
        try:
            md_text = file_content.decode('utf-8')
            # Convert markdown to plain text (remove markdown syntax)
            # For POC, we'll just return the raw text
            # In production, you might want to use a markdown parser
            text = markdown.markdown(md_text)
            logger.info(f"Parsed Markdown: {len(text)} characters")
            return md_text  # Return raw markdown for now
        
        except Exception as e:
            logger.error(f"Error parsing Markdown: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def parse_document(file_content: bytes, filename: str) -> str:
        """Parse document based on file extension"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return await DocumentParser.parse_pdf(file_content)
        elif filename_lower.endswith('.txt'):
            return await DocumentParser.parse_txt(file_content)
        elif filename_lower.endswith('.md') or filename_lower.endswith('.markdown'):
            return await DocumentParser.parse_markdown(file_content)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> List[Tuple[str, int]]:
        """Chunk text into smaller pieces with overlap"""
        # Simple token-based chunking (approximate)
        # In production, use a proper tokenizer
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [(text, 0)]
        
        start = 0
        chunk_id = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append((chunk_text, chunk_id))
            
            # Move start forward with overlap
            start = end - overlap
            chunk_id += 1
        
        logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks


# Global document parser instance
document_parser = DocumentParser()

