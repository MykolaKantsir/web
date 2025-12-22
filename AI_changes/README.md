# Gaston V1 AI Changes Documentation

This directory contains all AI-assisted development documentation for the Gaston V1 manufacturing monitoring system. Documentation is organized by category for easy navigation.

## Directory Structure

```
AI_changes/
├── README.md                    # This file - navigation index
├── implemented/                 # Completed features and implementations
├── planning/                    # Planned features and design docs
├── archived/                    # Outdated or superseded documentation
└── guides/                      # How-to guides and references
```

## Implemented Features

Documentation for completed and deployed features:

### [2025-12-22.md](implemented/2025-12-22.md)
**Recent Implementation - Manual Operation Status Toggle & Drawing Monitor Display**
- Manual machine-operation assignment controls
- Real-time drawing monitor display system with WebSocket support
- In-memory cursor cache with 3-minute timeout
- Hybrid polling + WebSocket architecture
- Full documentation of all changes from 2025-12-22

### [2025-12-22_part2.md](implemented/2025-12-22_part2.md)
**Part 2 - Logo Fix, Package Installation & Azure Deployment Guide**
- Fixed drawing monitor logo (colors, size, tagline)
- Corrected package installation to venv (channels, daphne)
- Updated VSCode launch configuration for Daphne
- Split HTML/CSS/JS files for better organization
- Complete Azure deployment guide with WebSocket configuration

### [2025-12-22_part3_asgi_fix.md](implemented/2025-12-22_part3_asgi_fix.md)
**Part 3 - Django ASGI Import Order Fix**
- Fixed Django settings initialization order in asgi.py
- Added django.setup() call to initialize app registry
- Resolved "Apps aren't loaded yet" import error
- Daphne server now starts successfully
- Standard Django Channels configuration pattern

### [dashboard_view.md](implemented/dashboard_view.md)
**Dashboard Airport View Implementation**
- Airport-style table view for machine dashboard
- Two-column layout: Machine | Status
- Auto-scroll functionality with 3-second pause
- Real-time status updates via AJAX polling
- Keyboard navigation (Arrow Left/Right)
- Color-coded status rows with gradients and glow effects

### [next_jobs_view.md](implemented/next_jobs_view.md)
**Next Jobs Airport View Implementation**
- Airport-style table view for next jobs queue
- Five-column layout: Machine | Job | Material | Quantity | Location
- Auto-scroll functionality
- "No operation" warning with red pulsing border
- View switching between card and table modes

### [API_AUTHENTICATION.md](implemented/API_AUTHENTICATION.md)
**Dual Authentication System**
- Token authentication for Android apps (no CSRF required)
- Session authentication for web browsers (CSRF required)
- Login/logout/validate endpoints
- Android integration examples
- Backwards compatible with existing Python scripts

## Guides & References

How-to guides and reference documentation:

### [TESTING_GUIDE.md](guides/TESTING_GUIDE.md)
**Beginner's Guide to Testing**
- Explains what tests are and why they matter
- Types of tests (Model, View, Utility)
- Detailed examples for monitoring, measuring, and inventory apps
- Best practices for writing tests
- Common assertions reference

### [RUNNING_TESTS.md](guides/RUNNING_TESTS.md)
**How to Run Tests**
- Quick start commands
- Understanding test output (dots, F, E)
- Common testing commands
- Tips for beginners

### [TESTING_SUMMARY.md](guides/TESTING_SUMMARY.md)
**Testing Introduction Summary**
- Overview of created test files
- Total test coverage (50+ test methods)
- Key test examples
- Why tests are important for manufacturing system

## Root Level Documentation

These files remain at the web root for easy access:

### [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md)
**Gaston V1 Design System**
- Complete color palette with hex codes and usage
- Typography specifications
- Design patterns (shadows, borders, animations)
- Component guidelines (buttons, cards, badges, forms)
- Responsive breakpoints
- Usage examples

## Archived Documentation

Outdated or superseded documentation (kept for historical reference):

### [to_do_old.md](archived/to_do_old.md)
**Original To-Do List (2024.08.04)**
- Old task list for job details page
- Cycle management features
- Monitoring improvements
- Status: Most items completed or superseded

### [TODO_old.md](archived/TODO_old.md)
**Old TODO Notes**
- Measuring app improvements
- Protocol dimension measurement tracking
- Status: Outdated

## Planning Documentation

Design documents and planned features (not yet implemented):

*Currently empty - add planning documents here as features are designed*

## Quick Reference

### Recently Completed (2025-12-22)
1. Manual machine-operation assignment toggle
2. Real-time drawing monitor display system
3. WebSocket integration with Django Channels
4. In-memory cursor cache with thread-safe state management

### Major Completed Features
1. Airport-style dashboard view with auto-scroll
2. Airport-style next jobs view with auto-scroll
3. Token authentication system for Android apps
4. Comprehensive test suite (50+ tests)
5. Complete design system documentation

### Testing
- **Run all tests:** `python manage.py test`
- **Run specific app:** `python manage.py test monitoring`
- **Verbose output:** `python manage.py test --verbosity=2`

### API Authentication
- **Login:** `POST /api/auth/login/` (returns token)
- **Validate:** `GET /api/auth/validate/` (checks token validity)
- **Logout:** `POST /api/auth/logout/` (deletes token)

## For AI Sessions

When starting a new AI conversation about Gaston V1:

1. **Start here:** Read this README.md for overview
2. **Check implemented/:** Review what's already built
3. **Check guides/:** Understand testing and design system
4. **Check DESIGN_SYSTEM.md:** Use consistent colors and patterns
5. **Check archived/:** Understand what's been superseded
6. **Document new work:** Add new documentation to appropriate folder

## File Naming Conventions

- **Implemented features:** `feature_name.md` or `YYYY-MM-DD.md` for daily summaries
- **Guides:** `UPPERCASE_GUIDE.md` for reference documentation
- **Planning:** `PLANNING_feature_name.md` for design docs
- **Archived:** `original_name_old.md` or `DEPRECATED_name.md`

## Contributing Guidelines

When adding new documentation:

1. Place in correct folder based on status
2. Use clear, descriptive filenames
3. Update this README.md with links and descriptions
4. Include implementation date in completed features
5. Mark deprecated docs with "Status: Outdated" or move to archived/

## Key Technologies

- **Backend:** Django 4.2+
- **WebSocket:** Django Channels, Daphne ASGI server
- **Frontend:** Vanilla JavaScript, airport-style CSS
- **Authentication:** Django REST Framework Token + Session
- **Testing:** Django TestCase framework
- **Real-time:** WebSocket + AJAX polling hybrid

## Contact & Version

- **Project:** Gaston V1 Manufacturing Monitoring System
- **Documentation Started:** 2024
- **Last Major Update:** 2025-12-22
- **Organization Structure:** 2025-12-22

---

**Note:** This documentation structure was created to organize multiple markdown files for better git repository management and easier navigation for both humans and AI assistants.
