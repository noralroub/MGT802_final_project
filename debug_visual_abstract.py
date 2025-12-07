"""Debug script for Sprint 4 - Tests full pipeline end-to-end."""

import json
from pathlib import Path
from core.visual_abstract import VisualAbstractGenerator


def main():
    """Test full pipeline with existing QA results."""
    print("\n" + "=" * 70)
    print("SPRINT 4 DEBUG SCRIPT - FULL PIPELINE TEST")
    print("=" * 70)

    # Paths
    qa_results_path = "data/debug_output/qa_results.json"
    output_path = "data/debug_output/trial_abstract.png"

    # Verify input file exists
    print("\n✓ Checking input files...")
    if not Path(qa_results_path).exists():
        print(f"❌ QA results file not found: {qa_results_path}")
        return

    print(f"  ✓ QA results found: {qa_results_path}")

    # Step 1: Initialize generator
    print("\n✓ Step 1: Initializing Visual Abstract Generator...")
    try:
        generator = VisualAbstractGenerator(qa_results_path, layout_type="modern_card")
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
        print(f"    - HR: {outcome['hazard_ratio']} (95% CI: {outcome['ci_lower']}-{outcome['ci_upper']})")
        print(f"    - P-value: {outcome['p_value']}")
        print(f"    - Event rates: {outcome['semaglutide_rate']}% vs {outcome['placebo_rate']}%")

        print(f"  ✓ Body Weight:")
        bw = trial_data['body_weight']
        print(f"    - Semaglutide: {bw['semaglutide_change']}%")
        print(f"    - Placebo: {bw['placebo_change']}%")
        print(f"    - Difference: {bw['difference']} percentage points")

        print(f"  ✓ Adverse Events:")
        ae = trial_data['adverse_events']
        print(f"    - Discontinuation: {ae['discontinuation']['drug']}% vs {ae['discontinuation']['placebo']}%")
        print(f"    - GI Symptoms: {ae['gastrointestinal']['drug']}% vs {ae['gastrointestinal']['placebo']}%")

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
