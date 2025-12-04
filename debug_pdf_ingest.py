"""Debug script to test PDF ingestion pipeline."""

import json
import sys
from core.pdf_ingest import pipeline_pdf_to_chunks
from config import TEST_PDF_PATH

if __name__ == "__main__":
    try:
        pdf_path = TEST_PDF_PATH
        print(f"Processing: {pdf_path}\n")

        result = pipeline_pdf_to_chunks(pdf_path)

        # Output 1: Print metadata
        print("=" * 60)
        print("METADATA")
        print("=" * 60)
        for key, value in result["metadata"].items():
            print(f"{key}: {value}")

        # Output 2: Print sections found
        print("\n" + "=" * 60)
        print("SECTIONS DETECTED")
        print("=" * 60)
        for section, text in result["sections"].items():
            token_estimate = len(text) // 4
            print(f"\n{section.upper()}: {len(text)} chars, ~{token_estimate} tokens")
            print(f"Preview: {text[:150]}...")

        # Output 3: Print first 5 chunks
        print("\n" + "=" * 60)
        print("FIRST 5 CHUNKS")
        print("=" * 60)
        for i, chunk in enumerate(result["chunks"][:5]):
            token_estimate = len(chunk) // 4
            print(f"\n--- CHUNK {i} ({len(chunk)} chars, ~{token_estimate} tokens) ---")
            print(chunk[:300] + "..." if len(chunk) > 300 else chunk)

        # Output 4: Save full result to JSON
        print("\n" + "=" * 60)
        print("SAVING DEBUG OUTPUT")
        print("=" * 60)

        debug_output = {
            "metadata": result["metadata"],
            "sections": {k: len(v) for k, v in result["sections"].items()},
            "sample_chunks": result["chunks"][:3]
        }

        output_path = "data/debug_output/pdf_parsing_result.json"
        with open(output_path, "w") as f:
            json.dump(debug_output, f, indent=2)

        print(f"✓ Full output saved to {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
