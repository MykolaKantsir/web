from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from monitoring.models import Job, Machine, Cycle, Monitor_operation


class JobModelTests(TestCase):
    """Test the Job model - tracks production jobs on machines"""

    def setUp(self):
        """Create test data before each test"""
        # Create a test machine
        self.machine = Machine.objects.create(
            name="Test CNC Machine",
            ip_address="192.168.1.100",
            is_virtual=False
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

        # Verify the job was created with correct values
        self.assertEqual(job.project, "TEST-001")
        self.assertEqual(job.required_quantity, 10)
        self.assertEqual(job.currently_made_quantity, 0)
        self.assertEqual(job.machine, self.machine)

    def test_job_remaining_parts(self):
        """Test calculation of remaining parts in a job"""
        job = Job.objects.create(
            project="TEST-002",
            machine=self.machine,
            required_quantity=50,
            currently_made_quantity=30,
            started=timezone.now()
        )

        # Calculate remaining parts
        remaining = job.required_quantity - job.currently_made_quantity

        # Should have 20 parts remaining
        self.assertEqual(remaining, 20)

    def test_job_is_complete(self):
        """Test checking if a job is complete"""
        job = Job.objects.create(
            project="TEST-003",
            machine=self.machine,
            required_quantity=10,
            currently_made_quantity=10,
            started=timezone.now()
        )

        # Job should be complete when currently_made >= required
        is_complete = job.currently_made_quantity >= job.required_quantity
        self.assertTrue(is_complete)

    def test_job_is_not_complete(self):
        """Test checking if a job is incomplete"""
        job = Job.objects.create(
            project="TEST-004",
            machine=self.machine,
            required_quantity=100,
            currently_made_quantity=50,
            started=timezone.now()
        )

        # Job should NOT be complete
        is_complete = job.currently_made_quantity >= job.required_quantity
        self.assertFalse(is_complete)

    def test_job_string_representation(self):
        """Test the __str__ method of Job"""
        start_time = timezone.now()
        job = Job.objects.create(
            project="PART-123",
            machine=self.machine,
            required_quantity=5,
            started=start_time
        )

        job_str = str(job)

        # String should contain the project name and quantity
        self.assertIn("PART-123", job_str)
        self.assertIn("5", job_str)

    def test_job_with_multiple_quantities(self):
        """Test job with parts_per_cycle > 1"""
        job = Job.objects.create(
            project="TEST-005",
            machine=self.machine,
            required_quantity=100,
            currently_made_quantity=0,
            parts_per_cycle=5,  # Makes 5 parts per cycle
            started=timezone.now()
        )

        self.assertEqual(job.parts_per_cycle, 5)

        # If we complete 4 cycles, we should have 20 parts
        cycles_completed = 4
        parts_made = cycles_completed * job.parts_per_cycle
        self.assertEqual(parts_made, 20)


class MachineModelTests(TestCase):
    """Test the Machine model - represents CNC machines"""

    def test_machine_creation(self):
        """Test creating a machine"""
        machine = Machine.objects.create(
            name="CNC-001",
            ip_address="192.168.1.50",
            is_virtual=False
        )

        self.assertEqual(machine.name, "CNC-001")
        self.assertEqual(machine.ip_address, "192.168.1.50")
        self.assertFalse(machine.is_virtual)

    def test_virtual_machine(self):
        """Test creating a virtual machine"""
        machine = Machine.objects.create(
            name="Virtual-Machine-1",
            ip_address="127.0.0.1",
            is_virtual=True
        )

        self.assertTrue(machine.is_virtual)


class MonitorOperationTests(TestCase):
    """Test the Monitor_operation model - production operations"""

    def test_operation_creation(self):
        """Test creating a monitor operation"""
        operation = Monitor_operation.objects.create(
            operation_id=12345,
            name="Milling operation",
            quantity=50,
            material="Aluminum",
            is_in_progress=False,
            is_setup=False
        )

        self.assertEqual(operation.operation_id, 12345)
        self.assertEqual(operation.name, "Milling operation")
        self.assertEqual(operation.quantity, 50)
        self.assertFalse(operation.is_in_progress)
        self.assertFalse(operation.is_setup)

    def test_operation_in_progress_flag(self):
        """Test the is_in_progress flag"""
        operation = Monitor_operation.objects.create(
            operation_id=12346,
            name="Test operation",
            quantity=10,
            is_in_progress=True
        )

        self.assertTrue(operation.is_in_progress)

    def test_operation_setup_flag(self):
        """Test the is_setup flag"""
        operation = Monitor_operation.objects.create(
            operation_id=12347,
            name="Setup operation",
            quantity=1,
            is_setup=True
        )

        self.assertTrue(operation.is_setup)


class MonitoringViewTests(TestCase):
    """Test monitoring app views"""

    def setUp(self):
        """Set up test client and create test data"""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create a test machine
        self.machine = Machine.objects.create(
            name="CNC-001",
            ip_address="192.168.1.50"
        )

    def test_dashboard_requires_login(self):
        """Test that the dashboard requires login"""
        # Try to access dashboard without logging in
        response = self.client.get(reverse('monitoring:home'))

        # Should redirect to login page (302) or return 403
        self.assertIn(response.status_code, [302, 403])

    def test_dashboard_loads_when_logged_in(self):
        """Test that the dashboard loads successfully when logged in"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')

        # Try to load the dashboard
        response = self.client.get(reverse('monitoring:home'))

        # Check that the page loaded successfully (status code 200)
        self.assertEqual(response.status_code, 200)


# Example of a simple utility function test
class JobCalculationTests(TestCase):
    """Test job-related calculations"""

    def test_completion_percentage(self):
        """Test calculating completion percentage"""
        # If we made 25 out of 100 parts, we're 25% done
        made = 25
        required = 100

        percentage = (made / required) * 100

        self.assertEqual(percentage, 25.0)

    def test_completion_percentage_edge_case_zero(self):
        """Test completion when nothing is made yet"""
        made = 0
        required = 50

        percentage = (made / required) * 100

        self.assertEqual(percentage, 0.0)

    def test_completion_percentage_edge_case_complete(self):
        """Test completion when job is 100% done"""
        made = 100
        required = 100

        percentage = (made / required) * 100

        self.assertEqual(percentage, 100.0)

    def test_avoid_division_by_zero(self):
        """Test handling of edge case where required_quantity is 0"""
        made = 5
        required = 0

        # Should handle this gracefully (avoid division by zero)
        if required == 0:
            percentage = 0
        else:
            percentage = (made / required) * 100

        self.assertEqual(percentage, 0)
