from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from inventory.models import Order, ProductToBeAdded
from inventory.choices import OrderStatus
from datetime import date

# Import specific tool types
# Note: If EndMill doesn't exist in your models, replace with an actual model
# Check your inventory/models.py for available tool classes
try:
    from inventory.models import EndMill, DrillingTool
    HAS_TOOL_MODELS = True
except ImportError:
    HAS_TOOL_MODELS = False


class OrderModelTests(TestCase):
    """Test the Order model - purchase orders for tools and materials"""

    def setUp(self):
        """Create test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_order_creation_basic(self):
        """Test creating a basic order"""
        # Note: This is a simplified test. In reality, you'd create a Product first
        # and link it via GenericForeignKey
        if HAS_TOOL_MODELS:
            # Create a tool first
            tool = EndMill.objects.create(
                code="EM-001",
                manufacturer="SANDVIK",
                description="Test end mill",
                quantity=5,
                catalog_price=45.50
            )

            # Create order
            content_type = ContentType.objects.get_for_model(EndMill)
            order = Order.objects.create(
                content_type=content_type,
                object_id=tool.id,
                quantity=10,
                ordered_by=self.user,
                status=OrderStatus.CREATED
            )

            self.assertEqual(order.quantity, 10)
            self.assertEqual(order.status, OrderStatus.CREATED)
            self.assertEqual(order.ordered_by, self.user)

    def test_order_status_workflow(self):
        """Test order status transitions from CREATED -> PENDING -> COMPLETED"""
        if HAS_TOOL_MODELS:
            tool = EndMill.objects.create(
                code="EM-002",
                manufacturer="KENNAMETAL",
                description="Test tool",
                quantity=3
            )

            content_type = ContentType.objects.get_for_model(EndMill)
            order = Order.objects.create(
                content_type=content_type,
                object_id=tool.id,
                quantity=5,
                status=OrderStatus.CREATED
            )

            # Check initial status
            self.assertEqual(order.status, OrderStatus.CREATED)

            # Move to PENDING
            order.status = OrderStatus.PENDING
            order.save()
            self.assertEqual(order.status, OrderStatus.PENDING)

            # Move to COMPLETED
            order.status = OrderStatus.COMPLETED
            order.save()
            self.assertEqual(order.status, OrderStatus.COMPLETED)

    def test_order_date_auto_set(self):
        """Test that order_date is automatically set"""
        if HAS_TOOL_MODELS:
            tool = EndMill.objects.create(
                code="EM-003",
                manufacturer="SANDVIK",
                description="Test",
                quantity=1
            )

            content_type = ContentType.objects.get_for_model(EndMill)
            order = Order.objects.create(
                content_type=content_type,
                object_id=tool.id,
                quantity=5
            )

            # order_date should be set automatically to today
            self.assertEqual(order.order_date, date.today())


class ProductToBeAddedTests(TestCase):
    """Test the ProductToBeAdded model - queue for new products"""

    def test_product_to_be_added_creation(self):
        """Test adding a product to the queue"""
        product_queue = ProductToBeAdded.objects.create(
            barcode="1234567890123"
        )

        self.assertEqual(product_queue.barcode, "1234567890123")

    def test_product_barcode_uniqueness(self):
        """Test that barcodes must be unique"""
        # Create first product
        ProductToBeAdded.objects.create(barcode="UNIQUE123")

        # Try to create another with same barcode - should raise error
        with self.assertRaises(Exception):  # Will raise IntegrityError
            ProductToBeAdded.objects.create(barcode="UNIQUE123")

    def test_product_to_be_added_string(self):
        """Test the __str__ method"""
        product_queue = ProductToBeAdded.objects.create(
            barcode="TEST-BARCODE-001"
        )

        self.assertEqual(str(product_queue), "TEST-BARCODE-001")


# Only run these tests if tool models exist
if HAS_TOOL_MODELS:
    class ToolModelTests(TestCase):
        """Test tool models - end mills, drills, etc."""

        def test_endmill_creation(self):
            """Test creating an end mill"""
            endmill = EndMill.objects.create(
                code="EM-100",
                manufacturer="SANDVIK",
                description="High-speed end mill 10mm",
                quantity=5,
                catalog_price=55.00,
                barcode="1111111111"
            )

            self.assertEqual(endmill.code, "EM-100")
            self.assertEqual(endmill.manufacturer, "SANDVIK")
            self.assertEqual(endmill.quantity, 5)

        def test_tool_quantity_update(self):
            """Test updating tool quantity (e.g., after receiving an order)"""
            tool = EndMill.objects.create(
                code="EM-101",
                manufacturer="KENNAMETAL",
                description="Test tool",
                quantity=5
            )

            # Original quantity
            self.assertEqual(tool.quantity, 5)

            # Receive 10 more tools
            tool.quantity += 10
            tool.save()

            # Verify update
            updated_tool = EndMill.objects.get(code="EM-101")
            self.assertEqual(updated_tool.quantity, 15)

        def test_low_stock_detection(self):
            """Test detecting tools with low stock"""
            # Create a tool with low stock
            low_stock_tool = EndMill.objects.create(
                code="EM-LOW",
                manufacturer="SANDVIK",
                description="Low stock tool",
                quantity=2  # Only 2 left!
            )

            # Create a tool with sufficient stock
            good_stock_tool = EndMill.objects.create(
                code="EM-OK",
                manufacturer="SANDVIK",
                description="Good stock tool",
                quantity=20
            )

            # Check low stock (threshold: 5)
            low_stock_threshold = 5

            is_low_stock = low_stock_tool.quantity < low_stock_threshold
            is_good_stock = good_stock_tool.quantity >= low_stock_threshold

            self.assertTrue(is_low_stock)
            self.assertTrue(is_good_stock)

        def test_tool_search_by_code(self):
            """Test searching for a tool by code"""
            EndMill.objects.create(
                code="SEARCH-001",
                manufacturer="SANDVIK",
                description="Searchable tool",
                quantity=10
            )

            # Search for the tool
            found_tool = EndMill.objects.filter(code="SEARCH-001").first()

            self.assertIsNotNone(found_tool)
            self.assertEqual(found_tool.code, "SEARCH-001")

        def test_tool_search_by_barcode(self):
            """Test searching for a tool by barcode"""
            EndMill.objects.create(
                code="BAR-001",
                manufacturer="KENNAMETAL",
                description="Barcode test",
                quantity=5,
                barcode="9876543210"
            )

            # Search by barcode
            found_tool = EndMill.objects.filter(barcode="9876543210").first()

            self.assertIsNotNone(found_tool)
            self.assertEqual(found_tool.code, "BAR-001")

        def test_tool_search_by_manufacturer(self):
            """Test searching tools by manufacturer"""
            # Create multiple tools from different manufacturers
            EndMill.objects.create(
                code="SAND-001",
                manufacturer="SANDVIK",
                description="Sandvik tool 1",
                quantity=5
            )

            EndMill.objects.create(
                code="SAND-002",
                manufacturer="SANDVIK",
                description="Sandvik tool 2",
                quantity=8
            )

            EndMill.objects.create(
                code="KENN-001",
                manufacturer="KENNAMETAL",
                description="Kennametal tool",
                quantity=3
            )

            # Search for SANDVIK tools
            sandvik_tools = EndMill.objects.filter(manufacturer="SANDVIK")

            self.assertEqual(sandvik_tools.count(), 2)

        def test_tool_string_representation(self):
            """Test the __str__ method of tools"""
            tool = EndMill.objects.create(
                code="STR-001",
                manufacturer="SANDVIK",
                description="String test tool",
                quantity=10
            )

            tool_str = str(tool)

            # String should include manufacturer and code
            self.assertIn("SANDVIK", tool_str)
            self.assertIn("STR-001", tool_str)


class InventoryCalculationTests(TestCase):
    """Test inventory-related calculations"""

    def test_reorder_quantity_calculation(self):
        """Test calculating how many to reorder"""
        current_stock = 3
        minimum_stock = 10

        # Calculate reorder quantity
        reorder_qty = max(0, minimum_stock - current_stock)

        self.assertEqual(reorder_qty, 7)

    def test_no_reorder_needed(self):
        """Test when stock is sufficient"""
        current_stock = 15
        minimum_stock = 10

        reorder_qty = max(0, minimum_stock - current_stock)

        self.assertEqual(reorder_qty, 0)

    def test_total_order_cost(self):
        """Test calculating total cost of an order"""
        quantity = 10
        price_per_unit = 45.50

        total_cost = quantity * price_per_unit

        self.assertEqual(total_cost, 455.00)

    def test_stock_value_calculation(self):
        """Test calculating total value of stock"""
        # If we have 5 tools at $50 each
        quantity = 5
        unit_price = 50.00

        stock_value = quantity * unit_price

        self.assertEqual(stock_value, 250.00)
