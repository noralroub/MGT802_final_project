"""Debug script for Sprint 4 - Tests full pipeline end-to-end."""

import argparse
from pathlib import Path

from agents.extraction_agent import EvidenceExtractorAgent
from core.visual_abstract import VisualAbstractGenerator


def main():
    """Test full pipeline with an uploaded PDF."""
    print("\n" + "=" * 70)
    print("SPRINT 4 DEBUG SCRIPT - FULL PIPELINE TEST")
    print("=" * 70)

    # Paths
    parser = argparse.ArgumentParser(
        description="Generate a visual abstract from a clinical trial PDF."
    )
    parser.add_argument("pdf_path", help="Path to the clinical trial PDF to analyze")
    parser.add_argument(
        "--output",
        help="Destination for the rendered visual abstract PNG",
        default="data/debug_output/trial_abstract.png"
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path
    output_path = args.output


    # Verify input file exists
    print("\n✓ Checking input files...")
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    print(f"  ✓ PDF found: {pdf_path}")

    extractor = EvidenceExtractorAgent()
    print("\n✓ Step 0: Running the extraction pipeline on the PDF...")
    extraction_result = extractor.run_full_extraction(pdf_path)
    visual_data = extraction_result.get("visual_data", {})
    if not visual_data:
        print("❌ Extraction did not produce visual data")
        return

    # Step 1: Initialize generator
    print("\n✓ Step 1: Initializing Visual Abstract Generator...")
    try:
        generator = VisualAbstractGenerator(layout_type="modern_card", trial_data=visual_data)
        print("  ✓ Generator initialized")
        print(f"    - Trial: {generator.trial_data['trial_info']['title']}")
        print(f"    - Publication: {generator.trial_data['trial_info']['publication']}")
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return

    # Step 2: Verify trial data extraction
    print("\n✓ Step 2: Verifying extracted trial data...")
    try:
        trial_data = generator.trial_data

        print(f"  ✓ Population:")
        print(f"    - Total: {trial_data['population']['total_enrolled']:,}")
        print(f"    - Drug: {trial_data['population']['drug_arm']:,}")
        print(f"    - Placebo: {trial_data['population']['placebo_arm']:,}")

        print(f"  ✓ Primary Outcome:")
        outcome = trial_data['primary_outcome']
        event_rates = trial_data.get('event_rates', {})
        print(f"    - HR: {outcome['hazard_ratio']} (95% CI: {outcome['ci_lower']}-{outcome['ci_upper']})")
        print(f"    - P-value: {outcome['p_value']}")
        print(f"    - Event rates: {event_rates.get('arm_1_percent')}% vs {event_rates.get('arm_2_percent')}%")

        print(f"  ✓ Body Weight:")
        bw = trial_data['body_weight']
        print(f"    - Semaglutide: {bw['semaglutide_change']}%")
        print(f"    - Placebo: {bw['placebo_change']}%")
        print(f"    - Difference: {bw['difference']} percentage points")

        print(f"  ✓ Adverse Events:")
        ae = trial_data['adverse_events']
        print(f"    - Summary: {ae.get('summary', 'N/A')}")
        for item in ae.get('notable', []):
            print(f"      • {item}")

    except Exception as e:
        print(f"❌ Failed to verify trial data: {e}")
        return

    # Step 3: Generate infographic
    print("\n✓ Step 3: Generating visual abstract infographic...")
    try:
        image = generator.generate_abstract()
        print(f"  ✓ Infographic generated")
        print(f"    - Image size: {image.size[0]}x{image.size[1]} pixels")
        print(f"    - Image mode: {image.mode}")
    except Exception as e:
        print(f"❌ Failed to generate infographic: {e}")
        return

    # Step 4: Export as PNG
    print(f"\n✓ Step 4: Exporting infographic as PNG...")
    try:
        generator.export_as_png(output_path)
        file_size = Path(output_path).stat().st_size
        print(f"  ✓ Saved to: {output_path}")
        print(f"    - File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    except Exception as e:
        print(f"❌ Failed to export PNG: {e}")
        return

    # Step 5: Export as bytes
    print(f"\n✓ Step 5: Exporting as bytes...")
    try:
        png_bytes = generator.export_as_bytes()
        print(f"  ✓ PNG as bytes: {len(png_bytes):,} bytes")
    except Exception as e:
        print(f"❌ Failed to export as bytes: {e}")
        return

    # Summary
    print("\n" + "=" * 70)
    print("✅ FULL PIPELINE TEST PASSED!")
    print("=" * 70)
    print("\n✓ All steps completed successfully:")
    print("  1. ✓ Generator initialized")
    print("  2. ✓ Trial data extracted")
    print("  3. ✓ Infographic generated")
    print("  4. ✓ Exported as PNG")
    print("  5. ✓ Exported as bytes")

    print(f"\n✓ Output:")
    print(f"  - Visual abstract: {output_path}")
    print(f"  - File size: {file_size/1024:.1f} KB")

    print("\n✓ Next steps:")
    print("  - Run the Streamlit app: streamlit run app_streamlit.py")
    print("  - Or test with more PDFs: python3 debug_visual_abstract.py <pdf_path>")
    print("\n")


if __name__ == "__main__":
    main()
