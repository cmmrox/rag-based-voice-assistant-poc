import logging
import io
import re
from typing import List, Tuple
from PyPDF2 import PdfReader
import markdown

logger = logging.getLogger(__name__)

# Approximate token estimation: ~4 characters per token for English text
CHARS_PER_TOKEN = 4


class DocumentParser:
    """Document parser for PDF, TXT, and MD files"""
    
    @staticmethod
    async def parse_pdf(file_content: bytes) -> str:
        """Parse PDF file and extract text"""
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            logger.info(f"Parsing PDF with {total_pages} pages...")
            
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += page_text + "\n"
                
                # Log progress every 10 pages or on last page
                if page_num % 10 == 0 or page_num == total_pages:
                    logger.info(f"Processed {page_num}/{total_pages} pages "
                              f"({len(text)} characters extracted)")
            
            logger.info(f"Successfully parsed PDF: {len(text)} characters, {total_pages} pages")
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
    def _estimate_tokens(text: str) -> int:
        """Estimate token count (approximate: ~4 chars per token)"""
        return len(text) // CHARS_PER_TOKEN
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Pattern to match sentence endings (. ! ?) followed by whitespace or end of string
        # Handles common abbreviations and decimal numbers
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])(?=\n\n)|(?<=[.!?])(?=\Z)'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out empty sentences and clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> List[Tuple[str, int]]:
        """
        Chunk text into smaller pieces with overlap, respecting sentence boundaries.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap size in tokens (approximate)
        
        Returns:
            List of tuples (chunk_text, chunk_id)
        """
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        if not text:
            logger.warning("Empty text provided for chunking")
            return []
        
        # Estimate total tokens
        total_tokens = DocumentParser._estimate_tokens(text)
        logger.info(f"Chunking text: {len(text)} characters, ~{total_tokens} tokens "
                   f"(target chunk size: {chunk_size} tokens, overlap: {overlap} tokens)")
        
        # If text is smaller than chunk size, return as single chunk
        if total_tokens <= chunk_size:
            logger.info("Text fits in single chunk, no chunking needed")
            return [(text, 0)]
        
        # Split into sentences for sentence-aware chunking
        sentences = DocumentParser._split_into_sentences(text)
        logger.info(f"Split text into {len(sentences)} sentences")
        
        chunks = []
        chunk_id = 0
        current_chunk_sentences = []
        current_chunk_tokens = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            sentence_tokens = DocumentParser._estimate_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_chunk_tokens + sentence_tokens > chunk_size and current_chunk_sentences:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append((chunk_text, chunk_id))
                logger.debug(f"Created chunk {chunk_id}: ~{current_chunk_tokens} tokens, "
                           f"{len(current_chunk_sentences)} sentences")
                
                chunk_id += 1
                
                # Start new chunk with overlap
                # Go back to include overlap sentences
                overlap_tokens = 0
                overlap_sentences = []
                j = len(current_chunk_sentences) - 1
                
                while j >= 0 and overlap_tokens < overlap:
                    prev_sentence = current_chunk_sentences[j]
                    prev_tokens = DocumentParser._estimate_tokens(prev_sentence)
                    if overlap_tokens + prev_tokens <= overlap:
                        overlap_sentences.insert(0, prev_sentence)
                        overlap_tokens += prev_tokens
                        j -= 1
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences
                current_chunk_tokens = overlap_tokens
                
                # Don't increment i, process current sentence again
                continue
            
            # Add sentence to current chunk
            current_chunk_sentences.append(sentence)
            current_chunk_tokens += sentence_tokens
            i += 1
        
        # Add final chunk if there are remaining sentences
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append((chunk_text, chunk_id))
            logger.debug(f"Created final chunk {chunk_id}: ~{current_chunk_tokens} tokens, "
                       f"{len(current_chunk_sentences)} sentences")
        
        # Log chunk statistics
        if chunks:
            chunk_sizes = [DocumentParser._estimate_tokens(chunk[0]) for chunk in chunks]
            avg_size = sum(chunk_sizes) / len(chunk_sizes)
            min_size = min(chunk_sizes)
            max_size = max(chunk_sizes)
            
            logger.info(f"Successfully chunked text into {len(chunks)} chunks: "
                       f"avg ~{avg_size:.0f} tokens, "
                       f"min ~{min_size} tokens, "
                       f"max ~{max_size} tokens")
        
        return chunks


# Global document parser instance
document_parser = DocumentParser()

