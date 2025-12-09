"""Image Library Agent - selects abstract visuals from local assets."""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ImageLibraryAgent:
    """Selects the best-fit image thumbnail from the internal library."""

    def __init__(self, image_dir: str = "assets/image_library") -> None:
        self.image_dir = Path(image_dir)
        self.library = self._build_library()

        if not self.image_dir.exists():
            logger.warning("Image directory %s does not exist", self.image_dir)

    def extract(
        self,
        metadata: Dict[str, Any],
        background: Dict[str, Any],
        design: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pick an image and caption based on trial context."""
        metadata = metadata or {}
        background = background or {}
        design = design or {}
        results = results or {}

        description_parts: List[str] = []

        def add_text(value: Any) -> None:
            if isinstance(value, str):
                description_parts.append(value)
            elif isinstance(value, list):
                description_parts.extend([str(item) for item in value if item])

        add_text(metadata.get("title", ""))
        add_text(metadata.get("journal", ""))
        add_text(background.get("background", ""))
        add_text(design.get("intervention", ""))
        add_text(design.get("comparator", ""))
        add_text(design.get("primary_outcomes", []))
        add_text(results.get("main_finding", ""))

        description = " ".join(description_parts).lower()
        match = self._select_image(description)

        return {
            "image_path": str(match.get("path", "")),
            "caption": match.get("caption", "Clinical illustration")
        }

    def _select_image(self, description: str) -> Dict[str, Any]:
        """Score each image by keyword matches, choose best."""
        best = None
        best_score = -1

        for item in self.library:
            keywords = item.get("keywords", [])
            score = sum(description.count(keyword) for keyword in keywords)

            if score > best_score:
                best_score = score
                best = item

        return best or self.library[-1]

    def _build_library(self) -> List[Dict[str, Any]]:
        """Return list of available library assets with metadata."""
        def asset(filename: str, caption: str, keywords: List[str]) -> Dict[str, Any]:
            return {
                "path": self.image_dir / filename,
                "caption": caption,
                "keywords": [k.lower() for k in keywords]
            }

        return [
            asset(
                "anatomical-heart-svgrepo-com.svg",
                "Cardiac / hemodynamic focus",
                ["cardiac", "heart", "myocardial", "hcm", "angiography", "ischemic", "heart failure", "cardiomyopathy"]
            ),
            asset(
                "obesity.svg",
                "Metabolic or obesity-focused intervention",
                ["obesity", "weight", "semaglutide", "glp-1", "metabolic", "diabetes", "bmi"]
            )
        ]
