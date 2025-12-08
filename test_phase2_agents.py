"""Quick test of Phase 2 agents - verify imports and basic functionality."""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test all agents import successfully."""
    print("\n🧪 Testing Phase 2 Agent Imports...")

    try:
        from agents.summary_agent import SummaryAgent
        print("  ✓ SummaryAgent")
    except Exception as e:
        print(f"  ✗ SummaryAgent: {e}")
        return False

    try:
        from agents.combiner_agent import CombinerAgent
        print("  ✓ CombinerAgent")
    except Exception as e:
        print(f"  ✗ CombinerAgent: {e}")
        return False

    try:
        from agents.metadata_agent import MetadataAgent
        print("  ✓ MetadataAgent")
    except Exception as e:
        print(f"  ✗ MetadataAgent: {e}")
        return False

    try:
        from agents.background_agent import BackgroundAgent
        print("  ✓ BackgroundAgent")
    except Exception as e:
        print(f"  ✗ BackgroundAgent: {e}")
        return False

    try:
        from agents.design_agent import DesignAgent
        print("  ✓ DesignAgent")
    except Exception as e:
        print(f"  ✗ DesignAgent: {e}")
        return False

    try:
        from agents.results_agent import ResultsAgent
        print("  ✓ ResultsAgent")
    except Exception as e:
        print(f"  ✗ ResultsAgent: {e}")
        return False

    try:
        from agents.limitations_agent import LimitationsAgent
        print("  ✓ LimitationsAgent")
    except Exception as e:
        print(f"  ✗ LimitationsAgent: {e}")
        return False

    try:
        from agents.fact_checker import FactChecker
        print("  ✓ FactChecker")
    except Exception as e:
        print(f"  ✗ FactChecker: {e}")
        return False

    try:
        from agents.phase2_orchestrator import Phase2Orchestrator
        print("  ✓ Phase2Orchestrator")
    except Exception as e:
        print(f"  ✗ Phase2Orchestrator: {e}")
        return False

    return True


def test_agent_creation():
    """Test agent instantiation."""
    print("\n🧪 Testing Agent Instantiation...")

    try:
        from agents.summary_agent import SummaryAgent
        agent = SummaryAgent()
        print("  ✓ SummaryAgent instantiation")
    except Exception as e:
        print(f"  ✗ SummaryAgent instantiation: {e}")
        return False

    try:
        from agents.combiner_agent import CombinerAgent
        agent = CombinerAgent()
        print("  ✓ CombinerAgent instantiation")
    except Exception as e:
        print(f"  ✗ CombinerAgent instantiation: {e}")
        return False

    try:
        from agents.metadata_agent import MetadataAgent
        agent = MetadataAgent()
        print("  ✓ MetadataAgent instantiation")
    except Exception as e:
        print(f"  ✗ MetadataAgent instantiation: {e}")
        return False

    try:
        from agents.fact_checker import FactChecker
        checker = FactChecker()
        print("  ✓ FactChecker instantiation")
    except Exception as e:
        print(f"  ✗ FactChecker instantiation: {e}")
        return False

    try:
        from agents.phase2_orchestrator import Phase2Orchestrator
        orchestrator = Phase2Orchestrator()
        print("  ✓ Phase2Orchestrator instantiation")
    except Exception as e:
        print(f"  ✗ Phase2Orchestrator instantiation: {e}")
        return False

    return True


def test_fact_checker():
    """Test fact checker validation logic."""
    print("\n🧪 Testing FactChecker Validation...")

    from agents.fact_checker import FactChecker

    checker = FactChecker()

    # Test with sample data
    test_data = {
        'metadata': {
            'title': 'Test Study',
            'population_size': 1000
        },
        'design': {
            'population_size': 1000
        },
        'results': {
            'main_finding': 'HR 0.74 (95% CI 0.58-0.95), p=0.017'
        }
    }

    extracted, issues = checker.validate(test_data)

    if not issues:
        print("  ✓ Valid data passes validation")
    else:
        print(f"  ✗ Valid data has issues: {issues}")
        return False

    # Test with invalid data
    bad_data = {
        'design': {
            'population_size': -100
        }
    }

    extracted, issues = checker.validate(bad_data)

    if issues and 'must be > 0' in issues[0]:
        print("  ✓ Invalid data detected correctly")
    else:
        print(f"  ✗ Invalid data not detected: {issues}")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("PHASE 2 AGENTS - INITIALIZATION TESTS")
    print("=" * 70)

    all_pass = True

    # Test imports
    if not test_imports():
        all_pass = False

    # Test instantiation
    if not test_agent_creation():
        all_pass = False

    # Test fact checker
    if not test_fact_checker():
        all_pass = False

    print("\n" + "=" * 70)
    if all_pass:
        print("✅ ALL PHASE 2 AGENT TESTS PASSED!")
        print("\nNext: Integrate orchestrator into app.py")
    else:
        print("❌ Some tests failed. Check errors above.")
        return 1

    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
