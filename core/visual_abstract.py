"""Visual abstract generator - composes infographic from all components."""

from PIL import Image, ImageDraw, ImageFont
import io
from typing import Dict, Any, Tuple
from utils.data_extraction import TrialDataExtractor
from utils.layout_designer import LayoutDesigner
from utils.chart_builder import ChartBuilder


class VisualAbstractGenerator:
    """Generate visual abstract infographic from trial data."""

    def __init__(self, qa_results_path: str = None, layout_type: str = "horizontal_3panel"):
        """
        Initialize visual abstract generator.

        Args:
            qa_results_path: Path to QA results JSON file
            layout_type: Type of layout to use
        """
        self.extractor = TrialDataExtractor()
        self.designer = LayoutDesigner(layout_type)
        self.builder = ChartBuilder()
        self.trial_data = None
        self.image = None

        if qa_results_path:
            qa_results = self.extractor.load_qa_results(qa_results_path)
            self.trial_data = self.extractor.extract_key_metrics(qa_results)

    def load_trial_data(self, qa_results_path: str) -> None:
        """Load trial data from QA results."""
        qa_results = self.extractor.load_qa_results(qa_results_path)
        self.trial_data = self.extractor.extract_key_metrics(qa_results)

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
        trial = self.trial_data['trial_info']

        # Fill background
        draw.rectangle(
            [(header['x'], header['y']), (header['x'] + header['width'], header['y'] + header['height'])],
            fill=header['bg_color']
        )

        # Title
        title_font = self._get_font(self.designer.get_typography().title_size)
        title_y = header['y'] + 15
        title_text = trial['title'].upper()

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
        pub_text = f"{trial['publication']} | {trial['trial_name']}"
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

        pop = self.trial_data['population']
        icon = self.designer.get_section("population")['icon']

        text = f"""{icon} POPULATION
n = {pop['total_enrolled']:,}
Drug: {pop['drug_arm']:,}
Placebo: {pop['placebo_arm']:,}
Age: {pop['age_mean']:.1f} yrs"""

        self._draw_text_in_section(draw, "population", text)

    def _draw_outcome_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw primary outcome section."""
        self._draw_section_box(draw, "outcome")

        outcome = self.trial_data['primary_outcome']
        icon = self.designer.get_section("outcome")['icon']

        text = f"""{icon} PRIMARY OUTCOME
HR: {outcome['hazard_ratio']:.2f}
CI: {outcome['ci_lower']:.2f}-{outcome['ci_upper']:.2f}
P: {outcome['p_value']}
Events: {outcome['semaglutide_rate']:.1f}%
vs {outcome['placebo_rate']:.1f}%"""

        self._draw_text_in_section(draw, "outcome", text)

    def _draw_adverse_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw adverse events section."""
        self._draw_section_box(draw, "adverse")

        ae = self.trial_data['adverse_events']
        icon = self.designer.get_section("adverse")['icon']

        disc = ae['discontinuation']
        gi = ae['gastrointestinal']

        text = f"""{icon} ADVERSE EVENTS
Discontinuation:
{disc['drug']:.1f}% vs {disc['placebo']:.1f}%
GI Symptoms:
{gi['drug']:.1f}% vs {gi['placebo']:.1f}%"""

        self._draw_text_in_section(draw, "adverse", text)

    def _draw_treatment_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw treatment section."""
        self._draw_section_box(draw, "treatment")

        dosing = self.trial_data['dosing']
        icon = self.designer.get_section("treatment")['icon']

        text = f"""{icon} TREATMENT
Dose: {dosing['dose']} {dosing['frequency']}
At Target: {dosing['at_target_percent']:.0f}%"""

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

        bw = self.trial_data['body_weight']

        section = self.designer.get_section("body_weight")
        font = self._get_font(self.designer.get_typography().section_header_size)
        label_font = self._get_font(self.designer.get_typography().label_size)

        x = section['x'] + 15
        y = section['y'] + 15

        # Title
        draw.text((x, y), "BODY WEIGHT CHANGE", font=font, fill=self.designer.get_colors().primary_text)
        y += 30

        # Content
        text = f"Semaglutide: {bw['semaglutide_change']:.2f}%"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)
        y += 25

        text = f"Placebo: {bw['placebo_change']:.2f}%"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)
        y += 25

        text = f"Difference: {bw['difference']:.2f} percentage points"
        draw.text((x, y), text, font=label_font, fill=self.designer.get_colors().primary_text)

    def _draw_conclusion_section(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw conclusion section."""
        self._draw_section_box(draw, "conclusion")

        section = self.designer.get_section("conclusion")
        font = self._get_font(self.designer.get_typography().label_size)

        x = section['x'] + 15
        y = section['y'] + 15
        line_height = 22

        conclusions = [
            "✓ Semaglutide superior to placebo for CV outcomes",
            "✓ Significant weight reduction achieved",
            "⚠ GI side effects more common with drug"
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
