"""Debug script to test the RAG retrieval pipeline."""

import json
from core.retrieval import RAGPipeline
from config import TEST_PDF_PATH

# Test queries for a cardiovascular trial paper
TEST_QUERIES = [
    "What was the primary cardiovascular outcome?",
    "How many patients were enrolled in the trial?",
    "What was the main inclusion criteria?",
    "What are the adverse events reported?",
    "What dose of semaglutide was used?",
]


def main():
    print("=" * 80)
    print("RAG RETRIEVAL DEBUG SCRIPT")
    print("=" * 80)

    # Initialize pipeline
    pipeline = RAGPipeline()

    # Ingest PDF
    print("\n[1] Ingesting PDF...")
    ingest_result = pipeline.ingest_pdf(TEST_PDF_PATH)
    print(f"✓ Ingestion successful")
    print(f"  - Chunks: {ingest_result['num_chunks']}")
    print(f"  - Collection info: {pipeline.get_collection_info()}")

    # Test retrieval
    print("\n[2] Testing retrieval with sample queries...")
    print("=" * 80)

    results_log = []

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 80)

        # Get retrieval stats
        stats = pipeline.get_retrieval_stats(query, top_k=3)

        print(f"Retrieved {stats['num_results']} relevant chunks:\n")

        for result in stats["results"]:
            print(f"  Rank #{result['rank']} (similarity: {result['similarity']:.4f})")
            print(f"  Preview: {result['preview']}\n")

        results_log.append({
            "query": query,
            "num_results": stats["num_results"],
            "top_similarity": stats["results"][0]["similarity"] if stats["results"] else None,
            "top_chunk_preview": stats["results"][0]["preview"] if stats["results"] else None
        })

    # Save results to JSON
    print("\n[3] Saving results to JSON...")
    output_path = "data/debug_output/retrieval_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "test_queries": TEST_QUERIES,
            "results": results_log
        }, f, indent=2)

    print(f"✓ Results saved to {output_path}")

    # Summary statistics
    print("\n[4] Summary Statistics")
    print("=" * 80)
    print(f"Total queries tested: {len(TEST_QUERIES)}")
    avg_similarity = sum(r["top_similarity"] for r in results_log if r["top_similarity"]) / len(results_log)
    print(f"Average top similarity score: {avg_similarity:.4f}")

    print("\n✓ Debug script completed successfully!")


if __name__ == "__main__":
    main()
