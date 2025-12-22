# How to Run Tests

## Quick Start

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test monitoring
python manage.py test measuring
python manage.py test inventory

# Run a specific test class
python manage.py test monitoring.tests.JobModelTests
python manage.py test measuring.tests.ToleranceCheckTests

# Run a specific test method
python manage.py test monitoring.tests.JobModelTests.test_job_creation

# Run with more detail
python manage.py test --verbosity=2
```

## What Tests Were Created

### **Monitoring App** (`monitoring/tests.py`)
- **JobModelTests**: Test job creation, completion tracking, remaining parts
- **MachineModelTests**: Test machine creation and virtual machines
- **MonitorOperationTests**: Test operation tracking and flags
- **MonitoringViewTests**: Test dashboard access and authentication
- **JobCalculationTests**: Test job completion percentage calculations

### **Measuring App** (`measuring/tests.py`)
- **DrawingModelTests**: Test drawing creation and multi-page drawings
- **DimensionModelTests**: Test dimension creation and tolerances
- **ToleranceCheckTests**: **Critical tests for quality control**
  - Bilateral tolerance (±0.1)
  - Shaft tolerance (negative only)
  - Hole tolerance (positive only)
  - Edge cases (exact min/max values)
- **MeasuredValueTests**: Test recording measurements
- **ProtocolTests**: Test measurement protocols and reports

### **Inventory App** (`inventory/tests.py`)
- **OrderModelTests**: Test order creation and status workflow
- **ProductToBeAddedTests**: Test product queue and barcode uniqueness
- **ToolModelTests**: Test tool creation, search, and quantity updates
- **InventoryCalculationTests**: Test reorder calculations and stock value

## Understanding Test Output

### Successful Test Run
```
....................
----------------------------------------------------------------------
Ran 20 tests in 0.150s

OK
```
Each dot (.) represents a passing test.

### Failed Test
```
F...................
======================================================================
FAIL: test_job_creation (monitoring.tests.JobModelTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "monitoring/tests.py", line 32, line in test_job_creation
    self.assertEqual(job.project, "TEST-002")
AssertionError: 'TEST-001' != 'TEST-002'

----------------------------------------------------------------------
Ran 20 tests in 0.150s

FAILED (failures=1)
```
F = Failed test, shows which assertion failed and why.

### Error in Test
```
E...................
======================================================================
ERROR: test_job_creation (monitoring.tests.JobModelTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AttributeError: 'NoneType' object has no attribute 'project'

----------------------------------------------------------------------
Ran 20 tests in 0.150s

FAILED (errors=1)
```
E = Error occurred (usually a bug in the test or missing data)

## Tips for Beginners

1. **Start with one app**: `python manage.py test measuring`
2. **Read the output carefully**: It shows which test failed and why
3. **Tests use a separate test database**: Your real data is safe
4. **Run tests often**: After every code change
5. **Add tests when fixing bugs**: Write a test that reproduces the bug first

## Common Commands

```bash
# Keep the test database between runs (faster)
python manage.py test --keepdb

# Stop on first failure
python manage.py test --failfast

# Run tests in parallel (faster for large test suites)
python manage.py test --parallel

# Show which tests are running
python manage.py test --verbosity=2

# Debug mode (shows print statements)
python manage.py test --debug-mode
```

## Next Steps

1. Run the tests to see if your models work correctly
2. Add more tests as you add features
3. Use tests to catch bugs before deployment
4. Consider setting up continuous integration (CI) to run tests automatically
