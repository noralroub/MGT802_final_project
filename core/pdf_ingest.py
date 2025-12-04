"""PDF ingestion and text chunking module for cardiovascular trial papers."""

import logging
import re
from typing import Dict, List
import pdfplumber
import tiktoken

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from all pages of a PDF using pdfplumber.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Concatenated text from all pages
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    logger.warning(f"Page {page_num} returned empty text")

        if not text.strip():
            raise ValueError(f"No text extracted from {pdf_path}")

        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def detect_sections(text: str) -> Dict[str, int]:
    """
    Detect section headers in the text using regex (case-insensitive).

    Args:
        text: Full document text

    Returns:
        Dictionary mapping section name to character position in text
    """
    from config import SECTION_HEADERS

    sections = {}

    for section in SECTION_HEADERS:
        # Case-insensitive search for section headers
        # Match header with optional whitespace, but don't require line boundaries
        pattern = rf"\b{re.escape(section)}\b"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            sections[section.lower()] = match.start()
        else:
            logger.warning(f"Section '{section}' not found in document")

    return sections


def extract_section(text: str, section_name: str) -> str:
    """
    Extract text for a specific section from start to next section.

    Args:
        text: Full document text
        section_name: Name of section to extract

    Returns:
        Text content of the section, or empty string if not found
    """
    sections = detect_sections(text)
    section_lower = section_name.lower()

    if section_lower not in sections:
        logger.warning(f"Section '{section_name}' not found")
        return ""

    start_pos = sections[section_lower]

    # Find next section position
    end_pos = len(text)
    for other_section, pos in sections.items():
        if pos > start_pos:
            end_pos = min(end_pos, pos)

    return text[start_pos:end_pos].strip()


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using tiktoken.

    Args:
        text: Text to estimate tokens for

    Returns:
        Approximate token count
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.warning(f"Error counting tokens: {e}. Using char-based estimate.")
        return len(text) // 4


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 128) -> List[str]:
    """
    Split text into chunks with overlap, respecting sentence boundaries.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens
        overlap: Overlap between chunks in tokens

    Returns:
        List of text chunks
    """
    # Estimate chars per token (rough: 4 chars per token)
    chars_per_token = 4
    chunk_chars = chunk_size * chars_per_token
    overlap_chars = overlap * chars_per_token

    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)

    current_chunk = ""

    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence

        if estimate_tokens(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
            # Save current chunk if not empty
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Start new chunk with overlap from previous chunk
            if chunks:
                # Get last overlap_chars from previous chunk
                overlap_text = chunks[-1][-overlap_chars:] if len(chunks[-1]) > overlap_chars else chunks[-1]
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def pipeline_pdf_to_chunks(pdf_path: str) -> Dict:
    """
    End-to-end pipeline: extract → detect sections → chunk text.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with raw text, sections, chunks, and metadata
    """
    # Extract text
    raw_text = extract_text_from_pdf(pdf_path)

    # Detect sections
    section_positions = detect_sections(raw_text)
    sections = {}
    for section_name in section_positions.keys():
        sections[section_name] = extract_section(raw_text, section_name)

    # Chunk text
    chunks = chunk_text(raw_text)

    # Generate metadata
    total_tokens = estimate_tokens(raw_text)
    avg_tokens_per_chunk = total_tokens / len(chunks) if chunks else 0

    return {
        "raw_text": raw_text,
        "sections": sections,
        "chunks": chunks,
        "metadata": {
            "num_pages": len(raw_text.split("\n")) // 30,  # rough estimate
            "total_chars": len(raw_text),
            "total_tokens": total_tokens,
            "num_chunks": len(chunks),
            "avg_tokens_per_chunk": avg_tokens_per_chunk,
        }
    }
