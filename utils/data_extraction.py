"""Data extraction module for parsing QA answers into structured trial data."""

import logging
import re
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List


logger = logging.getLogger(__name__)


@dataclass
class PopulationData:
    """Structured representation for study population data."""

    total_enrolled: int = 0
    drug_arm: int = 0
    placebo_arm: int = 0
    age_mean: Optional[float] = None
    bmi_minimum: Optional[float] = None

    def to_dict(self) -> Dict[str, Optional[float]]:
        """Return a serializable dictionary."""
        return asdict(self)


@dataclass
class OutcomeData:
    """Primary outcome metrics."""

    definition: str = ""
    hazard_ratio: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    p_value: Optional[str] = None
    semaglutide_rate: Optional[float] = None
    placebo_rate: Optional[float] = None

    def to_dict(self) -> Dict[str, Optional[float]]:
        return asdict(self)


@dataclass
class EventPair:
    """Helper structure for paired percentages (drug vs placebo)."""

    drug: Optional[float] = None
    placebo: Optional[float] = None


@dataclass
class AdverseEventRates:
    """Collection of adverse-event statistics."""

    discontinuation: EventPair = field(default_factory=EventPair)
    gastrointestinal: EventPair = field(default_factory=EventPair)
    serious_adverse: EventPair = field(default_factory=EventPair)

    def to_dict(self) -> Dict[str, Dict[str, Optional[float]]]:
        return {
            'discontinuation': asdict(self.discontinuation),
            'gastrointestinal': asdict(self.gastrointestinal),
            'serious_adverse': asdict(self.serious_adverse),
        }


@dataclass
class DosingData:
    """Structured dosing summary."""

    dose: Optional[str] = None
    frequency: Optional[str] = None
    at_target_percent: Optional[float] = None

    def to_dict(self) -> Dict[str, Optional[float]]:
        return asdict(self)


@dataclass
class BodyWeightData:
    """Body weight change summary."""

    semaglutide_change: Optional[float] = None
    placebo_change: Optional[float] = None
    difference: Optional[float] = None

    def to_dict(self) -> Dict[str, Optional[float]]:
        return asdict(self)


@dataclass
class TrialInfo:
    """High-level metadata about the clinical trial."""

    title: str = 'Clinical Trial Visual Abstract'
    drug: str = 'Investigational Therapy'
    indication: str = 'Indication not specified'
    trial_name: str = 'Clinical Study'
    publication: str = 'Publication not specified'

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class TrialDataExtractor:
    """Extract structured trial data from QA answers."""

    def __init__(self):
        """Initialize the extractor with regex patterns."""
        self.patterns = {
            # Patient counts
            'total_patients': r'(\d+(?:,\d+)*)\s+patients',
            'drug_arm': r'(\d+(?:,\d+)*)\s+(?:patients\s+)?assigned to receive',
            'placebo_arm': r'(\d+(?:,\d+)*)\s+(?:patients\s+)?assigned to receive placebo',

            # Demographics
            'age': r'(\d+(?:\.\d+)?)\s+years?(?:\s+old)?|age[:\s]+(\d+(?:\.\d+)?)',
            'female_percent': r'(?:female|women).*?(\d+(?:\.\d+)?)%',
            'male_percent': r'(?:male|men).*?(\d+(?:\.\d+)?)%',
            'bmi': r'BMI.*?(\d+(?:\.\d+)?)',

            # Outcomes
            'hazard_ratio': r'(?:HR|hazard\s+ratio)[:\s]+(\d+(?:\.\d+)?)',
            'ci_lower': r'95%\s*CI[:\s]*(\d+(?:\.\d+)?)',
            'ci_upper': r'(\d+(?:\.\d+)?)\)(?:\s*for|,|\.)',
            'p_value': r'[pP](?:\s*[=-]|value)[:\s]*(?:less than\s+)?(<?\s*0\.0*)?(\d+)',

            # Event rates
            'semaglutide_rate': r'semaglutide.*?(\d+(?:\.\d+)?)%',
            'placebo_rate': r'placebo.*?(\d+(?:\.\d+)?)%',

            # Body weight
            'weight_change_drug': r'semaglutide[:\s]*(-?\d+(?:\.\d+)?)%',
            'weight_change_placebo': r'placebo[:\s]*(-?\d+(?:\.\d+)?)%',
            'weight_difference': r'(?:difference|treatment\s+difference)[:\s]*(-?\d+(?:\.\d+)?)\s*percentage\s+points',

            # Adverse events
            'discontinuation_drug': r'discontinuation[:\s]*(\d+(?:\.\d+)?)%(?:\s+[a-z]*)?(?:semaglutide|drug)',
            'discontinuation_placebo': r'discontinuation[:\s]*(\d+(?:\.\d+)?)%(?:\s+[a-z]*)?(?:placebo)',
            'gi_drug': r'(?:GI|gastrointestinal).*?semaglutide[:\s]*(\d+(?:\.\d+)?)%',
            'gi_placebo': r'(?:GI|gastrointestinal).*?placebo[:\s]*(\d+(?:\.\d+)?)%',
            'serious_adverse_drug': r'(?:serious\s+)?adverse\s+events.*?semaglutide[:\s]*(\d+(?:\.\d+)?)%',
            'serious_adverse_placebo': r'(?:serious\s+)?adverse\s+events.*?placebo[:\s]*(\d+(?:\.\d+)?)%',

            # Dosing
            'dose': r'dose[:\s]*(\d+(?:\.\d+)?)\s*mg',
            'frequency': r'(\w+(?:\s+\w+)?)\s*(?:per\s+week|weekly|daily)',
            'at_target': r'(\d+(?:\.\d+)?)%\s+(?:of\s+)?(?:patients\s+)?(?:receiving\s+)?(?:semaglutide\s+)?(?:at|taking).*?target\s+dose',
        }

        # Question keywords used to locate answers within QA results
        self.question_topics = {
            'primary_outcome': ["primary cardiovascular outcome", "primary outcome"],
            'enrollment': ["how many patients", "patients were enrolled", "population size"],
            'adverse_events': ["adverse event", "adverse events"],
            'dosing': ["dose", "dosing", "dosage"],
            'inclusion': ["inclusion criteria", "inclusion and exclusion"],
            'hazard_ratio': ["hazard ratio"],
            'comparison': ["comparing", "versus", "vs", "compare"],
        }

    def _get_results_list(self, qa_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate QA results payload and normalize into list format."""
        if not isinstance(qa_results, dict):
            raise ValueError("QA results must be a dictionary with a 'results' field")

        entries = qa_results.get('results')
        if isinstance(entries, list):
            return entries

        if isinstance(entries, dict):
            return [
                {'question': question, 'answer': answer}
                for question, answer in entries.items()
            ]

        raise ValueError("QA results missing 'results' list; cannot extract trial data")

    def _find_answer(self, qa_results: Dict[str, Any], topic: str) -> str:
        """Retrieve the answer text for a topic based on keyword matching."""
        keywords = self.question_topics.get(topic, [])
        if not keywords:
            logger.warning("No keywords configured for topic '%s'", topic)
            return ""

        for entry in self._get_results_list(qa_results):
            question_text = (entry.get('question') or '').lower()
            if any(keyword in question_text for keyword in keywords):
                answer_text = entry.get('answer')
                if isinstance(answer_text, str):
                    return answer_text.strip()

        logger.warning("No QA answer found for topic '%s'", topic)
        return ""

    def extract_number(self, text: str, pattern: str) -> Optional[float]:
        """Extract first number matching pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Get first non-None group
            for group in match.groups():
                if group is not None:
                    # Remove commas and convert to float
                    clean = str(group).replace(',', '')
                    try:
                        return float(clean)
                    except ValueError:
                        continue
        return None

    def extract_text_section(self, text: str, start_keyword: str, end_keyword: Optional[str] = None) -> str:
        """Extract text between two keywords."""
        start_idx = text.lower().find(start_keyword.lower())
        if start_idx == -1:
            return ""

        if end_keyword:
            end_idx = text.lower().find(end_keyword.lower(), start_idx)
            if end_idx == -1:
                return text[start_idx:]
            return text[start_idx:end_idx]
        return text[start_idx:]

    def extract_demographics(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract population/demographic information."""
        enrollment_answer = self._find_answer(qa_results, 'enrollment')
        inclusion_answer = self._find_answer(qa_results, 'inclusion')

        total_enrolled = self.extract_number(enrollment_answer, self.patterns['total_patients'])
        drug_arm = self.extract_number(enrollment_answer, r'(\d+(?:,\d+)*)\s+patients?\s+(?:assigned\s+)?to receive\s+([\w\s-]+)')
        placebo_arm = self.extract_number(enrollment_answer, r'(\d+(?:,\d+)*)\s+patients?\s+(?:assigned\s+)?to receive\s+placebo')

        arm_counts = re.finditer(
            r'(\d+(?:,\d+)*)\s+(?:were\s+)?(?:assigned\s+)?to\s+(?:receive|the)\s+([\w\s-]+?)(?=(?:\s+(?:and|vs|versus|compared)|[.,;]|$))',
            enrollment_answer,
            re.IGNORECASE
        )

        drug_arm_value = None
        placebo_arm_value = None
        for match in arm_counts:
            count = int(match.group(1).replace(',', ''))
            label = match.group(2).strip().lower()
            if 'placebo' in label:
                placebo_arm_value = count
            elif drug_arm_value is None:
                drug_arm_value = count

        demographics = PopulationData(
            total_enrolled=int(total_enrolled) if total_enrolled is not None else 0,
            drug_arm=drug_arm_value if drug_arm_value is not None else int(drug_arm) if drug_arm is not None else 0,
            placebo_arm=placebo_arm_value if placebo_arm_value is not None else int(placebo_arm) if placebo_arm is not None else 0,
            age_mean=self.extract_number(inclusion_answer, self.patterns['age']),
            bmi_minimum=self.extract_number(inclusion_answer, self.patterns['bmi'])
        )

        return demographics.to_dict()

    def extract_outcomes(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract primary outcome information."""
        outcome_question_answer = self._find_answer(qa_results, 'primary_outcome')
        hazard_ratio_answer = self._find_answer(qa_results, 'hazard_ratio')
        comparison_answer = self._find_answer(qa_results, 'comparison')

        hr_match = re.search(r'(\d+(?:\.\d+)?)\s*\(95%\s*CI[,\s]*(\d+(?:\.\d+)?)[–\-](\d+(?:\.\d+)?)\)', hazard_ratio_answer, re.IGNORECASE)
        p_match = re.search(r'p(?:\s*[=-]|\s*value)?\s*(<?\s*0?\.\d+)', hazard_ratio_answer, re.IGNORECASE)
        serious_ae_match = re.search(r'serious\s+adverse\s+events.*?(\d+(?:\.\d+)?)%.*?(\d+(?:\.\d+)?)%', comparison_answer, re.IGNORECASE)

        outcomes = OutcomeData(
            definition=outcome_question_answer,
            hazard_ratio=float(hr_match.group(1)) if hr_match else None,
            ci_lower=float(hr_match.group(2)) if hr_match else None,
            ci_upper=float(hr_match.group(3)) if hr_match else None,
            p_value=p_match.group(1).replace(' ', '') if p_match else None,
            semaglutide_rate=float(serious_ae_match.group(1)) if serious_ae_match else None,
            placebo_rate=float(serious_ae_match.group(2)) if serious_ae_match else None,
        )

        return outcomes.to_dict()

    def extract_adverse_events(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract adverse event information."""
        ae_answer = self._find_answer(qa_results, 'adverse_events')
        comparison_answer = self._find_answer(qa_results, 'comparison')

        adverse_events = AdverseEventRates(
            discontinuation=EventPair(
                drug=self.extract_number(ae_answer, self.patterns['discontinuation_drug']),
                placebo=self.extract_number(ae_answer, self.patterns['discontinuation_placebo'])
            ),
            gastrointestinal=EventPair(
                drug=self.extract_number(ae_answer, self.patterns['gi_drug']),
                placebo=self.extract_number(ae_answer, self.patterns['gi_placebo'])
            ),
            serious_adverse=EventPair(
                drug=self.extract_number(comparison_answer, self.patterns['serious_adverse_drug']),
                placebo=self.extract_number(comparison_answer, self.patterns['serious_adverse_placebo'])
            ),
        )

        return adverse_events.to_dict()

    def extract_dosing(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dosing information."""
        dose_answer = self._find_answer(qa_results, 'dosing')

        dose_value = self.extract_number(dose_answer, self.patterns['dose'])
        frequency_match = re.search(self.patterns['frequency'], dose_answer or '', re.IGNORECASE)

        dosing = DosingData(
            dose=f"{dose_value:.1f} mg" if dose_value is not None else None,
            frequency=frequency_match.group(1).lower() if frequency_match else None,
            at_target_percent=self.extract_number(dose_answer, self.patterns['at_target'])
        )

        return dosing.to_dict()

    def extract_body_weight(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract body weight change information."""
        comparison_answer = self._find_answer(qa_results, 'comparison')

        # Parse body weight changes
        bw_match = re.search(
            r'body\s+weight.*?semaglutide.*?(-?\d+(?:\.\d+)?)%.*?placebo.*?(-?\d+(?:\.\d+)?)%',
            comparison_answer,
            re.IGNORECASE | re.DOTALL
        )

        body_weight = BodyWeightData(
            semaglutide_change=float(bw_match.group(1)) if bw_match else None,
            placebo_change=float(bw_match.group(2)) if bw_match else None,
        )

        if body_weight.semaglutide_change is not None and body_weight.placebo_change is not None:
            body_weight.difference = body_weight.semaglutide_change - body_weight.placebo_change

        return body_weight.to_dict()

    def extract_key_metrics(self, qa_results: Dict) -> Dict[str, Any]:
        """Extract all key metrics into structured format."""
        # Validate QA results structure upfront for clearer errors
        self._get_results_list(qa_results)

        trial_data = {
            'trial_info': self.extract_trial_info(qa_results),
            'population': self.extract_demographics(qa_results),
            'primary_outcome': self.extract_outcomes(qa_results),
            'adverse_events': self.extract_adverse_events(qa_results),
            'dosing': self.extract_dosing(qa_results),
            'body_weight': self.extract_body_weight(qa_results),
        }

        return trial_data

    def extract_trial_info(self, qa_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build trial info section from QA metadata, avoiding hard-coded defaults."""
        metadata = qa_results.get('metadata') or {}

        publication = metadata.get('publication') or metadata.get('journal')
        if publication and metadata.get('year'):
            publication = f"{publication} {metadata['year']}"

        default_info = TrialInfo()
        trial_info = TrialInfo(
            title=metadata.get('title') or qa_results.get('trial_title') or default_info.title,
            drug=metadata.get('drug') or metadata.get('intervention') or default_info.drug,
            indication=metadata.get('indication') or metadata.get('condition') or default_info.indication,
            trial_name=metadata.get('trial_name') or metadata.get('study') or default_info.trial_name,
            publication=publication or default_info.publication,
        )

        return trial_info.to_dict()

    @staticmethod
    def load_qa_results(filepath: str) -> Dict:
        """Load QA results from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_trial_data(trial_data: Dict, filepath: str) -> None:
        """Save extracted trial data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(trial_data, f, indent=2)


def extract_trial_data_from_qa(qa_results_path: str) -> Dict[str, Any]:
    """Main function to extract trial data from QA results."""
    extractor = TrialDataExtractor()
    qa_results = extractor.load_qa_results(qa_results_path)
    trial_data = extractor.extract_key_metrics(qa_results)
    return trial_data
