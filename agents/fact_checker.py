"""Fact Checker - Simple validation of extracted numbers.

Validates that extracted numbers are in realistic ranges for cardiovascular trials.
No LLM calls - just rule-based validation.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class FactChecker:
    """Validates extracted numbers are realistic.

    Performs basic sanity checks on extracted numerical data:
    - Population sizes > 0
    - Hazard ratios in reasonable range (0.01-10)
    - P-values between 0-1
    - Percentages between 0-100
    - Ages between 0-120
    """

    def __init__(self):
        """Initialize fact checker."""
        self.issues = []

    def validate(self, extracted_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Validate extracted data.

        Args:
            extracted_data: Dict with all extracted information from agents

        Returns:
            Tuple of (extracted_data, list of validation issues found)
        """
        self.issues = []

        # Check design data
        self._check_population_size(extracted_data)

        # Check results data
        self._check_results_data(extracted_data)

        return extracted_data, self.issues

    def _extract_value(self, field: Any) -> Any:
        """Get raw value from ReAct-style field dicts."""
        if isinstance(field, dict):
            return field.get("value")
        return field

    def _check_population_size(self, data: Dict[str, Any]) -> None:
        """Check population size is realistic."""
        design = data.get('design', {})
        pop_size = self._extract_value(design.get('population_size'))
        if isinstance(pop_size, str):
            try:
                pop_size = int(pop_size.replace(",", "").strip())
            except ValueError:
                pop_size = None

        if pop_size is not None:
            if pop_size <= 0:
                self.issues.append("Population size must be > 0")
            elif pop_size > 1000000:
                self.issues.append(f"Population size unusually large: {pop_size}")

    def _check_results_data(self, data: Dict[str, Any]) -> None:
        """Check results data for obvious errors."""
        results = data.get('results', {})
        main_finding = self._extract_value(results.get('main_finding', ''))

        # Extract numbers from main finding and validate
        if main_finding:
            self._check_numbers_in_text(main_finding)

    def _check_numbers_in_text(self, text: str) -> None:
        """Extract and validate numbers from text."""
        import re

        if not text:
            return

        # Look for hazard ratios (HR = X.XX)
        hr_pattern = r'(?:HR|hazard\s+ratio)[:\s]+([0-9.]+)'
        for match in re.finditer(hr_pattern, text, re.IGNORECASE):
            try:
                hr = float(match.group(1))
                if hr <= 0 or hr > 10:
                    self.issues.append(
                        f"Hazard ratio {hr} outside typical range (0.01-10)"
                    )
            except ValueError:
                pass

        # Look for p-values (p = X.XXX or p<0.05)
        p_pattern = r'(?:p|P)\s*[=<>]\s*0\.([0-9]+)'
        for match in re.finditer(p_pattern, text):
            try:
                p_val = float('0.' + match.group(1))
                if p_val < 0 or p_val > 1:
                    self.issues.append(
                        f"P-value {p_val} outside valid range (0-1)"
                    )
            except ValueError:
                pass

        # Look for percentages
        pct_pattern = r'(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(pct_pattern, text):
            try:
                pct = float(match.group(1))
                if pct < 0 or pct > 100:
                    self.issues.append(
                        f"Percentage {pct}% outside valid range (0-100)"
                    )
            except ValueError:
                pass

        # Look for ages
        age_pattern = r'(?:age|aged)\s+(\d+)'
        for match in re.finditer(age_pattern, text, re.IGNORECASE):
            try:
                age = int(match.group(1))
                if age < 0 or age > 120:
                    self.issues.append(
                        f"Age {age} outside valid range (0-120)"
                    )
            except ValueError:
                pass

    def get_summary(self) -> str:
        """Get human-readable summary of validation results."""
        if not self.issues:
            return "✓ All numerical values passed validation"

        summary = "⚠ Validation issues found:\n"
        for issue in self.issues:
            summary += f"  - {issue}\n"

        return summary
