"""Debug script to test the QA system."""

import json
from core.qa import QASystem
from config import TEST_PDF_PATH

# Sample questions for cardiovascular trial
SAMPLE_QUESTIONS = [
    "What was the primary cardiovascular outcome?",
    "How many patients were enrolled in the trial?",
    "What was the main adverse event reported?",
    "What dose of semaglutide was used?",
    "What were the inclusion criteria for the trial?",
    "What was the hazard ratio for the primary outcome?",
    "What are the results comparing semaglutide to placebo?",
]


def main():
    print("=" * 80)
    print("QA SYSTEM DEBUG SCRIPT")
    print("=" * 80)

    # Initialize QA system
    print("\n[1] Initializing QA system...")
    try:
        qa = QASystem(pdf_path=TEST_PDF_PATH, model="gpt-3.5-turbo")
        print("✓ QA system initialized")
        print(f"  System info: {qa.get_system_info()}")
    except Exception as e:
        print(f"✗ Error initializing QA system: {e}")
        print("  Make sure OPENAI_API_KEY is set in .env file")
        return

    # Test individual questions
    print("\n[2] Testing individual questions...")
    print("=" * 80)

    qa_results = []

    for i, question in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 80)

        try:
            result = qa.generate_answer_with_sources(question, top_k=3)

            # Display answer
            print(f"\nAnswer:\n{result['answer']}\n")

            # Display sources
            print(f"Sources used ({result['num_sources']}):")
            for source in result.get('sources', []):
                print(f"  [{source['source_id']}] Relevance: {source['similarity']:.2%}")
                print(f"      {source['preview']}\n")

            # Token usage
            if result.get('tokens_used'):
                print(f"Tokens used: {result['tokens_used']}")

            qa_results.append({
                "question": question,
                "answer": result["answer"],
                "num_sources": result["num_sources"],
                "tokens_used": result.get("tokens_used")
            })

        except Exception as e:
            print(f"✗ Error answering question: {e}")
            qa_results.append({
                "question": question,
                "error": str(e)
            })

    # Save results to JSON
    print("\n[3] Saving results to JSON...")
    output_path = "data/debug_output/qa_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "model": "gpt-3.5-turbo",
            "num_questions": len(SAMPLE_QUESTIONS),
            "results": qa_results
        }, f, indent=2)

    print(f"✓ Results saved to {output_path}")

    # Summary statistics
    print("\n[4] Summary Statistics")
    print("=" * 80)
    successful = sum(1 for r in qa_results if "answer" in r and "error" not in r)
    total_tokens = sum(r.get("tokens_used", 0) for r in qa_results if "tokens_used" in r)

    print(f"Questions answered: {successful}/{len(SAMPLE_QUESTIONS)}")
    if total_tokens:
        print(f"Total tokens used: {total_tokens}")
        print(f"Avg tokens per question: {total_tokens / successful:.0f}")

    print("\n✓ QA debug script completed!")


if __name__ == "__main__":
    main()
