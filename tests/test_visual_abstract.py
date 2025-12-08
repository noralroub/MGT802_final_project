"""Unit tests for Sprint 4 visual abstract components."""

import pytest
import json
from pathlib import Path
from PIL import Image
from config import OPENAI_API_KEY

# Skip all tests if API key not configured
pytestmark = pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not configured")


class TestDataExtraction:
    """Test data extraction module."""

    @pytest.fixture
    def extractor(self):
        """Create data extractor instance."""
        from utils.data_extraction import TrialDataExtractor
        return TrialDataExtractor()

    @pytest.fixture
    def qa_results(self, extractor):
        """Load QA results."""
        return extractor.load_qa_results('data/debug_output/qa_results.json')

    def test_extractor_initialization(self, extractor):
        """Test extractor can be initialized."""
        assert extractor is not None
        assert hasattr(extractor, 'extract_key_metrics')

    def test_load_qa_results(self, qa_results):
        """Test QA results can be loaded."""
        assert qa_results is not None
        assert 'results' in qa_results
        assert len(qa_results['results']) == 7

    def test_extract_demographics(self, extractor, qa_results):
        """Test demographic extraction."""
        demo = extractor.extract_demographics(qa_results)

        assert demo['total_enrolled'] == 17604
        assert demo['drug_arm'] == 8803
        assert demo['placebo_arm'] == 8801

    def test_extract_outcomes(self, extractor, qa_results):
        """Test primary outcome extraction."""
        outcomes = extractor.extract_primary_outcome(qa_results)

        assert outcomes['hazard_ratio'] == 0.8
        assert outcomes['ci_lower'] == 0.72
        assert outcomes['ci_upper'] == 0.9
        assert outcomes['p_value'] == 'p < 0.001'

    def test_extract_adverse_events(self, extractor, qa_results):
        """Test adverse event extraction."""
        ae = extractor.extract_adverse_events(qa_results)

        assert 'GI symptoms' in ae['summary']
        assert len(ae['notable']) >= 1

    def test_extract_dosing(self, extractor, qa_results):
        """Test dosing extraction."""
        dosing = extractor.extract_dosing(qa_results)

        assert dosing['dose'] == '2.4 mg'
        assert dosing['frequency'] == 'weekly'
        assert 'Once-weekly' in dosing['description']

    def test_extract_key_metrics(self, extractor, qa_results):
        """Test complete metric extraction."""
        trial_data = extractor.extract_key_metrics(qa_results)

        assert trial_data is not None
        assert 'trial_info' in trial_data
        assert 'population' in trial_data
        assert 'primary_outcome' in trial_data
        assert 'adverse_events' in trial_data


class TestLayoutDesigner:
    """Test layout designer module."""

    @pytest.fixture
    def designer(self):
        """Create layout designer instance."""
        from utils.layout_designer import LayoutDesigner
        return LayoutDesigner("horizontal_3panel")

    def test_designer_initialization(self, designer):
        """Test designer initialization."""
        assert designer is not None
        assert designer.layout_type == "horizontal_3panel"

    def test_get_image_dimensions(self, designer):
        """Test image dimensions."""
        width, height = designer.get_image_dimensions()

        assert width == 1400
        assert height == 1800

    def test_get_sections(self, designer):
        """Test section retrieval."""
        sections = designer.get_all_sections()

        expected_sections = ["header", "population", "outcome", "adverse",
                           "treatment", "body_weight", "conclusion", "footer"]
        for section_name in expected_sections:
            assert section_name in sections

    def test_get_section_properties(self, designer):
        """Test section properties."""
        population_section = designer.get_section("population")

        assert 'x' in population_section
        assert 'y' in population_section
        assert 'width' in population_section
        assert 'height' in population_section
        assert 'bg_color' in population_section

    def test_get_colors(self, designer):
        """Test color scheme."""
        colors = designer.get_colors()

        assert colors.background == (255, 255, 255)
        assert colors.population_bg == (230, 240, 255)
        assert colors.outcome_bg == (230, 255, 240)

    def test_get_typography(self, designer):
        """Test typography settings."""
        typo = designer.get_typography()

        assert typo.title_size == 28
        assert typo.section_header_size == 16
        assert typo.label_size == 13


class TestChartBuilder:
    """Test chart builder module."""

    @pytest.fixture
    def builder(self):
        """Create chart builder instance."""
        from utils.chart_builder import ChartBuilder
        return ChartBuilder()

    def test_builder_initialization(self, builder):
        """Test builder initialization."""
        assert builder is not None
        assert hasattr(builder, 'create_event_rate_chart')

    def test_create_event_rate_chart(self, builder):
        """Test event rate chart creation."""
        chart = builder.create_event_rate_chart(6.5, 8.0)

        assert chart is not None
        chart_bytes = chart.getbuffer().nbytes
        assert chart_bytes > 0

    def test_create_body_weight_chart(self, builder):
        """Test body weight chart creation."""
        chart = builder.create_body_weight_chart(-9.39, -0.88)

        assert chart is not None
        chart_bytes = chart.getbuffer().nbytes
        assert chart_bytes > 0

    def test_create_population_pie_chart(self, builder):
        """Test population pie chart creation."""
        chart = builder.create_population_pie_chart(8803, 8801)

        assert chart is not None
        chart_bytes = chart.getbuffer().nbytes
        assert chart_bytes > 0

    def test_format_hazard_ratio_text(self, builder):
        """Test hazard ratio text formatting."""
        text = builder.format_hazard_ratio_text(0.80, 0.72, 0.90, "<0.001")

        assert "HR: 0.80" in text
        assert "95% CI" in text
        assert "0.72" in text
        assert "0.90" in text

    def test_create_demographics_table(self, builder):
        """Test demographics table creation."""
        text = builder.create_demographics_table(17604, 8803, 8801, 61.6, 27)

        assert "POPULATION CHARACTERISTICS" in text
        assert "17,604" in text
        assert "8,803" in text

    def test_create_adverse_events_table(self, builder):
        """Test adverse events table creation."""
        text = builder.create_adverse_events_table()

        assert "ADVERSE EVENTS SUMMARY" in text
        assert "Discontinuation" in text


class TestVisualAbstractGenerator:
    """Test visual abstract generator module."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        from core.visual_abstract import VisualAbstractGenerator
        return VisualAbstractGenerator("data/debug_output/qa_results.json", layout_type="horizontal_3panel")

    def test_generator_initialization(self, generator):
        """Test generator initialization."""
        assert generator is not None
        assert generator.trial_data is not None

    def test_trial_data_loaded(self, generator):
        """Test trial data is loaded."""
        assert generator.trial_data['trial_info']['title'] is not None
        assert generator.trial_data['population']['total_enrolled'] > 0

    def test_generate_abstract(self, generator):
        """Test infographic generation."""
        image = generator.generate_abstract()

        assert image is not None
        assert isinstance(image, Image.Image)
        assert image.size == (1400, 1800)
        assert image.mode == 'RGB'

    def test_export_as_png(self, generator, tmp_path):
        """Test PNG export."""
        image = generator.generate_abstract()
        output_path = tmp_path / "test_abstract.png"

        generator.export_as_png(str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_as_bytes(self, generator):
        """Test bytes export."""
        image = generator.generate_abstract()
        png_bytes = generator.export_as_bytes()

        assert png_bytes is not None
        assert len(png_bytes) > 0
        # PNG files start with magic bytes
        assert png_bytes[:4] == b'\x89PNG'

    def test_get_image(self, generator):
        """Test get_image method."""
        image = generator.generate_abstract()
        retrieved_image = generator.get_image()

        assert retrieved_image is not None
        assert retrieved_image.size == image.size


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_full_pipeline(self):
        """Test complete pipeline from data to image."""
        from core.visual_abstract import VisualAbstractGenerator

        # Initialize
        generator = VisualAbstractGenerator("data/debug_output/qa_results.json", layout_type="horizontal_3panel")

        # Generate
        image = generator.generate_abstract()

        # Verify
        assert image is not None
        assert image.size == (1400, 1800)
        assert image.mode == 'RGB'

        # Export
        png_bytes = generator.export_as_bytes()
        assert len(png_bytes) > 0
        assert png_bytes[:4] == b'\x89PNG'

    def test_pipeline_with_missing_data(self):
        """Test pipeline handles missing data gracefully."""
        from core.visual_abstract import VisualAbstractGenerator

        # This should not crash even if data is incomplete
        generator = VisualAbstractGenerator("data/debug_output/qa_results.json", layout_type="horizontal_3panel")
        image = generator.generate_abstract()

        assert image is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
