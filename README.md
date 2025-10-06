# invivoDB: Curated Database for In Vivo Experimental Data

![](images/mousemovie1.gif.gif)
*Created with MeshyAI and edited with Canva.com*  

A Flask-based web application for managing and analyzing in vivo experimental data, designed to support drug discovery and digital twin modeling in life sciences research.

## Overview

InvivoDB provides a standardized platform for cataloging experimental animal data with structured schemas for species, therapies, experiments, and assays. The system features automated accession number generation, comprehensive data validation, and a user-friendly web interface.

## Key Features

- **Structured Data Management**: Comprehensive models for animals, experiments, therapies, and assays
- **Automated Accession Numbers**: Species-specific numbering system with validation
- **Therapy Classification**: Categorized by mechanism of action and therapeutic approach
- **Assay Integration**: Support for multiple assay types with measurements and quality control
- **Data Validation**: Pydantic schemas ensure data integrity and API documentation
- **Web Interface**: Flask-based dashboard with search, filtering, and detailed views

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite (included) or PostgreSQL for production

### Installation

```bash
# Clone repository
git clone <repository-url>
cd invivoDB

# Install dependencies
pip install -r requirements.txt

# Run the application
cd src/web
python app.py
```

Access the application at `http://localhost:5000`

## Application Structure

```
invivoDB/
├── src/
│   ├── models/
│   │   ├── database.py     # SQLAlchemy models
│   │   └── schemas.py      # Pydantic validation schemas
│   └── web/
│       ├── app.py          # Flask application
│       ├── templates/      # HTML templates
│       └── static/         # CSS, JS, images
├── requirements.txt        # Python dependencies
└── README.md
```

## Data Model

**Core Entities:**
- **Species**: Animal species with taxonomy information
- **Animals**: Individual experimental subjects with accession numbers
- **Experiments**: Research studies with methodology and timelines
- **Therapies**: Treatments categorized by mechanism of action
- **Assays**: Tests and measurements with quality control
- **Results**: Outcomes and statistical analysis

**Accession Number Format**: `SPECIES_CODE + YEAR + SEQUENCE + CHECKSUM`
Example: `MM2025000001A5` (Mouse, 2025, sequence 1, checksum A5)

## Web Interface Pages

- **Landing Page**: Search-focused entry point
- **Dashboard**: Database statistics and recent activity
- **Animals**: Browse and filter experimental subjects
- **Experiments**: View studies with filtering by species and date
- **Therapies**: Categorized treatment catalog
- **Assay Types**: Available test methodologies
- **Admin**: Data management and species configuration

## Configuration

**Environment Variables:**
- `FLASK_ENV`: Set to `production` for deployment
- `SECRET_KEY`: Application secret (required for production)
- `DATABASE_URL`: Database connection string

**Default Development Settings:**
- Database: SQLite (`invivodb.db`)
- Debug Mode: Enabled
- Port: 5000

## Contributing

This project welcomes contributions from the life sciences and software development communities. Areas of focus include:

- Data standardization and validation
- API development and documentation
- Statistical analysis tools
- Integration with external databases
- Performance optimization

## Team

**Project Lead**: Jason Lubega (@lujason01)

*Novice programmer seeking mentorship and collaboration from experienced developers to advance this essential tool for life sciences research.*  
*Full disclosure: I am usin AI tools to bring this project alive*

## License

Open source project - contributors welcome to showcase this work in their portfolios.

---  

Cheers from the **invivoDB Team**  
*Building standardized, reusable datasets for drug discovery and digital twin modeling*  
