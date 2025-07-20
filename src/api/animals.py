"""
Animals API Endpoints

REST API endpoints for managing animal data in InvivoDB.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from models.database import (
    Animal, Species, db, generate_accession_number, 
    get_species_code, parse_accession_number
)
from models.schemas import (
    AnimalCreate, AnimalUpdate, Animal as AnimalSchema,
    PaginationParams, SexEnum
)
from pydantic import ValidationError

# Create namespace
api = Namespace('animals', description='Animal management operations')

# Define models for Swagger documentation
animal_model = api.model('Animal', {
    'id': fields.Integer(required=True, description='Animal ID'),
    'accession_number': fields.String(required=True, description='Unique accession number'),
    'species_id': fields.Integer(required=True, description='Species ID'),
    'strain': fields.String(description='Animal strain'),
    'age_at_start': fields.Float(description='Age at start in weeks'),
    'weight_at_start': fields.Float(description='Weight at start in grams'),
    'sex': fields.String(description='Animal sex', enum=['Male', 'Female', 'Mixed']),
    'genetic_background': fields.String(description='Genetic background information'),
    'housing_conditions': fields.String(description='Housing conditions'),
    'ethical_approval': fields.String(description='Ethics committee approval number'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'species': fields.Nested(api.model('SpeciesInfo', {
        'id': fields.Integer,
        'common_name': fields.String,
        'scientific_name': fields.String
    }), description='Species information')
})

animal_create_model = api.model('AnimalCreate', {
    'species_id': fields.Integer(required=True, description='Species ID'),
    'strain': fields.String(description='Animal strain'),
    'age_at_start': fields.Float(description='Age at start in weeks'),
    'weight_at_start': fields.Float(description='Weight at start in grams'),
    'sex': fields.String(description='Animal sex', enum=['Male', 'Female', 'Mixed']),
    'genetic_background': fields.String(description='Genetic background information'),
    'housing_conditions': fields.String(description='Housing conditions'),
    'ethical_approval': fields.String(description='Ethics committee approval number'),
    'accession_number': fields.String(description='Custom accession number (auto-generated if not provided)')
})

animal_update_model = api.model('AnimalUpdate', {
    'species_id': fields.Integer(description='Species ID'),
    'strain': fields.String(description='Animal strain'),
    'age_at_start': fields.Float(description='Age at start in weeks'),
    'weight_at_start': fields.Float(description='Weight at start in grams'),
    'sex': fields.String(description='Animal sex', enum=['Male', 'Female', 'Mixed']),
    'genetic_background': fields.String(description='Genetic background information'),
    'housing_conditions': fields.String(description='Housing conditions'),
    'ethical_approval': fields.String(description='Ethics committee approval number')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(default=1, description='Page number'),
    'per_page': fields.Integer(default=20, description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages')
})

animals_list_model = api.model('AnimalsList', {
    'animals': fields.List(fields.Nested(animal_model)),
    'pagination': fields.Nested(pagination_model)
})


@api.route('/')
class AnimalsListAPI(Resource):
    @api.doc('list_animals')
    @api.expect(api.parser()
                .add_argument('page', type=int, location='args', default=1, help='Page number')
                .add_argument('per_page', type=int, location='args', default=20, help='Items per page')
                .add_argument('species_id', type=int, location='args', help='Filter by species ID')
                .add_argument('sex', type=str, location='args', help='Filter by sex')
                .add_argument('strain', type=str, location='args', help='Filter by strain')
                .add_argument('search', type=str, location='args', help='Search in accession number or strain'))
    @api.marshal_with(animals_list_model)
    def get(self):
        """Get list of all animals with pagination and filtering"""
        args = request.args
        page = args.get('page', 1, type=int)
        per_page = min(args.get('per_page', 20, type=int), 100)  # Max 100 items per page
        species_id = args.get('species_id', type=int)
        sex = args.get('sex', type=str)
        strain = args.get('strain', type=str)
        search = args.get('search', '', type=str)
        
        query = Animal.query.join(Species)
        
        # Apply filters
        if species_id:
            query = query.filter(Animal.species_id == species_id)
        
        if sex:
            query = query.filter(Animal.sex == sex)
        
        if strain:
            query = query.filter(Animal.strain.ilike(f'%{strain}%'))
        
        if search:
            query = query.filter(
                (Animal.accession_number.ilike(f'%{search}%')) |
                (Animal.strain.ilike(f'%{search}%'))
            )
        
        # Apply pagination
        paginated = query.order_by(Animal.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'animals': [animal_to_dict(animal) for animal in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }
    
    @api.doc('create_animal')
    @api.expect(animal_create_model)
    @api.marshal_with(animal_model, code=201)
    @api.response(400, 'Validation error')
    @api.response(404, 'Species not found')
    @api.response(409, 'Animal already exists')
    def post(self):
        """Create a new animal"""
        try:
            # Validate input data
            animal_data = AnimalCreate(**request.json)
            
            # Check if species exists
            species = Species.query.get(animal_data.species_id)
            if not species:
                api.abort(404, f'Species with ID {animal_data.species_id} not found')
            
            # Generate accession number if not provided
            accession_number = animal_data.accession_number
            if not accession_number:
                species_code = get_species_code(species.scientific_name)
                current_year = datetime.now().year
                
                # Find the next sequence number for this species and year
                last_animal = Animal.query.filter(
                    Animal.accession_number.like(f"{species_code}{current_year}%")
                ).order_by(Animal.accession_number.desc()).first()
                
                if last_animal:
                    try:
                        parsed = parse_accession_number(last_animal.accession_number)
                        sequence = parsed['sequence'] + 1
                    except ValueError:
                        sequence = 1
                else:
                    sequence = 1
                
                accession_number = generate_accession_number(species_code, current_year, sequence)
            
            # Check if accession number already exists
            existing = Animal.query.filter_by(accession_number=accession_number).first()
            if existing:
                api.abort(409, f'Animal with accession number "{accession_number}" already exists')
            
            # Create new animal
            animal = Animal(
                accession_number=accession_number,
                species_id=animal_data.species_id,
                strain=animal_data.strain,
                age_at_start=animal_data.age_at_start,
                weight_at_start=animal_data.weight_at_start,
                sex=animal_data.sex,
                genetic_background=animal_data.genetic_background,
                housing_conditions=animal_data.housing_conditions,
                ethical_approval=animal_data.ethical_approval
            )
            
            db.session.add(animal)
            db.session.commit()
            
            return animal_to_dict(animal), 201
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<int:animal_id>')
class AnimalAPI(Resource):
    @api.doc('get_animal')
    @api.marshal_with(animal_model)
    @api.response(404, 'Animal not found')
    def get(self, animal_id):
        """Get a specific animal by ID"""
        animal = Animal.query.get(animal_id)
        if not animal:
            api.abort(404, f'Animal with ID {animal_id} not found')
        return animal_to_dict(animal)
    
    @api.doc('update_animal')
    @api.expect(animal_update_model)
    @api.marshal_with(animal_model)
    @api.response(404, 'Animal not found')
    @api.response(400, 'Validation error')
    def put(self, animal_id):
        """Update a specific animal"""
        animal = Animal.query.get(animal_id)
        if not animal:
            api.abort(404, f'Animal with ID {animal_id} not found')
        
        try:
            # Validate input data
            update_data = AnimalUpdate(**request.json)
            
            # If species_id is being updated, check if the new species exists
            if hasattr(update_data, 'species_id') and update_data.species_id:
                species = Species.query.get(update_data.species_id)
                if not species:
                    api.abort(404, f'Species with ID {update_data.species_id} not found')
            
            # Update only provided fields
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(animal, field):
                    setattr(animal, field, value)
            
            # Update the updated_at timestamp
            animal.updated_at = datetime.utcnow()
            
            db.session.commit()
            return animal_to_dict(animal)
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('delete_animal')
    @api.response(204, 'Animal deleted successfully')
    @api.response(404, 'Animal not found')
    @api.response(409, 'Cannot delete animal with associated experiments')
    def delete(self, animal_id):
        """Delete a specific animal"""
        animal = Animal.query.get(animal_id)
        if not animal:
            api.abort(404, f'Animal with ID {animal_id} not found')
        
        # Check if animal has associated experiments
        if animal.experiments:
            api.abort(409, f'Cannot delete animal with {len(animal.experiments)} associated experiments')
        
        try:
            db.session.delete(animal)
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/accession/<accession_number>')
class AnimalByAccessionAPI(Resource):
    @api.doc('get_animal_by_accession')
    @api.marshal_with(animal_model)
    @api.response(404, 'Animal not found')
    def get(self, accession_number):
        """Get a specific animal by accession number"""
        animal = Animal.query.filter_by(accession_number=accession_number).first()
        if not animal:
            api.abort(404, f'Animal with accession number "{accession_number}" not found')
        return animal_to_dict(animal)


@api.route('/<int:animal_id>/experiments')
class AnimalExperimentsAPI(Resource):
    @api.doc('get_animal_experiments')
    @api.response(404, 'Animal not found')
    def get(self, animal_id):
        """Get all experiments for a specific animal"""
        animal = Animal.query.get(animal_id)
        if not animal:
            api.abort(404, f'Animal with ID {animal_id} not found')
        
        return {
            'animal_id': animal_id,
            'accession_number': animal.accession_number,
            'experiment_count': len(animal.experiments),
            'experiments': [
                {
                    'id': exp.id,
                    'title': exp.title,
                    'start_date': exp.start_date.isoformat() if exp.start_date else None,
                    'end_date': exp.end_date.isoformat() if exp.end_date else None,
                    'study_design': exp.study_design
                } for exp in animal.experiments
            ]
        }


@api.route('/generate-accession')
class GenerateAccessionAPI(Resource):
    @api.doc('generate_accession_number')
    @api.expect(api.parser()
                .add_argument('species_id', type=int, required=True, location='args', help='Species ID'))
    def get(self):
        """Generate a new accession number for a species"""
        species_id = request.args.get('species_id', type=int)
        
        if not species_id:
            api.abort(400, 'species_id parameter is required')
        
        species = Species.query.get(species_id)
        if not species:
            api.abort(404, f'Species with ID {species_id} not found')
        
        species_code = get_species_code(species.scientific_name)
        current_year = datetime.now().year
        
        # Find the next sequence number for this species and year
        last_animal = Animal.query.filter(
            Animal.accession_number.like(f"{species_code}{current_year}%")
        ).order_by(Animal.accession_number.desc()).first()
        
        if last_animal:
            try:
                parsed = parse_accession_number(last_animal.accession_number)
                sequence = parsed['sequence'] + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1
        
        accession_number = generate_accession_number(species_code, current_year, sequence)
        
        return {
            'accession_number': accession_number,
            'species_id': species_id,
            'species_name': species.common_name,
            'species_code': species_code,
            'year': current_year,
            'sequence': sequence
        }


def animal_to_dict(animal):
    """Convert Animal object to dictionary for JSON serialization"""
    return {
        'id': animal.id,
        'accession_number': animal.accession_number,
        'species_id': animal.species_id,
        'strain': animal.strain,
        'age_at_start': animal.age_at_start,
        'weight_at_start': animal.weight_at_start,
        'sex': animal.sex,
        'genetic_background': animal.genetic_background,
        'housing_conditions': animal.housing_conditions,
        'ethical_approval': animal.ethical_approval,
        'created_at': animal.created_at.isoformat() if animal.created_at else None,
        'updated_at': animal.updated_at.isoformat() if animal.updated_at else None,
        'species': {
            'id': animal.species.id,
            'common_name': animal.species.common_name,
            'scientific_name': animal.species.scientific_name
        } if animal.species else None
    }
