"""Visual abstract generator - composes infographic from all components."""

from PIL import Image, ImageDraw, ImageFont
import io
from typing import Dict, Any, Tuple
from utils.data_extraction import TrialDataExtractor
from utils.layout_designer import LayoutDesigner
from utils.chart_builder import ChartBuilder


class VisualAbstractGenerator:
    """Generate visual abstract infographic from trial data."""

    def __init__(self, qa_results_path: str = None, layout_type: str = "horizontal_3panel", trial_data: Dict[str, Any] = None):
        """
        Initialize visual abstract generator.

        Args:
            qa_results_path: Path to QA results JSON file
            layout_type: Type of layout to use
            trial_data: Pre-computed structured data (bypasses QA parsing)
        """
        self.extractor = TrialDataExtractor()
        self.designer = LayoutDesigner(layout_type)
        self.builder = ChartBuilder()
        self.trial_data = trial_data
        self.image = None

        if qa_results_path and trial_data is None:
            qa_results = self.extractor.load_qa_results(qa_results_path)
            self.trial_data = self.extractor.extract_key_metrics(qa_results)

    def load_trial_data(self, qa_results_path: str) -> None:
        """Load trial data from QA results."""
        qa_results = self.extractor.load_qa_results(qa_results_path)
        self.trial_data = self.extractor.extract_key_metrics(qa_results)

    def set_trial_data(self, trial_data: Dict[str, Any]) -> None:
        """Set trial data directly (already structured)."""
        self.trial_data = trial_data

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get system font or default."""
        try:
            # Try to use default system fonts
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except (OSError, IOError):
            # Fallback to default PIL font
            return ImageFont.load_default()

    def _draw_header(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw header section."""
        header = self.designer.get_section("header")
        trial = self.trial_data.get('trial_info', {}) if self.trial_data else {}

        # Fill background
        draw.rectangle(
            [(header['x'], header['y']), (header['x'] + header['width'], header['y'] + header['height'])],
            fill=header['bg_color']
        )

        # Title
        title_font = self._get_font(self.designer.get_typography().title_size)
        title_y = header['y'] + 15
        title_text = trial.get('title', 'Clinical Trial').upper()

        # Split title if too long
        title_parts = []
        words = title_text.split()
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 60:
                title_parts.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            title_parts.append(' '.join(current_line))

        text_color = header.get('text_color', (255, 255, 255))
        for i, part in enumerate(title_parts[:2]):  # Max 2 lines
            draw.text(
                (header['x'] + 20, title_y + i * 28),
                part,
                font=title_font,
                fill=text_color
            )

        # Publication info
        pub_font = self._get_font(self.designer.get_typography().label_size)
        publication = trial.get('publication', 'Publication')
        trial_name = trial.get('trial_name', trial.get('drug', 'Trial'))
        pub_text = f"{publication} | {trial_name}"
        draw.text(
            (header['x'] + 20, header['y'] + header['height'] - 25),
            pub_text,
            font=pub_font,
            fill=text_color
        )

    def _draw_section_box(self, draw: ImageDraw.ImageDraw, section_name: str) -> None:
        """Draw a section with background and border."""
        section = self.designer.get_section(section_name)

        # Draw background
        draw.rectangle(
            [(section['x'], section['y']),
             (section['x'] + section['width'], section['y'] + section['height'])],
            fill=section.get('bg_color', (255, 255, 255)),
            outline=self.designer.get_colors().border,
            width=1
        )

    def _draw_text_in_section(self, draw: ImageDraw.ImageDraw, section_name: str,
                             text: str, icon: str = "") -> None:
        """Draw text content in a section."""
        section = self.designer.get_section(section_name)
        font = self._get_font(self.designer.get_typography().label_size)
        small_font = self._get_font(self.designer.get_typography().small_size)

        x = section['x'] + 15
        y = section['y'] + 15
        line_height = 20

        # Draw icon if provided
        if icon:
            icon_font = self._get_font(20)
            draw.text((x, y), icon, font=icon_font, fill=self.designer.get_colors().primary_text)
            y += 25

        # Draw text lines
        for line in text.split('\n'):
            if line.strip():
                draw.text((x, y), line.strip(), font=font, fill=self.designer.get_colors().primary_text)
                y += line_height

    def _draw_population_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw population section."""
        self._draw_section_box(draw, "population")

        pop = self.trial_data.get('population', {}) if self.trial_data else {}
        icon = self.designer.get_section("population")['icon']

        total = pop.get('total_enrolled')
        arm1_label = pop.get('arm_1_label', 'Arm 1')
        arm1_size = pop.get('arm_1_size')
        arm2_label = pop.get('arm_2_label', 'Arm 2')
        arm2_size = pop.get('arm_2_size')
        age_mean = pop.get('age_mean')

        lines = [
            f"{icon} POPULATION",
            f"Total: {int(total):,}" if isinstance(total, (int, float)) else f"Total: {total or 'n/a'}",
            f"{arm1_label}: {int(arm1_size):,}" if isinstance(arm1_size, (int, float)) else f"{arm1_label}: {arm1_size or 'n/a'}",
            f"{arm2_label}: {int(arm2_size):,}" if isinstance(arm2_size, (int, float)) else f"{arm2_label}: {arm2_size or 'n/a'}",
            f"Mean age: {age_mean:.1f} yrs" if isinstance(age_mean, (int, float)) else f"Mean age: {age_mean or 'n/a'}",
        ]

        self._draw_text_in_section(draw, "population", "\n".join(lines))

    def _draw_outcome_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw primary outcome section."""
        self._draw_section_box(draw, "outcome")

        outcome = self.trial_data.get('primary_outcome', {}) if self.trial_data else {}
        icon = self.designer.get_section("outcome")['icon']

        label = outcome.get('label', 'Primary outcome')
        effect = outcome.get('effect_measure') or outcome.get('definition') or ""
        estimate = outcome.get('estimate') or outcome.get('hazard_ratio')
        ci = outcome.get('ci') or ""
        p_value = outcome.get('p_value', "")

        text = f"""{icon} {label}
Effect: {effect or 'n/a'}
Estimate: {estimate or 'n/a'}
CI: {ci or 'n/a'}
P: {p_value or 'n/a'}"""

        events = self.trial_data.get('event_rates', {}) if self.trial_data else {}
        arm1 = events.get('arm_1_percent')
        arm2 = events.get('arm_2_percent')
        if arm1 is not None or arm2 is not None:
            text += f"\nEvents: {arm1 or 'n/a'}% vs {arm2 or 'n/a'}%"

        self._draw_text_in_section(draw, "outcome", text)

    def _draw_adverse_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw adverse events section."""
        self._draw_section_box(draw, "adverse")

        ae = self.trial_data.get('adverse_events', {}) if self.trial_data else {}
        icon = self.designer.get_section("adverse")['icon']

        summary = ae.get('summary') or "Adverse events summary unavailable"
        notable = ae.get('notable') or []
        text_lines = [f"{icon} ADVERSE EVENTS", summary]
        text_lines.extend([f"- {item}" for item in notable[:3]])

        self._draw_text_in_section(draw, "adverse", "\n".join(text_lines))

    def _draw_treatment_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw treatment section."""
        self._draw_section_box(draw, "treatment")

        dosing = self.trial_data.get('dosing', {}) if self.trial_data else {}
        icon = self.designer.get_section("treatment")['icon']

        text = f"""{icon} TREATMENT
{dosing.get('description', '').strip() or 'Dosing not specified'}"""

        section = self.designer.get_section("treatment")
        font = self._get_font(self.designer.get_typography().label_size)
        x = section['x'] + 15
        y = section['y'] + 15

        # Draw icon
        icon_font = self._get_font(20)
        draw.text((x, y), icon, font=icon_font, fill=self.designer.get_colors().primary_text)

        # Draw text
        y += 30
        for line in text.split('\n')[1:]:
            draw.text((x, y), line.strip(), font=font, fill=self.designer.get_colors().primary_text)
            y += 22

    def _draw_body_weight_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw body weight section."""
        self._draw_section_box(draw, "body_weight")

        bw = self.trial_data.get('body_weight', {}) if self.trial_data else {}

        section = self.designer.get_section("body_weight")
        font = self._get_font(self.designer.get_typography().section_header_size)
        label_font = self._get_font(self.designer.get_typography().label_size)

        x = section['x'] + 15
        y = section['y'] + 15

        # Title
        draw.text((x, y), "BODY WEIGHT CHANGE", font=font, fill=self.designer.get_colors().primary_text)
        y += 30

        # Content
        arm1_change = bw.get('arm_1_change_percent')
        arm2_change = bw.get('arm_2_change_percent')
        diff = None
        if isinstance(arm1_change, (int, float)) and isinstance(arm2_change, (int, float)):
            diff = arm1_change - arm2_change

        text = f"Arm 1: {arm1_change:.2f}%" if isinstance(arm1_change, (int, float)) else f"Arm 1: {arm1_change or 'n/a'}"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)
        y += 25

        text = f"Arm 2: {arm2_change:.2f}%" if isinstance(arm2_change, (int, float)) else f"Arm 2: {arm2_change or 'n/a'}"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)
        y += 25

        text = f"Difference: {diff:.2f} percentage points" if diff is not None else "Difference: n/a"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)

    def _draw_conclusion_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw conclusion section."""
        self._draw_section_box(draw, "conclusion")

        section = self.designer.get_section("conclusion")
        font = self._get_font(self.designer.get_typography().label_size)

        x = section['x'] + 15
        y = section['y'] + 15
        line_height = 22

        conclusions = self.trial_data.get('conclusions', []) if self.trial_data else []
        if not conclusions:
            conclusions = [
                "✓ Primary outcome favored intervention",
                "✓ Safety acceptable",
                "⚠ Review limitations before applying broadly",
            ]

        for conclusion in conclusions:
            draw.text((x, y), conclusion, font=font, fill=self.designer.get_colors().primary_text)
            y += line_height

    def _draw_footer(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw footer."""
        footer = self.designer.get_section("footer")
        font = self._get_font(self.designer.get_typography().small_size)
        text_color = footer.get('text_color', (150, 150, 150))

        footer_text = "Generated by Medical Visual Abstract System | Data from Semaglutide Trial (NEJM 2023)"
        draw.text(
            (footer['x'] + 10, footer['y'] + 10),
            footer_text,
            font=font,
            fill=text_color
        )

    def generate_abstract(self) -> Image.Image:
        """
        Generate visual abstract infographic.

        Returns:
            PIL Image object
        """
        if not self.trial_data:
            raise ValueError("No trial data loaded. Call load_trial_data() first.")

        # Create image
        width, height = self.designer.get_image_dimensions()
        self.image = Image.new('RGB', (width, height),
                              color=self.designer.get_colors().background)
        draw = ImageDraw.Draw(self.image)

        # Draw sections
        self._draw_header(draw)
        self._draw_population_section(draw)
        self._draw_outcome_section(draw)
        self._draw_adverse_section(draw)
        self._draw_treatment_section(draw)
        self._draw_body_weight_section(draw)
        self._draw_conclusion_section(draw)
        self._draw_footer(draw)

        return self.image

    def export_as_png(self, filepath: str) -> None:
        """
        Export infographic as PNG file.

        Args:
            filepath: Path to save PNG file
        """
        if self.image is None:
            raise ValueError("No image generated. Call generate_abstract() first.")

        self.image.save(filepath, 'PNG', quality=95)

    def export_as_bytes(self) -> bytes:
        """
        Export infographic as bytes.

        Returns:
            PNG image as bytes
        """
        if self.image is None:
            raise ValueError("No image generated. Call generate_abstract() first.")

        buffer = io.BytesIO()
        self.image.save(buffer, 'PNG', quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    def get_image(self) -> Image.Image:
        """Get generated image."""
        if self.image is None:
            raise ValueError("No image generated. Call generate_abstract() first.")
        return self.image
