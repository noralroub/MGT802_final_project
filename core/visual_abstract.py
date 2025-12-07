"""Visual abstract generator - composes infographic from all components."""

from PIL import Image, ImageDraw, ImageFont
import io
from typing import Dict, Any, Tuple, List
from utils.data_extraction import TrialDataExtractor
from utils.layout_designer import LayoutDesigner
from utils.chart_builder import ChartBuilder


class VisualAbstractGenerator:
    """Generate visual abstract infographic from trial data."""

    def __init__(self, qa_results_path: str = None, layout_type: str = "modern_card", trial_data: Dict[str, Any] = None):
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
        self.trial_data = self._normalize_trial_data(trial_data) if trial_data else None
        self.image = None

        if qa_results_path and trial_data is None:
            qa_results = self.extractor.load_qa_results(qa_results_path)
            self.trial_data = self._normalize_trial_data(self.extractor.extract_key_metrics(qa_results))

    def load_trial_data(self, qa_results_path: str) -> None:
        """Load trial data from QA results."""
        qa_results = self.extractor.load_qa_results(qa_results_path)
        self.trial_data = self._normalize_trial_data(self.extractor.extract_key_metrics(qa_results))

    def set_trial_data(self, trial_data: Dict[str, Any]) -> None:
        """Set trial data directly (already structured)."""
        self.trial_data = self._normalize_trial_data(trial_data)

    def _normalize_trial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize LLM output into the keys the renderer expects.
        Handles common variations like 'effect' vs 'effect_measure' and fills safe defaults.
        """
        if not data:
            return {}

        normalized = {}

        trial = data.get("trial_info", {})
        normalized["trial_info"] = {
            "title": trial.get("title") or trial.get("trial_title") or "",
            "drug": trial.get("drug") or trial.get("intervention") or "",
            "indication": trial.get("indication") or "",
            "trial_name": trial.get("trial_name") or trial.get("name") or "",
            "publication": trial.get("publication") or trial.get("journal") or "",
        }

        pop = data.get("population", {})
        normalized["population"] = {
            "total_enrolled": pop.get("total_enrolled") or pop.get("n_enrolled"),
            "arm_1_label": pop.get("arm_1_label") or pop.get("arm1_label") or pop.get("arm_1") or "Arm 1",
            "arm_1_size": pop.get("arm_1_size") or pop.get("arm1_size"),
            "arm_2_label": pop.get("arm_2_label") or pop.get("arm2_label") or pop.get("arm_2") or "Arm 2",
            "arm_2_size": pop.get("arm_2_size") or pop.get("arm2_size"),
            "age_mean": pop.get("age_mean") or pop.get("mean_age"),
        }

        primary = data.get("primary_outcome", {})
        normalized["primary_outcome"] = {
            "label": primary.get("label") or primary.get("name") or "Primary outcome",
            "effect_measure": primary.get("effect_measure") or primary.get("effect") or primary.get("definition"),
            "estimate": primary.get("estimate") or primary.get("hazard_ratio") or primary.get("value"),
            "ci": primary.get("ci") or primary.get("confidence_interval"),
            "p_value": primary.get("p_value") or primary.get("p"),
        }

        events = data.get("event_rates", {})
        normalized["event_rates"] = {
            "arm_1_percent": events.get("arm_1_percent") or events.get("arm1_percent") or events.get("arm_1") or events.get("arm1"),
            "arm_2_percent": events.get("arm_2_percent") or events.get("arm2_percent") or events.get("arm_2") or events.get("arm2"),
        }

        ae = data.get("adverse_events", {})
        normalized["adverse_events"] = {
            "summary": ae.get("summary") or "",
            "notable": ae.get("notable") or ae.get("details") or [],
        }

        dosing = data.get("dosing", {})
        normalized["dosing"] = {
            "description": dosing.get("description") or dosing.get("dosing") or "",
        }

        bw = data.get("body_weight", {})
        normalized["body_weight"] = {
            "arm_1_change_percent": bw.get("arm_1_change_percent") or bw.get("arm1_change_percent"),
            "arm_2_change_percent": bw.get("arm_2_change_percent") or bw.get("arm2_change_percent"),
        }

        conclusions = data.get("conclusions") or data.get("conclusion") or []
        if isinstance(conclusions, str):
            conclusions = [conclusions]
        normalized["conclusions"] = conclusions

        return normalized

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get system font or default."""
        try:
            # Try to use default system fonts
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except (OSError, IOError):
            # Fallback to default PIL font
            return ImageFont.load_default()

    def _wrap_text(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont,
                   max_width: int) -> List[str]:
        """Word-wrap helper for modern layout text blocks."""
        if not text:
            return []

        words = text.split()
        lines: List[str] = []
        current = ""

        for word in words:
            test_line = (current + " " + word).strip()
            line_width = draw.textlength(test_line, font=font)

            if line_width <= max_width:
                current = test_line
            else:
                # If even a single word is too long, still add what we have
                if current:
                    lines.append(current)
                    current = word
                else:
                    # Word is too long, add it anyway (will overflow slightly)
                    lines.append(word)
                    current = ""

        if current:
            lines.append(current)
        return lines

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

    def _draw_modern_template(self, draw: ImageDraw.ImageDraw) -> None:
        """Render the modern reference-inspired layout."""
        sections = self.designer.get_all_sections()
        theme = self.designer.get_theme_tokens()

        trial = self.trial_data.get("trial_info", {}) if self.trial_data else {}
        population = self.trial_data.get("population", {}) if self.trial_data else {}
        primary = self.trial_data.get("primary_outcome", {}) if self.trial_data else {}
        events = self.trial_data.get("event_rates", {}) if self.trial_data else {}
        adverse = self.trial_data.get("adverse_events", {}) if self.trial_data else {}
        dosing = self.trial_data.get("dosing", {}) if self.trial_data else {}
        conclusions = self.trial_data.get("conclusions", []) if self.trial_data else []

        card = sections["card"]
        header = sections["header"]
        hero = sections["hero"]
        left_col = sections["left_column"]
        right_col = sections["right_column"]
        results_box = sections["results_box"]
        chart_section = sections["chart"]
        footer = sections["footer"]

        # Card base
        card_rect = [card["x"], card["y"], card["x"] + card["width"], card["y"] + card["height"]]
        draw.rounded_rectangle(
            card_rect,
            radius=card.get("radius", 10),
            fill=theme.get("white"),
            outline=theme.get("navy_dark"),
            width=3
        )

        # Header bar
        header_rect = [header["x"], header["y"], header["x"] + header["width"], header["y"] + header["height"]]
        draw.rectangle(header_rect, fill=theme.get("navy_dark"))
        label_font = self._get_font(20)
        title_font = self._get_font(28)
        label_text = (trial.get("trial_name") or trial.get("drug") or "STUDY").upper()
        title_text = trial.get("title") or "Clinical Trial Summary"

        label_width = draw.textlength(label_text, font=label_font) + 24
        label_rect = [
            header["x"] + 16,
            header["y"] + 12,
            header["x"] + 16 + label_width,
            header["y"] + header["height"] - 12,
        ]
        draw.rounded_rectangle(label_rect, radius=10, fill=theme.get("red_primary"))
        draw.text((label_rect[0] + 12, label_rect[1] + 6), label_text, font=label_font, fill=theme.get("white"))
        title_width = header["width"] - (label_width + 80)
        title_lines = self._wrap_text(draw, title_text, title_font, max(title_width, 200))
        text_y = header["y"] + 18
        for line in title_lines[:2]:
            draw.text(
                (label_rect[2] + 16, text_y),
                line,
                font=title_font,
                fill=theme.get("white")
            )
            text_y += 32

        # Hero section
        hero_rect = [hero["x"], hero["y"], hero["x"] + hero["width"], hero["y"] + hero["height"]]
        draw.rectangle(hero_rect, fill=theme.get("red_primary"))
        heart_x = hero["x"] + 40
        heart_y = hero["y"] + 35
        circle_r = 32
        left_circle = (heart_x, heart_y, heart_x + 2 * circle_r, heart_y + 2 * circle_r)
        right_circle = (heart_x + circle_r, heart_y, heart_x + 3 * circle_r, heart_y + 2 * circle_r)
        triangle = [
            (heart_x - 5, heart_y + circle_r),
            (heart_x + 3 * circle_r + 5, heart_y + circle_r),
            (heart_x + 1.5 * circle_r, heart_y + 3 * circle_r)
        ]
        draw.ellipse(left_circle, fill=theme.get("red_dark"), outline=theme.get("white"), width=2)
        draw.ellipse(right_circle, fill=theme.get("red_dark"), outline=theme.get("white"), width=2)
        draw.polygon(triangle, fill=theme.get("red_dark"), outline=theme.get("white"))
        hero_font = self._get_font(24)
        hero_text = conclusions[0] if conclusions else "Main finding or conclusion highlighted here."
        available_width = hero["width"] - (heart_x + 3 * circle_r - hero["x"]) - 60
        hero_lines = self._wrap_text(draw, hero_text, hero_font, int(available_width))
        text_x = heart_x + 3 * circle_r + 20
        text_y = hero["y"] + 35
        for line in hero_lines[:4]:
            draw.text((text_x, text_y), line, font=hero_font, fill=theme.get("white"))
            text_y += 32

        # Left column
        left_padding = left_col.get("padding", 30)
        intro_text = self._build_intro_text(trial, population)
        intro_font = self._get_font(20)
        intro_lines = self._wrap_text(draw, intro_text, intro_font, left_col["width"] - 2 * left_padding)
        cursor_y = left_col["y"] + left_padding
        for line in intro_lines:
            draw.text(
                (left_col["x"] + left_padding, cursor_y),
                line,
                font=intro_font,
                fill=theme.get("gray_text")
            )
            cursor_y += 28
        cursor_y += 12
        pill_rect = [
            left_col["x"] + left_padding,
            cursor_y,
            left_col["x"] + left_col["width"] - left_padding,
            cursor_y + 42
        ]
        draw.rounded_rectangle(pill_rect, radius=20, fill=theme.get("navy_dark"))
        pill_text = "STUDY POPULATION"
        pill_font = self._get_font(20)
        pill_text_x = pill_rect[0] + (
            (pill_rect[2] - pill_rect[0]) - draw.textlength(pill_text, font=pill_font)
        ) / 2
        draw.text((pill_text_x, pill_rect[1] + 7), pill_text, font=pill_font, fill=theme.get("white"))
        cursor_y = pill_rect[3] + 20

        stat_font = self._get_font(32)
        stat_label_font = self._get_font(18)
        stat_box_width = (left_col["width"] - 2 * left_padding - 20) // 2
        stats = [
            (str(population.get("total_enrolled") or "n/a"), "Total Participants"),
            (str(population.get("age_mean") or "n/a"), "Mean Age"),
        ]
        for idx, (value, label) in enumerate(stats):
            x = left_col["x"] + left_padding + idx * (stat_box_width + 20)
            draw.text((x, cursor_y), value, font=stat_font, fill=theme.get("navy_dark"))
            draw.text((x, cursor_y + 38), label, font=stat_label_font, fill=theme.get("gray_text"))
        cursor_y += 100

        row_font = self._get_font(19)
        icon_rows = [
            ("M", dosing.get("description") or "Dosing not specified"),
            ("30d", adverse.get("summary") or "No adverse events summarized."),
        ]
        for label, text in icon_rows:
            badge_rect = [
                left_col["x"] + left_padding,
                cursor_y,
                left_col["x"] + left_padding + 50,
                cursor_y + 50
            ]
            draw.rounded_rectangle(badge_rect, radius=12, fill=theme.get("gray_light"))
            draw.text(
                (badge_rect[0] + 10, badge_rect[1] + 10),
                label,
                font=self._get_font(20),
                fill=theme.get("navy_dark")
            )
            wrapped = self._wrap_text(draw, text, row_font, left_col["width"] - 2 * left_padding - 70)
            text_y = cursor_y + 8
            for line in wrapped:
                draw.text(
                    (badge_rect[2] + 12, text_y),
                    line,
                    font=row_font,
                    fill=theme.get("gray_text")
                )
                text_y += 26
            cursor_y = max(cursor_y + 60, text_y + 4)

        # Right column background
        draw.rectangle(
            [right_col["x"], right_col["y"], right_col["x"] + right_col["width"], right_col["y"] + right_col["height"]],
            fill=theme.get("gray_light")
        )

        # Results box
        res_rect = [results_box["x"], results_box["y"], results_box["x"] + results_box["width"],
                    results_box["y"] + results_box["height"]]
        draw.rounded_rectangle(res_rect, radius=results_box.get("radius", 12), fill=theme.get("white"),
                               outline=theme.get("red_primary"), width=3)
        header_rect = [res_rect[0], res_rect[1], res_rect[2], res_rect[1] + 50]
        draw.rounded_rectangle(header_rect, radius=results_box.get("radius", 12), fill=theme.get("red_primary"))
        header_font = self._get_font(24)
        header_text = "RESULTS"
        header_x = res_rect[0] + (results_box["width"] - draw.textlength(header_text, font=header_font)) / 2
        draw.text((header_x, res_rect[1] + 12), header_text, font=header_font, fill=theme.get("white"))

        content_y = res_rect[1] + 65
        primary_font = self._get_font(24)
        draw.text((res_rect[0] + 20, content_y), primary.get("label", "Primary Outcome"),
                  font=primary_font, fill=theme.get("red_primary"))
        content_y += 34
        detail_font = self._get_font(20)
        details = [
            f"Effect: {primary.get('effect_measure') or 'n/a'}",
            f"Estimate: {primary.get('estimate') or 'n/a'}",
            f"CI: {primary.get('ci') or 'n/a'} | P: {primary.get('p_value') or 'n/a'}",
        ]
        detail_width = results_box["width"] - 40
        for detail in details:
            for line in self._wrap_text(draw, detail, detail_font, detail_width):
                draw.text((res_rect[0] + 20, content_y), line, font=detail_font, fill=theme.get("gray_text"))
                content_y += 26
            content_y += 4

        bullet_items = adverse.get("notable") or conclusions[:4] or ["No additional findings provided."]
        bullet_font = self._get_font(20)
        for item in bullet_items[:4]:
            draw.text((res_rect[0] + 20, content_y), "✗", font=bullet_font, fill=theme.get("red_primary"))
            wrapped_item = self._wrap_text(draw, item, detail_font, detail_width - 40)
            line_y = content_y
            for line in wrapped_item:
                draw.text((res_rect[0] + 48, line_y), line, font=detail_font, fill=theme.get("gray_text"))
                line_y += 24
            content_y = line_y + 4

        # Chart section
        chart_rect = [chart_section["x"], chart_section["y"], chart_section["x"] + chart_section["width"],
                      chart_section["y"] + chart_section["height"]]
        draw.rounded_rectangle(chart_rect, radius=chart_section.get("radius", 12), fill=theme.get("white"))
        chart_title = "Event Rates"
        chart_font = self._get_font(22)
        draw.text((chart_rect[0] + 20, chart_rect[1] + 16), chart_title, font=chart_font, fill=theme.get("navy_dark"))

        bars = []
        arm1_pct = self._safe_percentage(events.get("arm_1_percent"))
        arm2_pct = self._safe_percentage(events.get("arm_2_percent"))
        if arm1_pct is not None:
            bars.append((population.get("arm_1_label", "Arm 1"), arm1_pct,
                         population.get("arm_1_size"), theme.get("bar_blue")))
        if arm2_pct is not None:
            bars.append((population.get("arm_2_label", "Arm 2"), arm2_pct,
                         population.get("arm_2_size"), theme.get("bar_red")))
        if not bars:
            bars.append(("Group", 50, None, theme.get("bar_gray")))

        bar_y = chart_rect[1] + 65
        bar_label_font = self._get_font(20)
        bar_value_font = self._get_font(20)
        for label, value, n_value, color in bars:
            draw.text((chart_rect[0] + 20, bar_y), label, font=bar_label_font, fill=theme.get("gray_text"))
            container_x = chart_rect[0] + 150
            container_width = chart_rect[2] - container_x - 90
            container_rect = [container_x, bar_y - 5, container_x + container_width, bar_y + 28]
            draw.rounded_rectangle(container_rect, radius=12, fill=theme.get("gray_light"))
            fill_width = container_width * min(max(value, 0), 100) / 100
            draw.rounded_rectangle(
                [container_x, bar_y - 5, container_x + fill_width, bar_y + 28],
                radius=12,
                fill=color
            )
            value_text = f"{value:.0f}%"
            text_width = draw.textlength(value_text, font=bar_value_font)
            if fill_width > text_width + 16:
                text_x = container_x + fill_width - text_width - 8
                text_color = theme.get("white")
            else:
                text_x = container_x + fill_width + 10
                text_color = color
            draw.text((text_x, bar_y + 2), value_text, font=bar_value_font, fill=text_color)
            sample_text = f"N = {int(n_value):,}" if isinstance(n_value, (int, float)) else "N = n/a"
            draw.text((chart_rect[2] - 80, bar_y + 2), sample_text, font=bar_label_font, fill=theme.get("gray_text"))
            bar_y += 50

        # Footer
        footer_rect = [footer["x"], footer["y"], footer["x"] + footer["width"], footer["y"] + footer["height"]]
        draw.rectangle(footer_rect, fill=theme.get("navy_dark"))
        footer_font = self._get_font(18)
        footer_text = f"{trial.get('publication', 'Journal')} | {trial.get('trial_name', '')}".strip(" |")
        draw.text((footer_rect[0] + 18, footer_rect[1] + 14), footer_text, font=footer_font, fill=theme.get("white"))

    def _build_intro_text(self, trial: Dict[str, Any], population: Dict[str, Any]) -> str:
        """Compose intro paragraph for modern layout."""
        indication = trial.get("indication") or "patients"
        arm1 = population.get("arm_1_label", "Arm 1")
        arm2 = population.get("arm_2_label", "Arm 2")
        total = population.get("total_enrolled") or "n/a"
        drug = trial.get("drug") or "intervention"
        title = trial.get("title", "This study")
        return (
            f"{title} compared {arm1} vs {arm2} in {indication}. "
            f"{total} participants evaluated the impact of {drug}."
        )

    def _safe_percentage(self, value: Any) -> Any:
        """Ensure a numeric percentage is returned when possible."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        text = str(value).replace("%", "").strip()
        try:
            return float(text)
        except ValueError:
            return None

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
        if self.designer.layout_type == "modern_card":
            background = self.designer.get_theme_tokens().get("gray_light", (245, 245, 245))
        else:
            background = self.designer.get_colors().background
        self.image = Image.new('RGB', (width, height), color=background)
        draw = ImageDraw.Draw(self.image)

        if self.designer.layout_type == "modern_card":
            self._draw_modern_template(draw)
        else:
            # Draw sections for classic layout
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
 
