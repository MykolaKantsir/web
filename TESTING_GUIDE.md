# Testing Guide for Beginners

## What is a Test?

A **test** is a small program that automatically checks if your code works correctly. Instead of manually clicking through your app every time you make a change, tests do the checking for you.

### Why Write Tests?

1. **Catch bugs early**: Find problems before your users do
2. **Safe changes**: Modify code confidently - tests alert you if something breaks
3. **Documentation**: Tests show how your code should work
4. **Save time**: Automated testing is faster than manual testing

---

## Types of Tests in This Project

### 1. **Model Tests** - Test Database Models
- Check if data saves correctly
- Verify calculated fields work
- Test model methods and relationships

### 2. **View Tests** - Test Web Pages and APIs
- Verify pages load correctly
- Check if forms work
- Test API endpoints return correct data

### 3. **Utility Tests** - Test Helper Functions
- Verify calculations
- Test data transformations
- Check edge cases

---

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test monitoring
python manage.py test measuring
python manage.py test inventory

# Run a specific test file
python manage.py test monitoring.tests.test_models

# Run tests with more details
python manage.py test --verbosity=2
```

---

## Test Examples for Your Apps

### **MONITORING APP** - Machine Monitoring Tests

#### Key Things to Test:
1. **Job Creation & Tracking**
   - Does a job save correctly?
   - Is the job completion percentage calculated correctly?
   - Does the estimated end time calculation work?

2. **Machine States**
   - Does machine status update correctly?
   - Are machine subscriptions working?

3. **Cycle Analysis**
   - Are full cycles detected correctly?
   - Do cycle calculations work?

#### Example Tests:

```python
# File: monitoring/tests/test_models.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from monitoring.models import Job, Machine, Cycle

class JobModelTests(TestCase):
    """Test the Job model"""

    def setUp(self):
        """Create test data before each test"""
        self.machine = Machine.objects.create(
            name="Test CNC Machine",
            ip_address="192.168.1.100"
        )

    def test_job_creation(self):
        """Test that a job can be created successfully"""
        job = Job.objects.create(
            project="TEST-001",
            machine=self.machine,
            required_quantity=10,
            currently_made_quantity=0,
            started=timezone.now()
        )

        self.assertEqual(job.project, "TEST-001")
        self.assertEqual(job.required_quantity, 10)
        self.assertEqual(job.currently_made_quantity, 0)

    def test_job_completion_percentage(self):
        """Test that job completion is calculated correctly"""
        job = Job.objects.create(
            project="TEST-002",
            machine=self.machine,
            required_quantity=100,
            currently_made_quantity=25,
            started=timezone.now()
        )

        # Job should be 25% complete
        expected_percentage = (25 / 100) * 100
        # Add a method to your Job model to calculate this
        # actual_percentage = job.get_completion_percentage()
        # self.assertEqual(actual_percentage, expected_percentage)

    def test_job_remaining_parts(self):
        """Test calculation of remaining parts"""
        job = Job.objects.create(
            project="TEST-003",
            machine=self.machine,
            required_quantity=50,
            currently_made_quantity=30,
            started=timezone.now()
        )

        # Should have 20 parts remaining
        remaining = job.required_quantity - job.currently_made_quantity
        self.assertEqual(remaining, 20)

    def test_job_str_representation(self):
        """Test the string representation of a job"""
        job = Job.objects.create(
            project="PART-123",
            machine=self.machine,
            required_quantity=5,
            started=timezone.now()
        )

        # Check that the string contains the project name
        self.assertIn("PART-123", str(job))
        self.assertIn("5", str(job))
```

```python
# File: monitoring/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from monitoring.models import Machine, Job
from django.contrib.auth.models import User

class MonitoringViewTests(TestCase):
    """Test monitoring app views"""

    def setUp(self):
        """Set up test client and create test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.machine = Machine.objects.create(
            name="CNC-001",
            ip_address="192.168.1.50"
        )

    def test_dashboard_loads(self):
        """Test that the dashboard page loads successfully"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')

        # Try to load the dashboard
        response = self.client.get(reverse('monitoring:home'))

        # Check that the page loaded successfully (status code 200)
        self.assertEqual(response.status_code, 200)

    def test_machine_detail_view(self):
        """Test that individual machine detail page works"""
        self.client.login(username='testuser', password='testpass123')

        # Get the machine detail page
        url = reverse('monitoring:machine_detail', args=[self.machine.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check that the machine name appears on the page
        self.assertContains(response, "CNC-001")
```

---

### **MEASURING APP** - Quality Measurement Tests

#### Key Things to Test:
1. **Drawing Management**
   - Can drawings be created with images?
   - Are drawings searchable?

2. **Dimensions & Tolerances**
   - Do tolerance checks work correctly?
   - Are measurements within tolerance?

3. **Measurement Protocols**
   - Can protocols be created and finished?
   - Do measured values link correctly?

#### Example Tests:

```python
# File: measuring/tests/test_models.py

from django.test import TestCase
from measuring.models import Drawing, Dimension, MeasuredValue, Protocol

class MeasuringModelTests(TestCase):
    """Test measuring app models"""

    def setUp(self):
        """Create test drawing"""
        self.drawing = Drawing.objects.create(
            filename="TEST-DRAWING-001.pdf",
            pages_count=1
        )

    def test_drawing_creation(self):
        """Test that a drawing can be created"""
        self.assertEqual(self.drawing.filename, "TEST-DRAWING-001.pdf")
        self.assertEqual(self.drawing.pages_count, 1)

    def test_dimension_tolerance_check(self):
        """Test checking if a measured value is within tolerance"""
        # Create a dimension with tolerance range 10.0 to 10.5
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=100, y=100, width=50, height=50,
            value="10±0.25",
            min_value=10.0,
            max_value=10.5
        )

        # Test a measurement within tolerance
        measured_value_ok = MeasuredValue.objects.create(
            dimension=dimension,
            value=10.2
        )

        # Check if value is within range
        is_within_tolerance = (
            dimension.min_value <= measured_value_ok.value <= dimension.max_value
        )
        self.assertTrue(is_within_tolerance)

        # Test a measurement outside tolerance
        measured_value_bad = MeasuredValue.objects.create(
            dimension=dimension,
            value=10.6  # Too high!
        )

        is_within_tolerance = (
            dimension.min_value <= measured_value_bad.value <= dimension.max_value
        )
        self.assertFalse(is_within_tolerance)

    def test_protocol_creation(self):
        """Test creating a measurement protocol"""
        protocol = Protocol.objects.create(
            drawing=self.drawing,
            is_finished=False
        )

        self.assertFalse(protocol.is_finished)

        # Finish the protocol
        protocol.is_finished = True
        protocol.save()

        self.assertTrue(protocol.is_finished)

    def test_dimension_str_representation(self):
        """Test the string representation of a dimension"""
        dimension = Dimension.objects.create(
            drawing=self.drawing,
            x=50, y=50, width=30, height=30,
            value="25.0"
        )

        # Should include the value and drawing filename
        self.assertIn("25.0", str(dimension))
        self.assertIn("TEST-DRAWING-001.pdf", str(dimension))
```

```python
# File: measuring/tests/test_tolerance_logic.py

from django.test import TestCase
from measuring.models import Drawing, Dimension, MeasuredValue

class ToleranceTests(TestCase):
    """Test tolerance checking logic"""

    def setUp(self):
        self.drawing = Drawing.objects.create(
            filename="TOL-TEST.pdf",
            pages_count=1
        )

    def test_bilateral_tolerance(self):
        """Test ±0.1 tolerance (bilateral)"""
        # Dimension: 50±0.1 (min: 49.9, max: 50.1)
        dim = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="50±0.1",
            min_value=49.9,
            max_value=50.1,
            type_selection=2  # Bilateral
        )

        # Test exact value
        self.assertTrue(49.9 <= 50.0 <= 50.1)

        # Test minimum edge
        self.assertTrue(49.9 <= 49.9 <= 50.1)

        # Test maximum edge
        self.assertTrue(49.9 <= 50.1 <= 50.1)

        # Test out of tolerance (too low)
        self.assertFalse(49.9 <= 49.8 <= 50.1)

        # Test out of tolerance (too high)
        self.assertFalse(49.9 <= 50.2 <= 50.1)

    def test_shaft_tolerance(self):
        """Test shaft tolerance (negative only)"""
        # Dimension: 20 -0.2 (min: 19.8, max: 20.0)
        dim = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="20 -0.2",
            min_value=19.8,
            max_value=20.0,
            type_selection=1  # Shaft
        )

        # Test values
        self.assertTrue(19.8 <= 19.9 <= 20.0)  # OK
        self.assertFalse(19.8 <= 19.7 <= 20.0)  # Too small
        self.assertFalse(19.8 <= 20.1 <= 20.0)  # Too large

    def test_hole_tolerance(self):
        """Test hole tolerance (positive only)"""
        # Dimension: 30 +0.3 (min: 30.0, max: 30.3)
        dim = Dimension.objects.create(
            drawing=self.drawing,
            x=0, y=0, width=10, height=10,
            value="30 +0.3",
            min_value=30.0,
            max_value=30.3,
            type_selection=3  # Hole
        )

        # Test values
        self.assertTrue(30.0 <= 30.1 <= 30.3)  # OK
        self.assertFalse(30.0 <= 29.9 <= 30.3)  # Too small
        self.assertFalse(30.0 <= 30.4 <= 30.3)  # Too large
```

---

### **INVENTORY APP** - Tool Inventory Tests

#### Key Things to Test:
1. **Product Management**
   - Can products be created and searched?
   - Do product quantities update correctly?

2. **Order Management**
   - Can orders be created?
   - Do order status transitions work?
   - Are weekly orders calculated correctly?

3. **Barcode/Label Generation**
   - Are labels generated correctly?
   - Do barcodes match products?

#### Example Tests:

```python
# File: inventory/tests/test_models.py

from django.test import TestCase
from inventory.models import Order, WeekOrders
from inventory.models import EndMill  # Example tool type
from django.contrib.auth.models import User
from datetime import date

class InventoryModelTests(TestCase):
    """Test inventory app models"""

    def setUp(self):
        """Create test products and users"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        # Create a test end mill tool
        self.tool = EndMill.objects.create(
            code="EM-001",
            manufacturer="SANDVIK",
            description="6mm 4-flute end mill",
            quantity=5,
            catalog_price=45.50,
            barcode="1234567890"
        )

    def test_product_creation(self):
        """Test that a product can be created"""
        self.assertEqual(self.tool.code, "EM-001")
        self.assertEqual(self.tool.quantity, 5)
        self.assertEqual(float(self.tool.catalog_price), 45.50)

    def test_product_quantity_update(self):
        """Test updating product quantity"""
        # Original quantity is 5
        self.assertEqual(self.tool.quantity, 5)

        # Add 10 more tools
        self.tool.quantity += 10
        self.tool.save()

        # Verify the update
        updated_tool = EndMill.objects.get(code="EM-001")
        self.assertEqual(updated_tool.quantity, 15)

    def test_product_low_stock_detection(self):
        """Test detecting low stock items"""
        # Set quantity to 2 (low stock)
        self.tool.quantity = 2
        self.tool.save()

        # Check if stock is low (threshold: 5)
        low_stock_threshold = 5
        is_low_stock = self.tool.quantity < low_stock_threshold

        self.assertTrue(is_low_stock)

    def test_product_barcode_search(self):
        """Test finding a product by barcode"""
        # Search for product by barcode
        found_tool = EndMill.objects.filter(barcode="1234567890").first()

        self.assertIsNotNone(found_tool)
        self.assertEqual(found_tool.code, "EM-001")

    def test_product_str_representation(self):
        """Test the string representation"""
        # Should include manufacturer and code
        self.assertIn("SANDVIK", str(self.tool))
        self.assertIn("EM-001", str(self.tool))
```

```python
# File: inventory/tests/test_orders.py

from django.test import TestCase
from inventory.models import Order, EndMill
from inventory.choices import OrderStatus
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class OrderTests(TestCase):
    """Test order management"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='orderuser',
            password='pass123'
        )

        self.tool = EndMill.objects.create(
            code="EM-002",
            manufacturer="KENNAMETAL",
            description="8mm end mill",
            quantity=3,
            catalog_price=52.00
        )

    def test_order_creation(self):
        """Test creating an order"""
        content_type = ContentType.objects.get_for_model(EndMill)

        order = Order.objects.create(
            content_type=content_type,
            object_id=self.tool.id,
            quantity=10,
            ordered_by=self.user,
            status=OrderStatus.CREATED
        )

        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.status, OrderStatus.CREATED)
        self.assertEqual(order.ordered_by, self.user)

    def test_order_status_workflow(self):
        """Test order status transitions"""
        content_type = ContentType.objects.get_for_model(EndMill)

        order = Order.objects.create(
            content_type=content_type,
            object_id=self.tool.id,
            quantity=5,
            status=OrderStatus.CREATED
        )

        # Progress through statuses
        self.assertEqual(order.status, OrderStatus.CREATED)

        order.status = OrderStatus.PENDING
        order.save()
        self.assertEqual(order.status, OrderStatus.PENDING)

        order.status = OrderStatus.COMPLETED
        order.save()
        self.assertEqual(order.status, OrderStatus.COMPLETED)

    def test_multiple_orders_same_product(self):
        """Test creating multiple orders for the same product"""
        content_type = ContentType.objects.get_for_model(EndMill)

        order1 = Order.objects.create(
            content_type=content_type,
            object_id=self.tool.id,
            quantity=5
        )

        order2 = Order.objects.create(
            content_type=content_type,
            object_id=self.tool.id,
            quantity=10
        )

        # Check that both orders exist
        orders = Order.objects.filter(
            content_type=content_type,
            object_id=self.tool.id
        )

        self.assertEqual(orders.count(), 2)
        self.assertEqual(orders[0].quantity + orders[1].quantity, 15)
```

```python
# File: inventory/tests/test_search.py

from django.test import TestCase
from inventory.models import EndMill, DrillingTool

class ProductSearchTests(TestCase):
    """Test product search functionality"""

    def setUp(self):
        """Create test products"""
        EndMill.objects.create(
            code="EM-100",
            manufacturer="SANDVIK",
            description="High-speed end mill 10mm",
            quantity=5
        )

        EndMill.objects.create(
            code="EM-200",
            manufacturer="KENNAMETAL",
            description="Carbide end mill 12mm",
            quantity=8
        )

        DrillingTool.objects.create(
            code="DR-050",
            manufacturer="SANDVIK",
            description="Drill bit 5mm",
            quantity=12
        )

    def test_search_by_code(self):
        """Test searching products by code"""
        results = EndMill.objects.filter(code="EM-100")

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().description, "High-speed end mill 10mm")

    def test_search_by_manufacturer(self):
        """Test searching by manufacturer"""
        # Search across all product types
        sandvik_endmills = EndMill.objects.filter(manufacturer="SANDVIK")
        sandvik_drills = DrillingTool.objects.filter(manufacturer="SANDVIK")

        self.assertEqual(sandvik_endmills.count(), 1)
        self.assertEqual(sandvik_drills.count(), 1)

    def test_search_by_description(self):
        """Test searching in description"""
        # Search for products with "Carbide" in description
        results = EndMill.objects.filter(description__icontains="Carbide")

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().code, "EM-200")

    def test_low_stock_filter(self):
        """Test filtering products with low stock"""
        low_stock_threshold = 6

        low_stock_tools = EndMill.objects.filter(quantity__lt=low_stock_threshold)

        # Should find EM-100 (qty=5)
        self.assertEqual(low_stock_tools.count(), 1)
        self.assertEqual(low_stock_tools.first().code, "EM-100")
```

---

## Best Practices

### 1. **Test Names Should Be Descriptive**
✅ Good: `test_job_completion_percentage_calculation`
❌ Bad: `test1`

### 2. **Each Test Should Test One Thing**
Don't test multiple features in one test - keep them focused.

### 3. **Use setUp() to Create Test Data**
Avoid duplicating test data creation in every test.

### 4. **Test Edge Cases**
- Empty values
- Zero quantities
- Maximum values
- Invalid inputs

### 5. **Test Both Success and Failure**
```python
def test_valid_measurement(self):
    # Test a measurement within tolerance
    ...

def test_invalid_measurement(self):
    # Test a measurement outside tolerance
    ...
```

---

## Next Steps

1. **Start Small**: Pick one model and write 2-3 basic tests
2. **Run Tests Often**: Run tests after every change
3. **Add Tests When Fixing Bugs**: If you find a bug, write a test for it first
4. **Gradually Increase Coverage**: Add more tests over time

---

## Common Assertions

```python
# Equality
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# True/False
self.assertTrue(condition)
self.assertFalse(condition)

# None checks
self.assertIsNone(value)
self.assertIsNotNone(value)

# Contains
self.assertIn(item, list)
self.assertNotIn(item, list)

# Strings
self.assertContains(response, "Expected text")

# Numbers
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
```

---

## Questions?

Testing might seem complicated at first, but it becomes easier with practice. Start with simple model tests and gradually work your way up to more complex scenarios!
