"""
Species API Endpoints

REST API endpoints for managing species data in InvivoDB.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from models.database import Species, db
from models.schemas import (
    SpeciesCreate, SpeciesUpdate, Species as SpeciesSchema,
    PaginationParams, PaginatedResponse
)
from pydantic import ValidationError

# Create namespace
api = Namespace('species', description='Species management operations')

# Define models for Swagger documentation
species_model = api.model('Species', {
    'id': fields.Integer(required=True, description='Species ID'),
    'common_name': fields.String(required=True, description='Common name of the species'),
    'scientific_name': fields.String(required=True, description='Scientific name of the species'),
    'taxonomy_id': fields.String(description='NCBI Taxonomy ID'),
    'description': fields.String(description='Species description'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

species_create_model = api.model('SpeciesCreate', {
    'common_name': fields.String(required=True, description='Common name of the species'),
    'scientific_name': fields.String(required=True, description='Scientific name of the species'),
    'taxonomy_id': fields.String(description='NCBI Taxonomy ID'),
    'description': fields.String(description='Species description')
})

species_update_model = api.model('SpeciesUpdate', {
    'common_name': fields.String(description='Common name of the species'),
    'scientific_name': fields.String(description='Scientific name of the species'),
    'taxonomy_id': fields.String(description='NCBI Taxonomy ID'),
    'description': fields.String(description='Species description')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(default=1, description='Page number'),
    'per_page': fields.Integer(default=20, description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages')
})

species_list_model = api.model('SpeciesList', {
    'species': fields.List(fields.Nested(species_model)),
    'pagination': fields.Nested(pagination_model)
})


@api.route('/')
class SpeciesListAPI(Resource):
    @api.doc('list_species')
    @api.expect(api.parser()
                .add_argument('page', type=int, location='args', default=1, help='Page number')
                .add_argument('per_page', type=int, location='args', default=20, help='Items per page')
                .add_argument('search', type=str, location='args', help='Search in name or scientific name'))
    @api.marshal_with(species_list_model)
    def get(self):
        """Get list of all species with pagination"""
        args = request.args
        page = args.get('page', 1, type=int)
        per_page = min(args.get('per_page', 20, type=int), 100)  # Max 100 items per page
        search = args.get('search', '', type=str)
        
        query = Species.query
        
        # Apply search filter if provided
        if search:
            query = query.filter(
                (Species.common_name.ilike(f'%{search}%')) |
                (Species.scientific_name.ilike(f'%{search}%'))
            )
        
        # Apply pagination
        paginated = query.order_by(Species.common_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'species': [species_to_dict(s) for s in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }
    
    @api.doc('create_species')
    @api.expect(species_create_model)
    @api.marshal_with(species_model, code=201)
    @api.response(400, 'Validation error')
    @api.response(409, 'Species already exists')
    def post(self):
        """Create a new species"""
        try:
            # Validate input data
            species_data = SpeciesCreate(**request.json)
            
            # Check if species already exists
            existing = Species.query.filter(
                (Species.scientific_name == species_data.scientific_name) |
                (Species.common_name == species_data.common_name)
            ).first()
            
            if existing:
                api.abort(409, f'Species with name "{species_data.common_name}" or scientific name "{species_data.scientific_name}" already exists')
            
            # Create new species
            species = Species(
                common_name=species_data.common_name,
                scientific_name=species_data.scientific_name,
                taxonomy_id=species_data.taxonomy_id,
                description=getattr(species_data, 'description', None)
            )
            
            db.session.add(species)
            db.session.commit()
            
            return species_to_dict(species), 201
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<int:species_id>')
class SpeciesAPI(Resource):
    @api.doc('get_species')
    @api.marshal_with(species_model)
    @api.response(404, 'Species not found')
    def get(self, species_id):
        """Get a specific species by ID"""
        species = Species.query.get(species_id)
        if not species:
            api.abort(404, f'Species with ID {species_id} not found')
        return species_to_dict(species)
    
    @api.doc('update_species')
    @api.expect(species_update_model)
    @api.marshal_with(species_model)
    @api.response(404, 'Species not found')
    @api.response(400, 'Validation error')
    def put(self, species_id):
        """Update a specific species"""
        species = Species.query.get(species_id)
        if not species:
            api.abort(404, f'Species with ID {species_id} not found')
        
        try:
            # Validate input data
            update_data = SpeciesUpdate(**request.json)
            
            # Update only provided fields
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(species, field):
                    setattr(species, field, value)
            
            db.session.commit()
            return species_to_dict(species)
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('delete_species')
    @api.response(204, 'Species deleted successfully')
    @api.response(404, 'Species not found')
    @api.response(409, 'Cannot delete species with associated animals')
    def delete(self, species_id):
        """Delete a specific species"""
        species = Species.query.get(species_id)
        if not species:
            api.abort(404, f'Species with ID {species_id} not found')
        
        # Check if species has associated animals
        if species.animals:
            api.abort(409, f'Cannot delete species with {len(species.animals)} associated animals')
        
        try:
            db.session.delete(species)
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<int:species_id>/animals')
class SpeciesAnimalsAPI(Resource):
    @api.doc('get_species_animals')
    @api.response(404, 'Species not found')
    def get(self, species_id):
        """Get all animals for a specific species"""
        species = Species.query.get(species_id)
        if not species:
            api.abort(404, f'Species with ID {species_id} not found')
        
        # This would need the Animal model imported and animal_to_dict function
        # For now, return basic info
        return {
            'species_id': species_id,
            'species_name': species.common_name,
            'animal_count': len(species.animals),
            'animals': [{'id': animal.id, 'accession_number': animal.accession_number} 
                       for animal in species.animals]
        }


def species_to_dict(species):
    """Convert Species object to dictionary for JSON serialization"""
    return {
        'id': species.id,
        'common_name': species.common_name,
        'scientific_name': species.scientific_name,
        'taxonomy_id': species.taxonomy_id,
        'description': species.description,
        'created_at': species.created_at.isoformat() if species.created_at else None
    }
