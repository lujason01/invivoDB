"""
InvivoDB Database Models (Flask-SQLAlchemy version)

This module defines the core database schema for the invivoDB project.
All models inherit from db.Model (Flask-SQLAlchemy).
"""

from datetime import datetime
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
import uuid

db = SQLAlchemy()

# Association table for many-to-many relationship between experiments and therapies
experiment_therapy_association = db.Table(
    'experiment_therapy',
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiments.id')),
    db.Column('therapy_id', db.Integer, db.ForeignKey('therapies.id'))
)

# Association table for many-to-many relationship between animals and assays
animal_assay_association = db.Table(
    'animal_assay',
    db.Column('animal_id', db.Integer, db.ForeignKey('animals.id')),
    db.Column('assay_id', db.Integer, db.ForeignKey('assays.id'))
)

class Species(db.Model):
    """Species model for categorizing experimental animals"""
    __tablename__ = 'species'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    common_name = db.Column(db.String(100), nullable=False)  # e.g., "Mouse", "Rat"
    scientific_name = db.Column(db.String(200), nullable=False)  # e.g., "Mus musculus"
    taxonomy_id = db.Column(db.String(50))  # NCBI Taxonomy ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    animals = db.relationship("Animal", back_populates="species")


class Animal(db.Model):
    """Experimental unit model - represents individual animals"""
    __tablename__ = 'animals'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accession_number = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "MM-001-2024"
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    strain = db.Column(db.String(100))  # e.g., "C57BL/6", "Sprague-Dawley"
    age_at_start = db.Column(db.Float)  # Age in weeks
    weight_at_start = db.Column(db.Float)  # Weight in grams
    sex = db.Column(db.String(10))  # "Male", "Female", "Mixed"
    genetic_background = db.Column(db.Text)  # Additional genetic information
    housing_conditions = db.Column(db.Text)  # Housing and environmental conditions
    ethical_approval = db.Column(db.String(100))  # Ethics committee approval number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    species = db.relationship("Species", back_populates="animals")
    experiments = db.relationship("Experiment", back_populates="animal")
    assays = db.relationship("Assay", secondary=animal_assay_association, back_populates="animals")


class TherapyCategory(db.Model):
    """Categories for different types of therapies"""
    __tablename__ = 'therapy_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Gene Therapy", "Immunocytokines"
    description = db.Column(db.Text)
    mechanism_of_action = db.Column(db.String(200))  # MOA classification
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    therapies = db.relationship("Therapy", back_populates="category")


class Therapy(db.Model):
    """Therapy/Treatment model"""
    __tablename__ = 'therapies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('therapy_categories.id'), nullable=False)
    vector_type = db.Column(db.String(100))  # For gene therapy vectors
    dosage = db.Column(db.String(100))  # Dosage information
    administration_route = db.Column(db.String(100))  # IV, IM, oral, etc.
    description = db.Column(db.Text)
    molecular_target = db.Column(db.String(200))  # Target protein/pathway
    compound_id = db.Column(db.String(100))  # External compound database ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    category = db.relationship("TherapyCategory", back_populates="therapies")
    experiments = db.relationship("Experiment", secondary=experiment_therapy_association, back_populates="therapies")


class Experiment(db.Model):
    """Experiment model - represents individual experiments on animals"""
    __tablename__ = 'experiments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    duration_days = db.Column(db.Integer)  # Calculated field
    study_design = db.Column(db.String(100))  # "Randomized", "Controlled", etc.
    primary_endpoint = db.Column(db.String(200))
    secondary_endpoints = db.Column(db.Text)
    inclusion_criteria = db.Column(db.Text)
    exclusion_criteria = db.Column(db.Text)
    statistical_method = db.Column(db.String(100))
    sample_size = db.Column(db.Integer)
    power_analysis = db.Column(db.Text)
    blinding = db.Column(db.Boolean, default=False)
    randomization = db.Column(db.Boolean, default=False)
    control_group = db.Column(db.String(100))
    notes = db.Column(db.Text)
    publication_doi = db.Column(db.String(100))  # Associated publication
    data_availability = db.Column(db.String(50))  # "Public", "Restricted", "Private"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    animal = db.relationship("Animal", back_populates="experiments")
    therapies = db.relationship("Therapy", secondary=experiment_therapy_association, back_populates="experiments")
    assays = db.relationship("Assay", back_populates="experiment")
    results = db.relationship("ExperimentResult", back_populates="experiment")


class AssayType(db.Model):
    """Types of assays/tests performed"""
    __tablename__ = 'assay_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Blood Chemistry", "Histology"
    category = db.Column(db.String(100))  # "Biochemical", "Molecular", "Behavioral"
    description = db.Column(db.Text)
    standard_protocol = db.Column(db.Text)  # Reference to standard protocol
    units = db.Column(db.String(50))  # Standard units for measurements
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assays = db.relationship("Assay", back_populates="assay_type")


class Assay(db.Model):
    """Individual assay/test performed on animals"""
    __tablename__ = 'assays'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    assay_type_id = db.Column(db.Integer, db.ForeignKey('assay_types.id'), nullable=False)
    timepoint = db.Column(db.String(50))  # "Baseline", "Day 7", "End of study"
    timepoint_hours = db.Column(db.Float)  # Hours from start of experiment
    protocol_deviation = db.Column(db.Text)  # Any deviations from standard protocol
    operator = db.Column(db.String(100))  # Person who performed the assay
    equipment = db.Column(db.String(200))  # Equipment used
    batch_id = db.Column(db.String(50))  # For reagent batch tracking
    quality_control_passed = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = db.relationship("Experiment", back_populates="assays")
    assay_type = db.relationship("AssayType", back_populates="assays")
    animals = db.relationship("Animal", secondary=animal_assay_association, back_populates="assays")
    measurements = db.relationship("AssayMeasurement", back_populates="assay")


class AssayMeasurement(db.Model):
    """Individual measurements from assays"""
    __tablename__ = 'assay_measurements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assay_id = db.Column(db.Integer, db.ForeignKey('assays.id'), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)  # e.g., "Glucose", "Weight"
    value = db.Column(db.Float)
    unit = db.Column(db.String(50))
    reference_range_min = db.Column(db.Float)
    reference_range_max = db.Column(db.Float)
    is_normal = db.Column(db.Boolean)
    detection_limit = db.Column(db.Float)
    below_detection_limit = db.Column(db.Boolean, default=False)
    dilution_factor = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assay = db.relationship("Assay", back_populates="measurements")


class ExperimentResult(db.Model):
    """Overall results and conclusions from experiments"""
    __tablename__ = 'experiment_results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    primary_outcome = db.Column(db.Text)
    secondary_outcomes = db.Column(db.Text)
    statistical_significance = db.Column(db.Boolean)
    p_value = db.Column(db.Float)
    effect_size = db.Column(db.Float)
    confidence_interval = db.Column(db.String(100))
    adverse_events = db.Column(db.Text)
    mortality_rate = db.Column(db.Float)  # Percentage
    efficacy_score = db.Column(db.Float)  # Standardized efficacy measure
    conclusions = db.Column(db.Text)
    limitations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = db.relationship("Experiment", back_populates="results")


class DataFile(db.Model):
    """Files associated with experiments (raw data, images, etc.)"""
    __tablename__ = 'data_files'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # "CSV", "Image", "Video", etc.
    file_size = db.Column(db.Integer)  # Size in bytes
    file_path = db.Column(db.String(500))  # Path to file storage
    checksum = db.Column(db.String(64))  # For data integrity
    description = db.Column(db.Text)
    is_processed = db.Column(db.Boolean, default=False)
    processing_notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Note: We'll add relationship to experiment when needed


def generate_accession_number(species_code: str, year: int, sequence: int) -> str:
    """Generate standardized accession numbers for animals"""
    return f"{species_code}-{sequence:03d}-{year}"


def create_tables(engine):
    """Create all tables in the database"""
    db.create_all(bind=engine)


def get_species_code(scientific_name: str) -> str:
    """Get species code for accession number generation"""
    species_codes = {
        "Mus musculus": "MM",
        "Rattus norvegicus": "RN",
        "Macaca mulatta": "MAC",
        "Canis lupus familiaris": "CAN"
    }
    return species_codes.get(scientific_name, "UNK")

