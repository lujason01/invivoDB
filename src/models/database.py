"""
InvivoDB Database Models

This module defines the core database schema for the invivoDB project.
It includes models for experimental units (animals), experiments, therapies,
assays, and related entities.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

# Association table for many-to-many relationship between experiments and therapies
experiment_therapy_association = Table(
    'experiment_therapy',
    Base.metadata,
    Column('experiment_id', Integer, ForeignKey('experiments.id')),
    Column('therapy_id', Integer, ForeignKey('therapies.id'))
)

# Association table for many-to-many relationship between animals and assays
animal_assay_association = Table(
    'animal_assay',
    Base.metadata,
    Column('animal_id', Integer, ForeignKey('animals.id')),
    Column('assay_id', Integer, ForeignKey('assays.id'))
)


class Species(Base):
    """Species model for categorizing experimental animals"""
    __tablename__ = 'species'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    common_name = Column(String(100), nullable=False)  # e.g., "Mouse", "Rat"
    scientific_name = Column(String(200), nullable=False)  # e.g., "Mus musculus"
    taxonomy_id = Column(String(50))  # NCBI Taxonomy ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    animals = relationship("Animal", back_populates="species")


class Animal(Base):
    """Experimental unit model - represents individual animals"""
    __tablename__ = 'animals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(50), unique=True, nullable=False)  # e.g., "MM-001-2024"
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    strain = Column(String(100))  # e.g., "C57BL/6", "Sprague-Dawley"
    age_at_start = Column(Float)  # Age in weeks
    weight_at_start = Column(Float)  # Weight in grams
    sex = Column(String(10))  # "Male", "Female", "Mixed"
    genetic_background = Column(Text)  # Additional genetic information
    housing_conditions = Column(Text)  # Housing and environmental conditions
    ethical_approval = Column(String(100))  # Ethics committee approval number
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    species = relationship("Species", back_populates="animals")
    experiments = relationship("Experiment", back_populates="animal")
    assays = relationship("Assay", secondary=animal_assay_association, back_populates="animals")


class TherapyCategory(Base):
    """Categories for different types of therapies"""
    __tablename__ = 'therapy_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # e.g., "Gene Therapy", "Immunocytokines"
    description = Column(Text)
    mechanism_of_action = Column(String(200))  # MOA classification
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    therapies = relationship("Therapy", back_populates="category")


class Therapy(Base):
    """Therapy/Treatment model"""
    __tablename__ = 'therapies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('therapy_categories.id'), nullable=False)
    vector_type = Column(String(100))  # For gene therapy vectors
    dosage = Column(String(100))  # Dosage information
    administration_route = Column(String(100))  # IV, IM, oral, etc.
    description = Column(Text)
    molecular_target = Column(String(200))  # Target protein/pathway
    compound_id = Column(String(100))  # External compound database ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("TherapyCategory", back_populates="therapies")
    experiments = relationship("Experiment", secondary=experiment_therapy_association, back_populates="therapies")


class Experiment(Base):
    """Experiment model - represents individual experiments on animals"""
    __tablename__ = 'experiments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    animal_id = Column(Integer, ForeignKey('animals.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    duration_days = Column(Integer)  # Calculated field
    study_design = Column(String(100))  # "Randomized", "Controlled", etc.
    primary_endpoint = Column(String(200))
    secondary_endpoints = Column(Text)
    inclusion_criteria = Column(Text)
    exclusion_criteria = Column(Text)
    statistical_method = Column(String(100))
    sample_size = Column(Integer)
    power_analysis = Column(Text)
    blinding = Column(Boolean, default=False)
    randomization = Column(Boolean, default=False)
    control_group = Column(String(100))
    notes = Column(Text)
    publication_doi = Column(String(100))  # Associated publication
    data_availability = Column(String(50))  # "Public", "Restricted", "Private"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    animal = relationship("Animal", back_populates="experiments")
    therapies = relationship("Therapy", secondary=experiment_therapy_association, back_populates="experiments")
    assays = relationship("Assay", back_populates="experiment")
    results = relationship("ExperimentResult", back_populates="experiment")


class AssayType(Base):
    """Types of assays/tests performed"""
    __tablename__ = 'assay_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # e.g., "Blood Chemistry", "Histology"
    category = Column(String(100))  # "Biochemical", "Molecular", "Behavioral"
    description = Column(Text)
    standard_protocol = Column(Text)  # Reference to standard protocol
    units = Column(String(50))  # Standard units for measurements
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assays = relationship("Assay", back_populates="assay_type")


class Assay(Base):
    """Individual assay/test performed on animals"""
    __tablename__ = 'assays'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    assay_type_id = Column(Integer, ForeignKey('assay_types.id'), nullable=False)
    timepoint = Column(String(50))  # "Baseline", "Day 7", "End of study"
    timepoint_hours = Column(Float)  # Hours from start of experiment
    protocol_deviation = Column(Text)  # Any deviations from standard protocol
    operator = Column(String(100))  # Person who performed the assay
    equipment = Column(String(200))  # Equipment used
    batch_id = Column(String(50))  # For reagent batch tracking
    quality_control_passed = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="assays")
    assay_type = relationship("AssayType", back_populates="assays")
    animals = relationship("Animal", secondary=animal_assay_association, back_populates="assays")
    measurements = relationship("AssayMeasurement", back_populates="assay")


class AssayMeasurement(Base):
    """Individual measurements from assays"""
    __tablename__ = 'assay_measurements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assay_id = Column(Integer, ForeignKey('assays.id'), nullable=False)
    parameter_name = Column(String(100), nullable=False)  # e.g., "Glucose", "Weight"
    value = Column(Float)
    unit = Column(String(50))
    reference_range_min = Column(Float)
    reference_range_max = Column(Float)
    is_normal = Column(Boolean)
    detection_limit = Column(Float)
    below_detection_limit = Column(Boolean, default=False)
    dilution_factor = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assay = relationship("Assay", back_populates="measurements")


class ExperimentResult(Base):
    """Overall results and conclusions from experiments"""
    __tablename__ = 'experiment_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    primary_outcome = Column(Text)
    secondary_outcomes = Column(Text)
    statistical_significance = Column(Boolean)
    p_value = Column(Float)
    effect_size = Column(Float)
    confidence_interval = Column(String(100))
    adverse_events = Column(Text)
    mortality_rate = Column(Float)  # Percentage
    efficacy_score = Column(Float)  # Standardized efficacy measure
    conclusions = Column(Text)
    limitations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="results")


class DataFile(Base):
    """Files associated with experiments (raw data, images, etc.)"""
    __tablename__ = 'data_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # "CSV", "Image", "Video", etc.
    file_size = Column(Integer)  # Size in bytes
    file_path = Column(String(500))  # Path to file storage
    checksum = Column(String(64))  # For data integrity
    description = Column(Text)
    is_processed = Column(Boolean, default=False)
    processing_notes = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: We'll add relationship to experiment when needed


def generate_accession_number(species_code: str, year: int, sequence: int) -> str:
    """Generate standardized accession numbers for animals"""
    return f"{species_code}-{sequence:03d}-{year}"


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def get_species_code(scientific_name: str) -> str:
    """Get species code for accession number generation"""
    species_codes = {
        "Mus musculus": "MM",
        "Rattus norvegicus": "RN",
        "Macaca mulatta": "MAC",
        "Canis lupus familiaris": "CAN"
    }
    return species_codes.get(scientific_name, "UNK")

