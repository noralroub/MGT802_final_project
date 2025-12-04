"""Chart building module for creating simple visualizations."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from typing import Dict, Any, Tuple, List
import numpy as np


class ChartBuilder:
    """Build simple charts for infographic."""

    def __init__(self):
        """Initialize chart builder."""
        self.drug_color = (31, 119, 180)  # Blue (0-255 scale)
        self.placebo_color = (255, 127, 14)  # Orange (0-255 scale)
        self.drug_color_norm = tuple(c / 255 for c in self.drug_color)  # Normalized for matplotlib
        self.placebo_color_norm = tuple(c / 255 for c in self.placebo_color)

    def _create_figure(self, figsize: Tuple[float, float] = (8, 4)) -> Tuple[plt.Figure, plt.Axes]:
        """Create matplotlib figure with white background."""
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
        fig.patch.set_facecolor('white')
        ax.patch.set_facecolor('white')
        return fig, ax

    def create_event_rate_chart(self, semaglutide_rate: float, placebo_rate: float) -> BytesIO:
        """
        Create side-by-side bar chart for event rates.

        Args:
            semaglutide_rate: Event rate for semaglutide (percentage)
            placebo_rate: Event rate for placebo (percentage)

        Returns:
            BytesIO object containing chart image
        """
        fig, ax = self._create_figure((6, 4))

        categories = ['Semaglutide', 'Placebo']
        values = [semaglutide_rate, placebo_rate]
        colors = [self.drug_color_norm, self.placebo_color_norm]

        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{value:.1f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Event Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylim(0, max(values) * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()

        # Save to bytes
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)

        return buffer

    def create_body_weight_chart(self, semaglutide_change: float, placebo_change: float) -> BytesIO:
        """
        Create bar chart for body weight changes.

        Args:
            semaglutide_change: Weight change for semaglutide (percentage)
            placebo_change: Weight change for placebo (percentage)

        Returns:
            BytesIO object containing chart image
        """
        fig, ax = self._create_figure((6, 4))

        categories = ['Semaglutide', 'Placebo']
        values = [semaglutide_change, placebo_change]
        colors = [self.drug_color_norm, self.placebo_color_norm]

        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            y_pos = height if height > 0 else height
            va = 'bottom' if height > 0 else 'top'
            ax.text(bar.get_x() + bar.get_width() / 2., y_pos,
                   f'{value:.2f}%',
                   ha='center', va=va, fontsize=14, fontweight='bold')

        ax.set_ylabel('Weight Change (%)', fontsize=12, fontweight='bold')
        ax.axhline(y=0, color='black', linewidth=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()

        # Save to bytes
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)

        return buffer

    def create_population_pie_chart(self, drug_count: int, placebo_count: int) -> BytesIO:
        """
        Create simple pie chart for population breakdown.

        Args:
            drug_count: Number of patients in drug arm
            placebo_count: Number of patients in placebo arm

        Returns:
            BytesIO object containing chart image
        """
        fig, ax = self._create_figure((6, 4))

        sizes = [drug_count, placebo_count]
        labels = [f'Semaglutide\n({drug_count:,})', f'Placebo\n({placebo_count:,})']
        colors = [self.drug_color_norm, self.placebo_color_norm]

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})

        # Style autopct text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        ax.set_title('Population Distribution', fontsize=12, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save to bytes
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)

        return buffer

    def format_hazard_ratio_text(self, hr: float, ci_lower: float, ci_upper: float, p_value: str) -> str:
        """
        Format hazard ratio with confidence interval and p-value.

        Args:
            hr: Hazard ratio value
            ci_lower: CI lower bound
            ci_upper: CI upper bound
            p_value: P-value string

        Returns:
            Formatted text string
        """
        return f"HR: {hr:.2f}\n(95% CI: {ci_lower:.2f}–{ci_upper:.2f})\nP-value: {p_value}"

    def format_percentage_text(self, label: str, value: float) -> str:
        """Format percentage value as text."""
        return f"{label}: {value:.1f}%"

    def create_adverse_events_table(self) -> str:
        """
        Create formatted text for adverse events.

        Returns:
            Formatted text for adverse events
        """
        text = """ADVERSE EVENTS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Discontinuation:    16.6% vs 8.2%
Gastrointestinal:   10.0% vs 2.0%
Serious Events:      6.5% vs 8.0%
"""
        return text

    def create_demographics_table(self, n_total: int, n_drug: int, n_placebo: int,
                                 age: float, bmi: int) -> str:
        """
        Create formatted text for demographics.

        Returns:
            Formatted text for demographics
        """
        text = f"""POPULATION CHARACTERISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Enrolled:       {n_total:,}
  • Semaglutide:      {n_drug:,}
  • Placebo:          {n_placebo:,}
Mean Age:            {age:.1f} years
BMI Requirement:     ≥{bmi}
"""
        return text

    def save_chart_to_file(self, buffer: BytesIO, filepath: str) -> None:
        """Save chart buffer to file."""
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())

    def get_chart_bytes(self, buffer: BytesIO) -> bytes:
        """Get chart as bytes."""
        return buffer.getvalue()
