"""
InvivoDB REST API Main Module

This module sets up the Flask-RESTx API with automatic documentation
and registers all API namespaces.
"""

from flask import Flask, Blueprint
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

# Import API namespaces
from .animals import api as animals_ns
from .species import api as species_ns
from .experiments import api as experiments_ns

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize Flask-RESTx API
api = Api(
    api_bp,
    version='1.0',
    title='InvivoDB REST API',
    description='A REST API for managing in vivo experimental data for digital animal twins',
    doc='/docs/'
)

# Add namespaces
api.add_namespace(animals_ns, path='/animals')
api.add_namespace(species_ns, path='/species')
api.add_namespace(experiments_ns, path='/experiments')

def init_api(app: Flask, db: SQLAlchemy):
    """
    Initialize the API with the Flask app and database
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    # Register the API blueprint
    app.register_blueprint(api_bp)
    
    # Store db reference for use in API endpoints
    api_bp.db = db
    
    return api
