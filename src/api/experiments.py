"""
Experiments API Endpoints

REST API endpoints for managing experiment data in InvivoDB.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from models.database import Experiment, Animal, db
from models.schemas import (
    ExperimentCreate, ExperimentUpdate, Experiment as ExperimentSchema,
    PaginationParams, StudyDesignEnum
)
from pydantic import ValidationError

# Create namespace
api = Namespace('experiments', description='Experiment management operations')

# Define models for Swagger documentation
experiment_model = api.model('Experiment', {
    'id': fields.Integer(required=True, description='Experiment ID'),
    'title': fields.String(required=True, description='Experiment title'),
    'animal_id': fields.Integer(required=True, description='Animal ID'),
    'start_date': fields.DateTime(required=True, description='Start date'),
    'end_date': fields.DateTime(description='End date'),
    'study_design': fields.String(description='Study design type', enum=[
        'Randomized', 'Controlled', 'Observational', 'Crossover'
    ]),
    'primary_endpoint': fields.String(description='Primary endpoint'),
    'secondary_endpoints': fields.String(description='Secondary endpoints'),
    'inclusion_criteria': fields.String(description='Inclusion criteria'),
    'exclusion_criteria': fields.String(description='Exclusion criteria'),
    'statistical_method': fields.String(description='Statistical method'),
    'sample_size': fields.Integer(description='Sample size'),
    'power_analysis': fields.String(description='Power analysis details'),
    'blinding': fields.Boolean(description='Whether the study was blinded'),
    'randomization': fields.Boolean(description='Whether randomization was used'),
    'control_group': fields.String(description='Control group description'),
    'notes': fields.String(description='Additional notes'),
    'publication_doi': fields.String(description='Associated publication DOI'),
    'data_availability': fields.String(description='Data availability'),
    'animal': fields.Nested(api.model('AnimalInfo', {
        'id': fields.Integer,
        'accession_number': fields.String,
        'species_name': fields.String
    }), description='Animal information')
})

experiment_create_model = api.model('ExperimentCreate', {
    'title': fields.String(required=True, description='Experiment title'),
    'animal_id': fields.Integer(required=True, description='Animal ID'),
    'start_date': fields.DateTime(required=True, description='Start date'),
    'end_date': fields.DateTime(description='End date'),
    'study_design': fields.String(description='Study design type', enum=[
        'Randomized', 'Controlled', 'Observational', 'Crossover'
    ]),
    'primary_endpoint': fields.String(description='Primary endpoint'),
    'secondary_endpoints': fields.String(description='Secondary endpoints'),
    'inclusion_criteria': fields.String(description='Inclusion criteria'),
    'exclusion_criteria': fields.String(description='Exclusion criteria'),
    'statistical_method': fields.String(description='Statistical method'),
    'sample_size': fields.Integer(description='Sample size'),
    'power_analysis': fields.String(description='Power analysis details'),
    'blinding': fields.Boolean(description='Whether the study was blinded'),
    'randomization': fields.Boolean(description='Whether randomization was used'),
    'control_group': fields.String(description='Control group description'),
    'notes': fields.String(description='Additional notes'),
    'publication_doi': fields.String(description='Associated publication DOI'),
    'data_availability': fields.String(description='Data availability')
})

experiment_update_model = api.model('ExperimentUpdate', {
    'title': fields.String(description='Experiment title'),
    'animal_id': fields.Integer(description='Animal ID'),
    'start_date': fields.DateTime(description='Start date'),
    'end_date': fields.DateTime(description='End date'),
    'study_design': fields.String(description='Study design type', enum=[
        'Randomized', 'Controlled', 'Observational', 'Crossover'
    ]),
    'primary_endpoint': fields.String(description='Primary endpoint'),
    'secondary_endpoints': fields.String(description='Secondary endpoints'),
    'inclusion_criteria': fields.String(description='Inclusion criteria'),
    'exclusion_criteria': fields.String(description='Exclusion criteria'),
    'statistical_method': fields.String(description='Statistical method'),
    'sample_size': fields.Integer(description='Sample size'),
    'power_analysis': fields.String(description='Power analysis details'),
    'blinding': fields.Boolean(description='Whether the study was blinded'),
    'randomization': fields.Boolean(description='Whether randomization was used'),
    'control_group': fields.String(description='Control group description'),
    'notes': fields.String(description='Additional notes'),
    'publication_doi': fields.String(description='Associated publication DOI'),
    'data_availability': fields.String(description='Data availability')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(default=1, description='Page number'),
    'per_page': fields.Integer(default=20, description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages')
})

experiments_list_model = api.model('ExperimentsList', {
    'experiments': fields.List(fields.Nested(experiment_model)),
    'pagination': fields.Nested(pagination_model)
})


@api.route('/')
class ExperimentsListAPI(Resource):
    @api.doc('list_experiments')
    @api.expect(api.parser()
                .add_argument('page', type=int, location='args', default=1, help='Page number')
                .add_argument('per_page', type=int, location='args', default=20, help='Items per page')
                .add_argument('animal_id', type=int, location='args', help='Filter by animal ID')
                .add_argument('species_id', type=int, location='args', help='Filter by species ID')
                .add_argument('study_design', type=str, location='args', help='Filter by study design')
                .add_argument('start_date_from', type=str, location='args', help='Filter by start date (from)')
                .add_argument('start_date_to', type=str, location='args', help='Filter by start date (to)')
                .add_argument('search', type=str, location='args', help='Search in title or notes'))
    @api.marshal_with(experiments_list_model)
    def get(self):
        """Get list of all experiments with pagination and filtering"""
        args = request.args
        page = args.get('page', 1, type=int)
        per_page = min(args.get('per_page', 20, type=int), 100)  # Max 100 items per page
        animal_id = args.get('animal_id', type=int)
        species_id = args.get('species_id', type=int)
        study_design = args.get('study_design', type=str)
        start_date_from = args.get('start_date_from', type=str)
        start_date_to = args.get('start_date_to', type=str)
        search = args.get('search', '', type=str)
        
        query = Experiment.query.join(Animal)
        
        # Apply filters
        if animal_id:
            query = query.filter(Experiment.animal_id == animal_id)
        
        if species_id:
            query = query.filter(Animal.species_id == species_id)
        
        if study_design:
            query = query.filter(Experiment.study_design.ilike(f'%{study_design}%'))
        
        if start_date_from:
            try:
                start_date_from = datetime.strptime(start_date_from, '%Y-%m-%d')
                query = query.filter(Experiment.start_date >= start_date_from)
            except ValueError:
                pass
        
        if start_date_to:
            try:
                start_date_to = datetime.strptime(start_date_to, '%Y-%m-%d')
                query = query.filter(Experiment.start_date <= start_date_to)
            except ValueError:
                pass
        
        if search:
            query = query.filter(
                (Experiment.title.ilike(f'%{search}%')) |
                (Experiment.notes.ilike(f'%{search}%'))
            )
        
        # Apply pagination
        paginated = query.order_by(Experiment.start_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'experiments': [experiment_to_dict(experiment) for experiment in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }
    
    @api.doc('create_experiment')
    @api.expect(experiment_create_model)
    @api.marshal_with(experiment_model, code=201)
    @api.response(400, 'Validation error')
    @api.response(404, 'Animal not found')
    @api.response(409, 'Experiment already exists')
    def post(self):
        """Create a new experiment"""
        try:
            # Validate input data
            experiment_data = ExperimentCreate(**request.json)
            
            # Check if animal exists
            animal = Animal.query.get(experiment_data.animal_id)
            if not animal:
                api.abort(404, f'Animal with ID {experiment_data.animal_id} not found')
            
            # Create new experiment
            experiment = Experiment(
                title=experiment_data.title,
                animal_id=experiment_data.animal_id,
                start_date=experiment_data.start_date,
                end_date=experiment_data.end_date,
                study_design=experiment_data.study_design,
                primary_endpoint=experiment_data.primary_endpoint,
                secondary_endpoints=experiment_data.secondary_endpoints,
                inclusion_criteria=experiment_data.inclusion_criteria,
                exclusion_criteria=experiment_data.exclusion_criteria,
                statistical_method=experiment_data.statistical_method,
                sample_size=experiment_data.sample_size,
                power_analysis=experiment_data.power_analysis,
                blinding=experiment_data.blinding,
                randomization=experiment_data.randomization,
                control_group=experiment_data.control_group,
                notes=experiment_data.notes,
                publication_doi=experiment_data.publication_doi,
                data_availability=experiment_data.data_availability
            )
            
            db.session.add(experiment)
            db.session.commit()
            
            return experiment_to_dict(experiment), 201
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<int:experiment_id>')
class ExperimentAPI(Resource):
    @api.doc('get_experiment')
    @api.marshal_with(experiment_model)
    @api.response(404, 'Experiment not found')
    def get(self, experiment_id):
        """Get a specific experiment by ID"""
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            api.abort(404, f'Experiment with ID {experiment_id} not found')
        return experiment_to_dict(experiment)
    
    @api.doc('update_experiment')
    @api.expect(experiment_update_model)
    @api.marshal_with(experiment_model)
    @api.response(404, 'Experiment not found')
    @api.response(400, 'Validation error')
    def put(self, experiment_id):
        """Update a specific experiment"""
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            api.abort(404, f'Experiment with ID {experiment_id} not found')
        
        try:
            # Validate input data
            update_data = ExperimentUpdate(**request.json)
            
            # If animal_id is being updated, check if the new animal exists
            if hasattr(update_data, 'animal_id') and update_data.animal_id:
                animal = Animal.query.get(update_data.animal_id)
                if not animal:
                    api.abort(404, f'Animal with ID {update_data.animal_id} not found')
            
            # Update only provided fields
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(experiment, field):
                    setattr(experiment, field, value)
            
            db.session.commit()
            return experiment_to_dict(experiment)
            
        except ValidationError as e:
            api.abort(400, f'Validation error: {e}')
        except IntegrityError as e:
            db.session.rollback()
            api.abort(409, f'Database constraint error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('delete_experiment')
    @api.response(204, 'Experiment deleted successfully')
    @api.response(404, 'Experiment not found')
    def delete(self, experiment_id):
        """Delete a specific experiment"""
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            api.abort(404, f'Experiment with ID {experiment_id} not found')
        
        try:
            db.session.delete(experiment)
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<int:experiment_id>/results')
class ExperimentResultsAPI(Resource):
    @api.doc('get_experiment_results')
    @api.response(404, 'Experiment not found')
    def get(self, experiment_id):
        """Get results for a specific experiment"""
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            api.abort(404, f'Experiment with ID {experiment_id} not found')
        
        return {
            'experiment_id': experiment_id,
            'primary_outcome': experiment.results.primary_outcome if experiment.results else None,
            'secondary_outcomes': experiment.results.secondary_outcomes if experiment.results else None,
            'conclusions': experiment.results.conclusions if experiment.results else None
        }


def experiment_to_dict(experiment):
    """Convert Experiment object to dictionary for JSON serialization"""
    return {
        'id': experiment.id,
        'title': experiment.title,
        'animal_id': experiment.animal_id,
        'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
        'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
        'study_design': experiment.study_design,
        'primary_endpoint': experiment.primary_endpoint,
        'secondary_endpoints': experiment.secondary_endpoints,
        'inclusion_criteria': experiment.inclusion_criteria,
        'exclusion_criteria': experiment.exclusion_criteria,
        'statistical_method': experiment.statistical_method,
        'sample_size': experiment.sample_size,
        'power_analysis': experiment.power_analysis,
        'blinding': experiment.blinding,
        'randomization': experiment.randomization,
        'control_group': experiment.control_group,
        'notes': experiment.notes,
        'publication_doi': experiment.publication_doi,
        'data_availability': experiment.data_availability,
        'animal': {
            'id': experiment.animal.id,
            'accession_number': experiment.animal.accession_number,
            'species_name': experiment.animal.species.common_name
        } if experiment.animal else None
    }

