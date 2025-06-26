"""
InvivoDB Pydantic Schemas

This module defines Pydantic models for API request/response validation
and serialization. These models ensure data integrity and provide
automatic API documentation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import re


class SexEnum(str, Enum):
    """Enumeration for animal sex"""
    MALE = "Male"
    FEMALE = "Female"
    MIXED = "Mixed"


class DataAvailabilityEnum(str, Enum):
    """Enumeration for data availability levels"""
    PUBLIC = "Public"
    RESTRICTED = "Restricted"
    PRIVATE = "Private"


class StudyDesignEnum(str, Enum):
    """Enumeration for study design types"""
    RANDOMIZED = "Randomized"
    CONTROLLED = "Controlled"
    OBSERVATIONAL = "Observational"
    CROSSOVER = "Crossover"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    
    class Config:
        from_attributes = True
        validate_assignment = True


# Species schemas
class SpeciesBase(BaseSchema):
    common_name: str = Field(..., max_length=100, description="Common name of the species")
    scientific_name: str = Field(..., max_length=200, description="Scientific name of the species")
    taxonomy_id: Optional[str] = Field(None, max_length=50, description="NCBI Taxonomy ID")


class SpeciesCreate(SpeciesBase):
    pass


class SpeciesUpdate(BaseSchema):
    common_name: Optional[str] = Field(None, max_length=100)
    scientific_name: Optional[str] = Field(None, max_length=200)
    taxonomy_id: Optional[str] = Field(None, max_length=50)


class Species(SpeciesBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Animal schemas
class AnimalBase(BaseSchema):
    species_id: int = Field(..., description="Species ID")
    strain: Optional[str] = Field(None, max_length=100, description="Animal strain")
    age_at_start: Optional[float] = Field(None, ge=0, description="Age at start in weeks")
    weight_at_start: Optional[float] = Field(None, ge=0, description="Weight at start in grams")
    sex: Optional[SexEnum] = Field(None, description="Animal sex")
    genetic_background: Optional[str] = Field(None, description="Genetic background information")
    housing_conditions: Optional[str] = Field(None, description="Housing and environmental conditions")
    ethical_approval: Optional[str] = Field(None, max_length=100, description="Ethics committee approval number")


class AnimalCreate(AnimalBase):
    accession_number: Optional[str] = Field(None, max_length=15, description="Auto-generated if not provided")
    
    @validator('accession_number')
    def validate_accession_number(cls, v):
        if v:
            # Import the validation function from database module
            from models.database import validate_accession_number
            if not validate_accession_number(v):
                raise ValueError('Accession number must follow format: SPECIES_CODE + YEAR + SEQUENCE + CHECKSUM (e.g., MM2025000001A5)')
        return v


class AnimalUpdate(BaseSchema):
    species_id: Optional[int] = None
    strain: Optional[str] = Field(None, max_length=100)
    age_at_start: Optional[float] = Field(None, ge=0)
    weight_at_start: Optional[float] = Field(None, ge=0)
    sex: Optional[SexEnum] = None
    genetic_background: Optional[str] = None
    housing_conditions: Optional[str] = None
    ethical_approval: Optional[str] = Field(None, max_length=100)


class Animal(AnimalBase):
    id: int
    accession_number: str
    created_at: datetime
    updated_at: datetime
    species: Optional[Species] = None


# Therapy Category schemas
class TherapyCategoryBase(BaseSchema):
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    mechanism_of_action: Optional[str] = Field(None, max_length=200, description="Mechanism of action")


class TherapyCategoryCreate(TherapyCategoryBase):
    pass


class TherapyCategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    mechanism_of_action: Optional[str] = Field(None, max_length=200)


class TherapyCategory(TherapyCategoryBase):
    id: int
    created_at: datetime


# Therapy schemas
class TherapyBase(BaseSchema):
    name: str = Field(..., max_length=200, description="Therapy name")
    category_id: int = Field(..., description="Therapy category ID")
    vector_type: Optional[str] = Field(None, max_length=100, description="Gene therapy vector type")
    dosage: Optional[str] = Field(None, max_length=100, description="Dosage information")
    administration_route: Optional[str] = Field(None, max_length=100, description="Administration route")
    description: Optional[str] = Field(None, description="Therapy description")
    molecular_target: Optional[str] = Field(None, max_length=200, description="Molecular target")
    compound_id: Optional[str] = Field(None, max_length=100, description="External compound database ID")


class TherapyCreate(TherapyBase):
    pass


class TherapyUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    vector_type: Optional[str] = Field(None, max_length=100)
    dosage: Optional[str] = Field(None, max_length=100)
    administration_route: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    molecular_target: Optional[str] = Field(None, max_length=200)
    compound_id: Optional[str] = Field(None, max_length=100)


class Therapy(TherapyBase):
    id: int
    created_at: datetime
    category: Optional[TherapyCategory] = None


# Assay Type schemas
class AssayTypeBase(BaseSchema):
    name: str = Field(..., max_length=100, description="Assay type name")
    category: Optional[str] = Field(None, max_length=100, description="Assay category")
    description: Optional[str] = Field(None, description="Assay description")
    standard_protocol: Optional[str] = Field(None, description="Standard protocol reference")
    units: Optional[str] = Field(None, max_length=50, description="Standard measurement units")


class AssayTypeCreate(AssayTypeBase):
    pass


class AssayTypeUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    standard_protocol: Optional[str] = None
    units: Optional[str] = Field(None, max_length=50)


class AssayType(AssayTypeBase):
    id: int
    created_at: datetime


# Experiment schemas
class ExperimentBase(BaseSchema):
    title: str = Field(..., max_length=300, description="Experiment title")
    animal_id: int = Field(..., description="Animal ID")
    start_date: datetime = Field(..., description="Experiment start date")
    end_date: Optional[datetime] = Field(None, description="Experiment end date")
    study_design: Optional[StudyDesignEnum] = Field(None, description="Study design type")
    primary_endpoint: Optional[str] = Field(None, max_length=200, description="Primary endpoint")
    secondary_endpoints: Optional[str] = Field(None, description="Secondary endpoints")
    inclusion_criteria: Optional[str] = Field(None, description="Inclusion criteria")
    exclusion_criteria: Optional[str] = Field(None, description="Exclusion criteria")
    statistical_method: Optional[str] = Field(None, max_length=100, description="Statistical method")
    sample_size: Optional[int] = Field(None, ge=1, description="Sample size")
    power_analysis: Optional[str] = Field(None, description="Power analysis details")
    blinding: Optional[bool] = Field(False, description="Whether the study was blinded")
    randomization: Optional[bool] = Field(False, description="Whether randomization was used")
    control_group: Optional[str] = Field(None, max_length=100, description="Control group description")
    notes: Optional[str] = Field(None, description="Additional notes")
    publication_doi: Optional[str] = Field(None, max_length=100, description="Associated publication DOI")
    data_availability: Optional[DataAvailabilityEnum] = Field(DataAvailabilityEnum.PRIVATE, description="Data availability level")


class ExperimentCreate(ExperimentBase):
    therapy_ids: Optional[List[int]] = Field(default_factory=list, description="List of therapy IDs")


class ExperimentUpdate(BaseSchema):
    title: Optional[str] = Field(None, max_length=300)
    animal_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    study_design: Optional[StudyDesignEnum] = None
    primary_endpoint: Optional[str] = Field(None, max_length=200)
    secondary_endpoints: Optional[str] = None
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None
    statistical_method: Optional[str] = Field(None, max_length=100)
    sample_size: Optional[int] = Field(None, ge=1)
    power_analysis: Optional[str] = None
    blinding: Optional[bool] = None
    randomization: Optional[bool] = None
    control_group: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    publication_doi: Optional[str] = Field(None, max_length=100)
    data_availability: Optional[DataAvailabilityEnum] = None
    therapy_ids: Optional[List[int]] = None


class Experiment(ExperimentBase):
    id: int
    duration_days: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    animal: Optional[Animal] = None
    therapies: Optional[List[Therapy]] = Field(default_factory=list)


# Assay Measurement schemas
class AssayMeasurementBase(BaseSchema):
    parameter_name: str = Field(..., max_length=100, description="Parameter name")
    value: Optional[float] = Field(None, description="Measurement value")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    reference_range_min: Optional[float] = Field(None, description="Reference range minimum")
    reference_range_max: Optional[float] = Field(None, description="Reference range maximum")
    is_normal: Optional[bool] = Field(None, description="Whether value is within normal range")
    detection_limit: Optional[float] = Field(None, description="Detection limit")
    below_detection_limit: Optional[bool] = Field(False, description="Whether value is below detection limit")
    dilution_factor: Optional[float] = Field(1.0, ge=0, description="Dilution factor applied")


class AssayMeasurementCreate(AssayMeasurementBase):
    pass


class AssayMeasurementUpdate(BaseSchema):
    parameter_name: Optional[str] = Field(None, max_length=100)
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    reference_range_min: Optional[float] = None
    reference_range_max: Optional[float] = None
    is_normal: Optional[bool] = None
    detection_limit: Optional[float] = None
    below_detection_limit: Optional[bool] = None
    dilution_factor: Optional[float] = Field(None, ge=0)


class AssayMeasurement(AssayMeasurementBase):
    id: int
    assay_id: int
    created_at: datetime


# Assay schemas
class AssayBase(BaseSchema):
    experiment_id: int = Field(..., description="Experiment ID")
    assay_type_id: int = Field(..., description="Assay type ID")
    timepoint: Optional[str] = Field(None, max_length=50, description="Timepoint description")
    timepoint_hours: Optional[float] = Field(None, ge=0, description="Hours from experiment start")
    protocol_deviation: Optional[str] = Field(None, description="Protocol deviations")
    operator: Optional[str] = Field(None, max_length=100, description="Operator name")
    equipment: Optional[str] = Field(None, max_length=200, description="Equipment used")
    batch_id: Optional[str] = Field(None, max_length=50, description="Reagent batch ID")
    quality_control_passed: Optional[bool] = Field(True, description="QC status")
    notes: Optional[str] = Field(None, description="Additional notes")


class AssayCreate(AssayBase):
    measurements: Optional[List[AssayMeasurementCreate]] = Field(default_factory=list)


class AssayUpdate(BaseSchema):
    experiment_id: Optional[int] = None
    assay_type_id: Optional[int] = None
    timepoint: Optional[str] = Field(None, max_length=50)
    timepoint_hours: Optional[float] = Field(None, ge=0)
    protocol_deviation: Optional[str] = None
    operator: Optional[str] = Field(None, max_length=100)
    equipment: Optional[str] = Field(None, max_length=200)
    batch_id: Optional[str] = Field(None, max_length=50)
    quality_control_passed: Optional[bool] = None
    notes: Optional[str] = None


class Assay(AssayBase):
    id: int
    created_at: datetime
    assay_type: Optional[AssayType] = None
    measurements: Optional[List[AssayMeasurement]] = Field(default_factory=list)


# Experiment Result schemas
class ExperimentResultBase(BaseSchema):
    primary_outcome: Optional[str] = Field(None, description="Primary outcome")
    secondary_outcomes: Optional[str] = Field(None, description="Secondary outcomes")
    statistical_significance: Optional[bool] = Field(None, description="Statistical significance")
    p_value: Optional[float] = Field(None, ge=0, le=1, description="P-value")
    effect_size: Optional[float] = Field(None, description="Effect size")
    confidence_interval: Optional[str] = Field(None, max_length=100, description="Confidence interval")
    adverse_events: Optional[str] = Field(None, description="Adverse events")
    mortality_rate: Optional[float] = Field(None, ge=0, le=100, description="Mortality rate percentage")
    efficacy_score: Optional[float] = Field(None, description="Standardized efficacy score")
    conclusions: Optional[str] = Field(None, description="Study conclusions")
    limitations: Optional[str] = Field(None, description="Study limitations")


class ExperimentResultCreate(ExperimentResultBase):
    experiment_id: int = Field(..., description="Experiment ID")


class ExperimentResultUpdate(ExperimentResultBase):
    pass


class ExperimentResult(ExperimentResultBase):
    id: int
    experiment_id: int
    created_at: datetime


# Summary schemas for dashboard/overview
class DatabaseSummary(BaseSchema):
    """Summary statistics for the database"""
    total_animals: int
    total_experiments: int
    total_therapies: int
    total_assays: int
    species_count: Dict[str, int]
    recent_experiments: int  # Last 30 days
    data_availability_breakdown: Dict[str, int]


class ExperimentSummary(BaseSchema):
    """Simplified experiment view for listings"""
    id: int
    title: str
    animal_accession: str
    species_name: str
    start_date: datetime
    duration_days: Optional[int]
    therapy_count: int
    assay_count: int
    has_results: bool
    data_availability: str


# Search and filter schemas
class ExperimentFilter(BaseSchema):
    """Filters for experiment search"""
    species_id: Optional[int] = None
    therapy_category_id: Optional[int] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    study_design: Optional[StudyDesignEnum] = None
    data_availability: Optional[DataAvailabilityEnum] = None
    has_results: Optional[bool] = None
    search_text: Optional[str] = None  # Search in title, notes, etc.


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseSchema):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

