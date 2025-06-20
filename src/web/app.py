"""
InvivoDB Web Application

A Flask-based web interface for the invivoDB database system.
Provides a user-friendly interface for browsing and managing 
in vivo experimental data.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import sys

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.database import (
    db, Species, Animal, TherapyCategory, Therapy, 
    Experiment, AssayType, Assay, AssayMeasurement, 
    ExperimentResult, generate_accession_number, get_species_code
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Database configuration - using SQLite for the prototype
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invivodb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Configure the database to use our models
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    db.create_all()


@app.route('/')
def index():
    """Home page with database overview"""
    try:
        # Get summary statistics
        total_animals = Animal.query.count()
        total_experiments = Experiment.query.count()
        total_therapies = Therapy.query.count()
        total_assays = Assay.query.count()
        
        # Get species breakdown
        species_data = db.session.query(Species.common_name, db.func.count(Animal.id)).join(Animal).group_by(Species.id).all()
        species_breakdown = {name: count for name, count in species_data}
        
        # Get recent experiments (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_experiments = Experiment.query.filter(Experiment.created_at >= thirty_days_ago).count()
        
        # Get recent experiments for display
        recent_exp_list = (Experiment.query
                          .join(Animal)
                          .join(Species)
                          .order_by(Experiment.created_at.desc())
                          .limit(5)
                          .all())
        
        return render_template('index.html',
                             total_animals=total_animals,
                             total_experiments=total_experiments,
                             total_therapies=total_therapies,
                             total_assays=total_assays,
                             species_breakdown=species_breakdown,
                             recent_experiments=recent_experiments,
                             recent_exp_list=recent_exp_list)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html',
                             total_animals=0,
                             total_experiments=0,
                             total_therapies=0,
                             total_assays=0,
                             species_breakdown={},
                             recent_experiments=0,
                             recent_exp_list=[])


@app.route('/animals')
def animals():
    """List all animals"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    animals_query = Animal.query.join(Species).order_by(Animal.created_at.desc())
    animals_paginated = animals_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('animals.html', animals=animals_paginated)


@app.route('/animals/<int:animal_id>')
def animal_detail(animal_id):
    """Show detailed information about a specific animal"""
    animal = Animal.query.get_or_404(animal_id)
    experiments = Experiment.query.filter_by(animal_id=animal_id).order_by(Experiment.start_date.desc()).all()
    
    return render_template('animal_detail.html', animal=animal, experiments=experiments)


@app.route('/experiments')
def experiments():
    """List all experiments with filtering options"""
    page = request.args.get('page', 1, type=int)
    species_filter = request.args.get('species_id', type=int)
    per_page = 20
    
    experiments_query = (Experiment.query
                        .join(Animal)
                        .join(Species)
                        .order_by(Experiment.start_date.desc()))
    
    if species_filter:
        experiments_query = experiments_query.filter(Species.id == species_filter)
    
    experiments_paginated = experiments_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get species for filter dropdown
    species_list = Species.query.all()
    
    return render_template('experiments.html', 
                         experiments=experiments_paginated,
                         species_list=species_list,
                         selected_species=species_filter)


@app.route('/experiments/<int:experiment_id>')
def experiment_detail(experiment_id):
    """Show detailed information about a specific experiment"""
    experiment = Experiment.query.get_or_404(experiment_id)
    assays = Assay.query.filter_by(experiment_id=experiment_id).join(AssayType).all()
    results = ExperimentResult.query.filter_by(experiment_id=experiment_id).first()
    
    return render_template('experiment_detail.html', 
                         experiment=experiment, 
                         assays=assays,
                         results=results)


@app.route('/therapies')
def therapies():
    """List all therapies"""
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category_id', type=int)
    per_page = 20
    
    therapies_query = Therapy.query.join(TherapyCategory).order_by(Therapy.name)
    
    if category_filter:
        therapies_query = therapies_query.filter(TherapyCategory.id == category_filter)
    
    therapies_paginated = therapies_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories for filter dropdown
    categories_list = TherapyCategory.query.all()
    
    return render_template('therapies.html',
                         therapies=therapies_paginated,
                         categories_list=categories_list,
                         selected_category=category_filter)


@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal():
    """Add a new animal to the database"""
    if request.method == 'POST':
        try:
            species_id = request.form.get('species_id', type=int)
            strain = request.form.get('strain')
            age_at_start = request.form.get('age_at_start', type=float)
            weight_at_start = request.form.get('weight_at_start', type=float)
            sex = request.form.get('sex')
            genetic_background = request.form.get('genetic_background')
            housing_conditions = request.form.get('housing_conditions')
            ethical_approval = request.form.get('ethical_approval')
            
            # Generate accession number
            species = Species.query.get(species_id)
            if not species:
                flash('Invalid species selected', 'error')
                return redirect(url_for('add_animal'))
            
            # Get next sequence number for this species
            last_animal = (Animal.query
                          .filter_by(species_id=species_id)
                          .order_by(Animal.id.desc())
                          .first())
            
            sequence = 1
            if last_animal:
                # Extract sequence from last accession number
                parts = last_animal.accession_number.split('-')
                if len(parts) >= 2:
                    sequence = int(parts[1]) + 1
            
            species_code = get_species_code(species.scientific_name)
            accession_number = generate_accession_number(species_code, datetime.now().year, sequence)
            
            # Create new animal
            animal = Animal(
                accession_number=accession_number,
                species_id=species_id,
                strain=strain,
                age_at_start=age_at_start,
                weight_at_start=weight_at_start,
                sex=sex,
                genetic_background=genetic_background,
                housing_conditions=housing_conditions,
                ethical_approval=ethical_approval
            )
            
            db.session.add(animal)
            db.session.commit()
            
            flash(f'Animal {accession_number} added successfully!', 'success')
            return redirect(url_for('animal_detail', animal_id=animal.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding animal: {str(e)}', 'error')
    
    # GET request - show form
    species_list = Species.query.all()
    return render_template('add_animal.html', species_list=species_list)


@app.route('/search')
def search():
    """Search functionality across experiments"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if query:
        # Search in experiment titles, notes, and animal accession numbers
        search_filter = f'%{query}%'
        experiments_query = (Experiment.query
                           .join(Animal)
                           .join(Species)
                           .filter(
                               (Experiment.title.like(search_filter)) |
                               (Experiment.notes.like(search_filter)) |
                               (Animal.accession_number.like(search_filter))
                           )
                           .order_by(Experiment.start_date.desc()))
        
        experiments_paginated = experiments_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        experiments_paginated = None
    
    return render_template('search.html', 
                         experiments=experiments_paginated,
                         query=query)


@app.route('/api/summary')
def api_summary():
    """API endpoint for dashboard summary data"""
    try:
        total_animals = Animal.query.count()
        total_experiments = Experiment.query.count()
        total_therapies = Therapy.query.count()
        total_assays = Assay.query.count()
        
        # Species breakdown
        species_data = db.session.query(Species.common_name, db.func.count(Animal.id)).join(Animal).group_by(Species.id).all()
        species_breakdown = {name: count for name, count in species_data}
        
        # Recent experiments
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_experiments = Experiment.query.filter(Experiment.created_at >= thirty_days_ago).count()
        
        return jsonify({
            'total_animals': total_animals,
            'total_experiments': total_experiments,
            'total_therapies': total_therapies,
            'total_assays': total_assays,
            'species_breakdown': species_breakdown,
            'recent_experiments': recent_experiments
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# Initialize sample data
def init_sample_data():
    """Initialize the database with sample data for demonstration"""
    if Species.query.count() == 0:
        # Add sample species
        mouse = Species(common_name="Mouse", scientific_name="Mus musculus", taxonomy_id="10090")
        rat = Species(common_name="Rat", scientific_name="Rattus norvegicus", taxonomy_id="10116")
        
        db.session.add(mouse)
        db.session.add(rat)
        
        # Add sample therapy categories
        gene_therapy = TherapyCategory(
            name="Gene Therapy",
            description="Therapeutic delivery of genetic material",
            mechanism_of_action="Gene expression modulation"
        )
        immunotherapy = TherapyCategory(
            name="Immunotherapy",
            description="Treatments that use the immune system",
            mechanism_of_action="Immune system enhancement"
        )
        
        db.session.add(gene_therapy)
        db.session.add(immunotherapy)
        
        # Add sample assay types
        blood_chemistry = AssayType(
            name="Blood Chemistry",
            category="Biochemical",
            description="Blood chemistry analysis",
            units="Various"
        )
        histology = AssayType(
            name="Histology",
            category="Morphological",
            description="Tissue histological examination",
            units="Qualitative"
        )
        
        db.session.add(blood_chemistry)
        db.session.add(histology)
        
        db.session.commit()
        print("Sample data initialized!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

