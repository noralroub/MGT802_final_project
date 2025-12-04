"""Configuration file for the Medical Abstract Generator project."""

# PDF Parsing Configuration
CHUNK_SIZE = 1024  # tokens
CHUNK_OVERLAP = 128  # tokens
CHARS_PER_TOKEN = 4  # rough estimate for token counting

# Section headers to detect (case-insensitive)
SECTION_HEADERS = [
    "abstract",
    "background",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusions",
    "references",
]

# Paths
DATA_DIR = "data"
PAPERS_DIR = "data/papers"
DEBUG_OUTPUT_DIR = "data/debug_output"
TEST_PDF_PATH = "data/papers/NEJMoa2307563.pdf"
