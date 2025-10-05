# InvivoDB Technical Documentation

## Current Application Status

The invivoDB application is a functional Flask web application running in development mode with the following implemented features:

### Implemented Features

**Web Interface:**
- Landing page with search functionality
- Dashboard with database statistics and recent activity
- Animal browsing with pagination and species filtering
- Experiment listing with detailed views
- Therapy catalog organized by categories
- Assay type management
- Admin interface for species management

**Database Schema:**
- SQLAlchemy models for all core entities
- Many-to-many relationships between experiments and therapies
- Automated accession number generation with validation
- Comprehensive data validation via Pydantic schemas

**Data Models:**
- Species (8 core species with taxonomy info)
- Animals (with unique accession numbers)
- Experiments (with full methodology tracking)
- Therapies (categorized by mechanism of action)
- Assays (with measurements and quality control)
- Results (statistical outcomes and conclusions)

## Running the Application

**Development Mode:**
```bash
cd src/web
python app.py
```

**Access URLs:**
- Main application: http://127.0.0.1:5000
- Dashboard: http://127.0.0.1:5000/dashboard
- Admin interface: http://127.0.0.1:5000/admin/species

## Database Configuration

**Current Setup:**
- SQLite database (`invivodb.db`) in development
- Database initialization with sample data on first run
- Flask-SQLAlchemy ORM with automatic table creation

**Production Ready:**
- PostgreSQL support via DATABASE_URL environment variable
- Gunicorn WSGI server configuration
- Environment-based configuration management

## Key Components

### Application Structure
```
src/web/app.py          # Main Flask application (400+ lines)
src/models/database.py  # SQLAlchemy models (237+ lines)  
src/models/schemas.py   # Pydantic validation (407+ lines)
```

### Route Handlers
- `/` - Landing page
- `/dashboard` - Statistics overview
- `/animals` - Animal listing and details
- `/experiments` - Experiment management
- `/therapies` - Treatment catalog
- `/assay_types` - Test methodology management
- `/add_animal` - Animal registration form

### Data Validation
- Pydantic schemas for all models
- Automated validation for accession numbers
- Enum-based constraints for data consistency
- API-ready request/response validation

## Dependencies

**Core Framework:**
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.23

**Data Validation:**
- Pydantic 1.10.13

**Production:**
- Gunicorn 21.2.0
- Werkzeug 3.0.1

## Known Issues

1. **DateTime Warning**: Using deprecated `datetime.utcnow()` in line 76 of app.py
2. **Missing Images**: Several species images (mouse.jpg, dog.jpg, etc.) return 404 errors
3. **Development Mode**: Currently configured for development with DEBUG=True

## Next Steps

**Priority Fixes:**
1. Update deprecated datetime usage to `datetime.now(datetime.UTC)`
2. Add missing species images to static/images/
3. Implement proper error handling for missing data

**Feature Enhancements:**
1. REST API endpoints with Flask-RESTX
2. Advanced search and filtering capabilities
3. Data export functionality
4. User authentication and authorization
5. Integration with external databases (ChEMBL, PubChem)

## Performance Notes

- Application loads successfully with sample data
- Database queries are optimized with proper relationships
- Pagination implemented for large datasets (20 items per page)
- Caching strategy needed for production deployment

## Deployment Readiness

**Current Status:** Development ready, production configuration available

**Production Checklist:**
- [x] Environment variable configuration
- [x] Database URL configuration
- [x] Production WSGI server (Gunicorn)
- [ ] SSL/HTTPS configuration
- [ ] Static file serving optimization
- [ ] Logging configuration
- [ ] Error monitoring integration

---

*Last updated: October 2025*
*Application version: Development prototype*