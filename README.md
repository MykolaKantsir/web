# Gaston V1 - Manufacturing Monitoring System

Enterprise-grade manufacturing monitoring and management system built with Django.

## Overview

Gaston V1 is a comprehensive manufacturing management platform featuring:

- **Real-time machine monitoring** with WebSocket support
- **Quality measurement system** with tolerance checking
- **Tool inventory management** with barcode tracking
- **Job planning and scheduling** with airport-style displays
- **Manufacturing drawing display** for shop floor monitors
- **Dual authentication** (Token for Android apps, Session for web)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test
```

## Documentation

Comprehensive documentation is available in the [AI_changes](AI_changes/) directory:

- **[AI_changes/README.md](AI_changes/README.md)** - Complete documentation index
- **[AI_changes/implemented/](AI_changes/implemented/)** - Completed features
- **[AI_changes/guides/](AI_changes/guides/)** - How-to guides and testing docs
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Color palette, typography, design patterns

## Key Features

### Machine Monitoring
- Real-time dashboard with airport-style table view
- Status tracking (Active, Stopped, Feed-Hold, Alarm, etc.)
- Auto-scroll display for kiosk/TV deployment
- Manual operation assignment controls

### Drawing Monitor Display
- Full-screen manufacturing drawing display
- WebSocket real-time updates (<500ms latency)
- Automatic cursor tracking with 3-minute timeout
- Embedded company logo when idle

### Quality Measurement
- PDF drawing import with multi-page support
- Dimension tolerance checking (bilateral, shaft, hole)
- Measurement protocol generation
- Tolerance validation in real-time

### Tool Inventory
- Barcode-based inventory tracking
- Low stock detection and alerts
- Order management workflow
- Product search and filtering

### Next Jobs Queue
- Airport-style job display
- Material and quantity tracking
- Location management
- "No operation" warnings

## Technology Stack

- **Backend:** Django 4.2+, Django REST Framework
- **Real-time:** Django Channels, Daphne ASGI server, WebSocket
- **Database:** SQLite (development), PostgreSQL (production ready)
- **Frontend:** Vanilla JavaScript, Bootstrap, Airport-style CSS
- **Authentication:** Token + Session dual authentication
- **Testing:** Django TestCase (50+ tests)

## Project Structure

```
web/
├── monitoring/          # Machine monitoring app
├── measuring/           # Quality measurement app
├── inventory/           # Tool inventory app
├── AI_changes/          # Documentation and implementation notes
├── DESIGN_SYSTEM.md     # Design system reference
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test monitoring
python manage.py test measuring
python manage.py test inventory

# Run with verbose output
python manage.py test --verbosity=2
```

See [AI_changes/guides/TESTING_GUIDE.md](AI_changes/guides/TESTING_GUIDE.md) for detailed testing documentation.

## API Documentation

The system provides REST APIs with dual authentication:

- **Token Authentication** (for Android/mobile apps)
- **Session Authentication** (for web browsers)

See [AI_changes/implemented/API_AUTHENTICATION.md](AI_changes/implemented/API_AUTHENTICATION.md) for API endpoints and usage.

## Design System

Consistent design across all views using:

- **Primary:** Deep Koamaru (#1a337e)
- **Accent:** Cadet Blue (#5F9EA0)
- **Status Colors:** Semantic green, orange, red, blue
- **Typography:** System fonts, monospace for airport boards
- **Components:** Cards, badges, buttons, forms

See [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) for complete design specifications.

## Recent Updates (2025-12-22)

- ✅ Manual machine-operation assignment controls
- ✅ Real-time drawing monitor display with WebSocket
- ✅ In-memory cursor cache with thread-safe state management
- ✅ Organized documentation structure

## Development

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Running with ASGI (WebSocket Support)

```bash
# Install Daphne (already in requirements.txt)
pip install daphne

# Run with Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 web.asgi:application
```

## Contributing

When adding new features:

1. Follow the [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) guidelines
2. Write tests for new functionality
3. Document changes in [AI_changes/](AI_changes/)
4. Update this README if adding major features

## License

Proprietary - Gaston Components

## Support

For questions or issues, refer to the comprehensive documentation in [AI_changes/README.md](AI_changes/README.md).
