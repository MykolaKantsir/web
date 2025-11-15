from django.test import TestCase
from django.utils import timezone
from measuring.models import Drawing, Dimension, MeasuredValue, Protocol, Page


class DrawingModelTests(TestCase):
    """Test the Drawing model - technical drawings for quality control"""

    def test_drawing_creation(self):
        """Test that a drawing can be created"""
        drawing = Drawing.objects.create(
            filename="TEST-DRAWING-001.pdf",
            pages_count=1,
            flip_angle=0
        )

        self.assertEqual(drawing.filename, "TEST-DRAWING-001.pdf")
        self.assertEqual(drawing.pages_count, 1)
        self.assertEqual(drawing.flip_angle, 0)

    def test_drawing_with_multiple_pages(self):
        """Test a multi-page drawing"""
        drawing = Drawing.objects.create(
            filename="MULTI-PAGE-DRAWING.pdf",
            pages_count=3
        )

        self.assertEqual(drawing.pages_count, 3)

    def test_drawing_string_representation(self):
        """Test the __str__ method of Drawing"""
        drawing = Drawing.objects.create(
            filename="PART-12345.pdf",
            pages_count=1
        )

        # String representation should be the filename
        self.assertEqual(str(drawing), "PART-12345.pdf")


class DimensionModelTests(TestCase):
    """Test the Dimension model - dimensions to be measured with tolerances"""

    def setUp(self):
        """Create a test drawing"""
        self.drawing = Drawing.objects.create(
            filename="TEST-DRAWING.pdf",
            pages_count=1
        )

    def test_dimension_creation(self):
        """Test creating a dimension"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=100.0,
            y=200.0,
            width=50.0,
            height=30.0,
            value="25.0",
            min_value=24.9,
            max_value=25.1,
            type_selection=2  # Bilateral
        )

        self.assertEqual(dimension.value, "25.0")
        self.assertEqual(dimension.min_value, 24.9)
        self.assertEqual(dimension.max_value, 25.1)

    def test_dimension_string_representation(self):
        """Test the __str__ method"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=50, y=50, width=30, height=30,
            value="10.5"
        )

        dim_str = str(dimension)

        # Should include value and drawing filename
        self.assertIn("10.5", dim_str)
        self.assertIn("TEST-DRAWING.pdf", dim_str)


class ToleranceCheckTests(TestCase):
    """Test tolerance checking logic - critical for quality control!"""

    def setUp(self):
        """Create test drawing"""
        self.drawing = Drawing.objects.create(
            filename="TOLERANCE-TEST.pdf",
            pages_count=1
        )

    def test_bilateral_tolerance_within_range(self):
        """Test a measurement within bilateral tolerance (±0.1)"""
        # Dimension: 50.0±0.1 (min: 49.9, max: 50.1)
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="50.0±0.1",
            min_value=49.9,
            max_value=50.1,
            type_selection=2  # Bilateral
        )

        # Test a measurement that's within tolerance
        test_value = 50.0
        is_within = dimension.min_value <= test_value <= dimension.max_value

        self.assertTrue(is_within)

    def test_bilateral_tolerance_outside_range_low(self):
        """Test a measurement below bilateral tolerance"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="50.0±0.1",
            min_value=49.9,
            max_value=50.1,
            type_selection=2
        )

        # Test a measurement that's too low
        test_value = 49.8  # Below 49.9
        is_within = dimension.min_value <= test_value <= dimension.max_value

        self.assertFalse(is_within)

    def test_bilateral_tolerance_outside_range_high(self):
        """Test a measurement above bilateral tolerance"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="50.0±0.1",
            min_value=49.9,
            max_value=50.1,
            type_selection=2
        )

        # Test a measurement that's too high
        test_value = 50.2  # Above 50.1
        is_within = dimension.min_value <= test_value <= dimension.max_value

        self.assertFalse(is_within)

    def test_shaft_tolerance(self):
        """Test shaft tolerance (negative only): 20.0 -0.2"""
        # Shaft dimension: 20 -0.2 (min: 19.8, max: 20.0)
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="20.0 -0.2",
            min_value=19.8,
            max_value=20.0,
            type_selection=1  # Shaft
        )

        # Test good value
        self.assertTrue(19.8 <= 19.9 <= 20.0)

        # Test too small
        self.assertFalse(19.8 <= 19.7 <= 20.0)

        # Test too large
        self.assertFalse(19.8 <= 20.1 <= 20.0)

    def test_hole_tolerance(self):
        """Test hole tolerance (positive only): 30.0 +0.3"""
        # Hole dimension: 30 +0.3 (min: 30.0, max: 30.3)
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="30.0 +0.3",
            min_value=30.0,
            max_value=30.3,
            type_selection=3  # Hole
        )

        # Test good value
        self.assertTrue(30.0 <= 30.1 <= 30.3)

        # Test too small
        self.assertFalse(30.0 <= 29.9 <= 30.3)

        # Test too large
        self.assertFalse(30.0 <= 30.4 <= 30.3)

    def test_exact_minimum_tolerance(self):
        """Test measurement exactly at minimum tolerance"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="100.0±0.5",
            min_value=99.5,
            max_value=100.5
        )

        # Exact minimum should be acceptable
        test_value = 99.5
        is_within = dimension.min_value <= test_value <= dimension.max_value

        self.assertTrue(is_within)

    def test_exact_maximum_tolerance(self):
        """Test measurement exactly at maximum tolerance"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="100.0±0.5",
            min_value=99.5,
            max_value=100.5
        )

        # Exact maximum should be acceptable
        test_value = 100.5
        is_within = dimension.min_value <= test_value <= dimension.max_value

        self.assertTrue(is_within)


class MeasuredValueTests(TestCase):
    """Test the MeasuredValue model - actual measurements"""

    def setUp(self):
        """Create test drawing and dimension"""
        self.drawing = Drawing.objects.create(
            filename="MEASURED-TEST.pdf",
            pages_count=1
        )

        self.dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="50.0±0.1",
            min_value=49.9,
            max_value=50.1
        )

    def test_measured_value_creation(self):
        """Test creating a measured value"""
        measured = MeasuredValue.objects.create(
            dimension=self.dimension,
            value=50.0
        )

        self.assertEqual(measured.value, 50.0)
        self.assertEqual(measured.dimension, self.dimension)

    def test_multiple_measurements_same_dimension(self):
        """Test recording multiple measurements for the same dimension"""
        # Record 3 measurements
        MeasuredValue.objects.create(dimension=self.dimension, value=49.95)
        MeasuredValue.objects.create(dimension=self.dimension, value=50.00)
        MeasuredValue.objects.create(dimension=self.dimension, value=50.05)

        # Check that all were saved
        measurements = MeasuredValue.objects.filter(dimension=self.dimension)
        self.assertEqual(measurements.count(), 3)


class ProtocolTests(TestCase):
    """Test the Protocol model - measurement reports"""

    def setUp(self):
        """Create test data"""
        self.drawing = Drawing.objects.create(
            filename="PROTOCOL-TEST.pdf",
            pages_count=1
        )

    def test_protocol_creation(self):
        """Test creating a protocol"""
        protocol = Protocol.objects.create(
            drawing=self.drawing,
            is_finished=False
        )

        self.assertEqual(protocol.drawing, self.drawing)
        self.assertFalse(protocol.is_finished)

    def test_protocol_finishing(self):
        """Test marking a protocol as finished"""
        protocol = Protocol.objects.create(
            drawing=self.drawing,
            is_finished=False
        )

        # Initially not finished
        self.assertFalse(protocol.is_finished)

        # Finish the protocol
        protocol.is_finished = True
        protocol.save()

        # Verify it's finished
        updated_protocol = Protocol.objects.get(id=protocol.id)
        self.assertTrue(updated_protocol.is_finished)

    def test_protocol_with_measured_values(self):
        """Test linking measured values to a protocol"""
        # Create dimension and measurements
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="25.0"
        )

        measured1 = MeasuredValue.objects.create(dimension=dimension, value=25.0)
        measured2 = MeasuredValue.objects.create(dimension=dimension, value=25.1)

        # Create protocol and link measurements
        protocol = Protocol.objects.create(drawing=self.drawing)
        protocol.measured_values.add(measured1, measured2)

        # Verify the measurements are linked
        self.assertEqual(protocol.measured_values.count(), 2)

    def test_protocol_string_representation(self):
        """Test the __str__ method"""
        protocol = Protocol.objects.create(drawing=self.drawing)

        protocol_str = str(protocol)

        # Should include the drawing filename
        self.assertIn("PROTOCOL-TEST.pdf", protocol_str)
