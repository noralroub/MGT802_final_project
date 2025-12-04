"""Layout design module for infographic composition."""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class Dimensions:
    """Image dimensions in pixels."""
    width: int = 1400
    height: int = 1800
    margin: int = 40
    padding: int = 20
    line_height: int = 24
    col_width: int = (1400 - 120) // 3  # 3 columns with margins


@dataclass
class Colors:
    """Color scheme for infographic."""
    background: Tuple[int, int, int] = (255, 255, 255)  # White
    primary_text: Tuple[int, int, int] = (40, 40, 40)  # Dark gray
    secondary_text: Tuple[int, int, int] = (100, 100, 100)  # Medium gray
    border: Tuple[int, int, int] = (200, 200, 200)  # Light gray

    # Section colors
    population_bg: Tuple[int, int, int] = (230, 240, 255)  # Light blue
    outcome_bg: Tuple[int, int, int] = (230, 255, 240)  # Light green
    adverse_bg: Tuple[int, int, int] = (255, 245, 230)  # Light orange
    treatment_bg: Tuple[int, int, int] = (245, 230, 255)  # Light purple

    # Chart colors
    drug_bar: Tuple[int, int, int] = (31, 119, 180)  # Blue
    placebo_bar: Tuple[int, int, int] = (255, 127, 14)  # Orange
    highlight: Tuple[int, int, int] = (214, 39, 40)  # Red


@dataclass
class Typography:
    """Font settings."""
    title_size: int = 28
    section_header_size: int = 16
    label_size: int = 13
    value_size: int = 14
    small_size: int = 11


class LayoutDesigner:
    """Design and position layout for infographic."""

    def __init__(self, layout_type: str = "horizontal_3panel"):
        """
        Initialize layout designer.

        Args:
            layout_type: Type of layout ("horizontal_3panel" or "vertical_stacked")
        """
        self.layout_type = layout_type
        self.dims = Dimensions()
        self.colors = Colors()
        self.typo = Typography()
        self.sections = self._define_sections()

    def _define_sections(self) -> Dict[str, Dict[str, Any]]:
        """Define section positions and dimensions for horizontal 3-panel layout."""
        if self.layout_type == "horizontal_3panel":
            return self._horizontal_3panel_layout()
        elif self.layout_type == "vertical_stacked":
            return self._vertical_stacked_layout()
        else:
            raise ValueError(f"Unknown layout type: {self.layout_type}")

    def _horizontal_3panel_layout(self) -> Dict[str, Dict[str, Any]]:
        """Define horizontal 3-panel layout (recommended)."""
        col_width = self.dims.col_width
        margin = self.dims.margin
        padding = self.dims.padding

        return {
            # Header section (full width)
            "header": {
                "x": margin,
                "y": margin,
                "width": self.dims.width - 2 * margin,
                "height": 120,
                "bg_color": (50, 50, 100),  # Dark blue
                "text_color": (255, 255, 255),  # White
            },

            # Three-column section (Population | Outcome | Adverse Events)
            "population": {
                "x": margin,
                "y": margin + 140,
                "width": col_width,
                "height": 350,
                "bg_color": self.colors.population_bg,
                "icon": "👥",
            },
            "outcome": {
                "x": margin + col_width + padding,
                "y": margin + 140,
                "width": col_width,
                "height": 350,
                "bg_color": self.colors.outcome_bg,
                "icon": "🎯",
            },
            "adverse": {
                "x": margin + 2 * (col_width + padding),
                "y": margin + 140,
                "width": col_width,
                "height": 350,
                "bg_color": self.colors.adverse_bg,
                "icon": "⚠️",
            },

            # Treatment section (full width)
            "treatment": {
                "x": margin,
                "y": margin + 500,
                "width": self.dims.width - 2 * margin,
                "height": 180,
                "bg_color": self.colors.treatment_bg,
                "icon": "💊",
            },

            # Body Weight section (full width)
            "body_weight": {
                "x": margin,
                "y": margin + 700,
                "width": self.dims.width - 2 * margin,
                "height": 250,
                "bg_color": (245, 245, 245),  # Light gray
            },

            # Conclusion section (full width)
            "conclusion": {
                "x": margin,
                "y": margin + 970,
                "width": self.dims.width - 2 * margin,
                "height": 150,
                "bg_color": (245, 250, 245),  # Very light green
            },

            # Footer
            "footer": {
                "x": margin,
                "y": self.dims.height - 60,
                "width": self.dims.width - 2 * margin,
                "height": 40,
                "text_color": (150, 150, 150),
            },
        }

    def _vertical_stacked_layout(self) -> Dict[str, Dict[str, Any]]:
        """Define vertical stacked layout."""
        margin = self.dims.margin
        full_width = self.dims.width - 2 * margin

        return {
            # Header (full width)
            "header": {
                "x": margin,
                "y": margin,
                "width": full_width,
                "height": 100,
                "bg_color": (50, 50, 100),
                "text_color": (255, 255, 255),
            },
            # Stack sections vertically
            "population": {
                "x": margin,
                "y": margin + 120,
                "width": full_width,
                "height": 140,
                "bg_color": self.colors.population_bg,
                "icon": "👥",
            },
            "outcome": {
                "x": margin,
                "y": margin + 280,
                "width": full_width,
                "height": 140,
                "bg_color": self.colors.outcome_bg,
                "icon": "🎯",
            },
            "adverse": {
                "x": margin,
                "y": margin + 440,
                "width": full_width,
                "height": 140,
                "bg_color": self.colors.adverse_bg,
                "icon": "⚠️",
            },
            "treatment": {
                "x": margin,
                "y": margin + 600,
                "width": full_width,
                "height": 140,
                "bg_color": self.colors.treatment_bg,
                "icon": "💊",
            },
            "body_weight": {
                "x": margin,
                "y": margin + 760,
                "width": full_width,
                "height": 200,
                "bg_color": (245, 245, 245),
            },
            "conclusion": {
                "x": margin,
                "y": margin + 980,
                "width": full_width,
                "height": 120,
                "bg_color": (245, 250, 245),
            },
            "footer": {
                "x": margin,
                "y": self.dims.height - 60,
                "width": full_width,
                "height": 40,
                "text_color": (150, 150, 150),
            },
        }

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get layout information for a section."""
        if section_name not in self.sections:
            raise ValueError(f"Unknown section: {section_name}")
        return self.sections[section_name]

    def get_all_sections(self) -> Dict[str, Dict[str, Any]]:
        """Get all sections."""
        return self.sections

    def get_image_dimensions(self) -> Tuple[int, int]:
        """Get total image dimensions."""
        return (self.dims.width, self.dims.height)

    def get_colors(self) -> Colors:
        """Get color scheme."""
        return self.colors

    def get_typography(self) -> Typography:
        """Get typography settings."""
        return self.typo

    def debug_layout(self) -> str:
        """Print debug info about layout."""
        info = f"""
Layout Type: {self.layout_type}
Image Size: {self.dims.width}x{self.dims.height}

Sections:
"""
        for section_name, section_info in self.sections.items():
            info += f"  {section_name}: x={section_info.get('x')}, y={section_info.get('y')}, "
            info += f"w={section_info.get('width')}, h={section_info.get('height')}\n"
        return info
