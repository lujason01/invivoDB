# InvivoDB Prototype

This is a prototype of the InvivoDB database system for curating in vivo experimental data for digital animal twins.

## 🚀 What's Implemented

### 1. Database Schema (SQLAlchemy Models)
- **Species**: Animal species with taxonomy information
- **Animals**: Individual experimental units with accession numbers
- **Experiments**: Research studies with detailed metadata
- **Therapies & Categories**: Treatment classifications
- **Assays & Measurements**: Test data and results
- **Results**: Statistical outcomes and conclusions

### 2. Data Models (Pydantic Schemas)
- Comprehensive validation schemas for all entities
- API-ready serialization models
- Search and filtering capabilities
- Pagination support

### 3. Web Interface (Flask Application)
- **Dashboard**: Overview with statistics and recent activity
- **Animal Management**: Add and browse experimental animals
- **Experiment Browsing**: Filter and search experiments
- **Therapy Database**: Categorized treatments
- **Search Functionality**: Cross-database search
- **Responsive Design**: Bootstrap-based UI

## 🏗️ Project Structure

```
invivoDB/
├── src/
│   ├── models/
│   │   ├── database.py      # SQLAlchemy database models
│   │   └── schemas.py       # Pydantic validation schemas
│   ├── web/
│   │   ├── app.py          # Flask application
│   │   └── templates/       # HTML templates
│   │       ├── base.html
│   │       ├── index.html
│   │       └── add_animal.html
│   └── api/                 # (Future: REST API endpoints)
├── requirements.txt         # Python dependencies
└── README.md               # Original project description
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   cd src/web
   python app.py
   ```

3. **Access the Application**
   - Open your browser to: http://localhost:5000
   - The database will be automatically created with sample data

## 📊 Features Demonstrated

### ✅ Currently Working
- **Animal Registration**: Add animals with auto-generated accession numbers
- **Species Management**: Support for multiple species with proper codes
- **Database Schema**: Complete relational model for experimental data
- **Web Interface**: User-friendly browsing and data entry
- **Search**: Basic search across experiments
- **Statistics Dashboard**: Real-time database metrics

### 🔧 Next Steps (Not Yet Implemented)
- Experiment creation workflow
- Therapy addition interface
- Assay data entry forms
- File upload for experimental data
- REST API endpoints
- User authentication
- Data export functionality
- Advanced search and filtering

## 🏷️ Accession Number System

Animals are automatically assigned unique accession numbers:
- **Format**: `[SPECIES_CODE]-[SEQUENCE]-[YEAR]`
- **Examples**: 
  - `MM-001-2025` (First mouse of 2025)
  - `RN-042-2025` (42nd rat of 2025)

### Species Codes
- **MM**: Mus musculus (Mouse)
- **RN**: Rattus norvegicus (Rat)  
- **MAC**: Macaca mulatta (Macaque)
- **CAN**: Canis lupus familiaris (Dog)

## 💡 Design Principles

1. **Standardization**: Consistent data formats for reproducibility
2. **ML-Ready**: Structured data suitable for machine learning
3. **Scalability**: Database design supports large datasets
4. **User Experience**: Intuitive interface for researchers
5. **Data Integrity**: Validation at multiple levels

## 🔬 Sample Workflow

1. **Add Species** (automatically seeded)
2. **Register Animals** with biological metadata
3. **Create Experiments** linking animals to studies
4. **Record Assays** with measurements and results
5. **Analyze Data** through the dashboard interface

## 🤝 Contributing

This prototype demonstrates the core functionality. Future development areas:

- **Backend**: Complete REST API implementation
- **Frontend**: Enhanced data visualization 
- **Data**: Import/export tools for existing datasets
- **Analysis**: Built-in statistical analysis tools
- **Integration**: Connections to external databases

## 📈 Prototype Goals Achieved

✅ Database schema design and implementation  
✅ Python data models with validation  
✅ Basic web interface for data management  
✅ Automatic accession number generation  
✅ Multi-species support  
✅ Responsive design  
✅ Sample data initialization  

## 🎯 Production Roadmap

1. **Phase 1**: Complete CRUD operations for all entities
2. **Phase 2**: REST API with authentication
3. **Phase 3**: Advanced search and analytics
4. **Phase 4**: File handling and data import/export
5. **Phase 5**: Collaborative features and user management

---

**Team**: Jason Lubega (@lujason01)  
**Repository**: https://github.com/lujason01/invivoDB  
**Status**: Functional Prototype (v0.1)

