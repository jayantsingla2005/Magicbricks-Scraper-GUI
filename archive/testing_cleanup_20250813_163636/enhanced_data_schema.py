#!/usr/bin/env python3
"""
Enhanced Data Schema for MagicBricks Scraper
Comprehensive database schema and models to handle detailed property information
including edge cases, multi-property types, and comprehensive field coverage.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, 
    JSON, Enum, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from typing import Dict, List, Any, Optional

Base = declarative_base()


# Enums for standardized values
class PropertyTypeEnum(enum.Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    VILLA = "villa"
    FLOOR = "floor"
    PLOT = "plot"
    PENTHOUSE = "penthouse"
    STUDIO = "studio"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    FARMHOUSE = "farmhouse"
    COMMERCIAL_CUM_RESIDENTIAL = "commercial_cum_residential"
    MIXED_USE = "mixed_use"
    OTHER = "other"


class TransactionTypeEnum(enum.Enum):
    SALE = "sale"
    RENT = "rent"
    PG = "pg"
    LEASE = "lease"


class PropertyStatusEnum(enum.Enum):
    READY_TO_MOVE = "ready_to_move"
    UNDER_CONSTRUCTION = "under_construction"
    PRE_LAUNCH = "pre_launch"
    NEW_LAUNCH = "new_launch"
    RESALE = "resale"
    UNKNOWN = "unknown"


class FurnishingEnum(enum.Enum):
    FURNISHED = "furnished"
    SEMI_FURNISHED = "semi_furnished"
    UNFURNISHED = "unfurnished"
    UNKNOWN = "unknown"


class FacingEnum(enum.Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTH_EAST = "north_east"
    NORTH_WEST = "north_west"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"
    UNKNOWN = "unknown"


class PriceTypeEnum(enum.Enum):
    FIXED = "fixed"
    NEGOTIABLE = "negotiable"
    ON_REQUEST = "on_request"
    STARTING_FROM = "starting_from"
    RANGE = "range"
    UNKNOWN = "unknown"


# Main Property Table
class Property(Base):
    __tablename__ = 'properties'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_url = Column(String(500), unique=True, nullable=False, index=True)
    magicbricks_id = Column(String(50), unique=True, index=True)
    
    # Basic property information
    title = Column(String(500))
    property_type = Column(Enum(PropertyTypeEnum))
    transaction_type = Column(Enum(TransactionTypeEnum), default=TransactionTypeEnum.SALE)
    
    # Location information
    city = Column(String(100), index=True)
    locality = Column(String(200), index=True)
    society = Column(String(300))
    address = Column(Text)
    
    # Configuration
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    balconies = Column(Integer)
    
    # Area information (in sqft as base unit)
    area = Column(Float)  # Built-up area
    super_area = Column(Float)  # Super built-up area
    carpet_area = Column(Float)  # Carpet area
    plot_area = Column(Float)  # Plot area (for plots/houses)
    
    # Area metadata
    area_unit = Column(String(20), default='sqft')
    area_type = Column(String(50))  # 'built_up', 'super', 'carpet', 'plot'
    area_approximate = Column(Boolean, default=False)
    area_range_min = Column(Float)
    area_range_max = Column(Float)
    
    # Price information
    price = Column(Float)
    price_unit = Column(String(20))  # 'lac', 'cr', 'per_sqft'
    price_type = Column(Enum(PriceTypeEnum), default=PriceTypeEnum.FIXED)
    price_negotiable = Column(Boolean, default=False)
    price_on_request = Column(Boolean, default=False)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    price_per_sqft = Column(Float)
    
    # Property details
    floor = Column(String(50))
    total_floors = Column(Integer)
    age = Column(String(50))  # '1-5 years', 'new', etc.
    furnishing = Column(Enum(FurnishingEnum))
    facing = Column(Enum(FacingEnum))
    parking = Column(String(100))
    status = Column(Enum(PropertyStatusEnum))
    possession = Column(String(100))
    
    # Additional configuration details
    property_subtype = Column(String(100))  # 'studio', 'duplex', etc.
    original_configuration = Column(String(50))  # Original text like '2 RK'
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    source_page_url = Column(String(500))
    
    # Data quality flags
    has_edge_cases = Column(Boolean, default=False)
    edge_case_severity = Column(String(20))  # 'low', 'medium', 'high'
    data_completeness_score = Column(Float)  # 0-100 percentage
    extraction_confidence = Column(Float)  # 0-100 percentage
    
    # Raw data preservation
    raw_html = Column(Text)
    raw_text = Column(Text)
    extraction_metadata = Column(JSON)
    
    # Relationships
    amenities = relationship("PropertyAmenity", back_populates="property", cascade="all, delete-orphan")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    edge_cases = relationship("PropertyEdgeCase", back_populates="property", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_property_location', 'city', 'locality'),
        Index('idx_property_type_price', 'property_type', 'price'),
        Index('idx_property_config', 'bedrooms', 'bathrooms'),
        Index('idx_property_scraped', 'scraped_at'),
    )


# Property Amenities Table
class PropertyAmenity(Base):
    __tablename__ = 'property_amenities'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    
    # Amenity information
    amenity_name = Column(String(200), nullable=False)
    amenity_category = Column(String(100))  # 'security', 'recreation', 'utilities', etc.
    amenity_value = Column(String(500))  # Additional details if any
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    property = relationship("Property", back_populates="amenities")
    
    # Indexes
    __table_args__ = (
        Index('idx_amenity_property', 'property_id'),
        Index('idx_amenity_name', 'amenity_name'),
    )


# Property Images Table
class PropertyImage(Base):
    __tablename__ = 'property_images'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    
    # Image information
    image_url = Column(String(1000), nullable=False)
    image_type = Column(String(50))  # 'exterior', 'interior', 'floor_plan', etc.
    image_order = Column(Integer, default=0)
    image_caption = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    property = relationship("Property", back_populates="images")
    
    # Indexes
    __table_args__ = (
        Index('idx_image_property', 'property_id'),
        Index('idx_image_order', 'property_id', 'image_order'),
    )


# Property Edge Cases Table
class PropertyEdgeCase(Base):
    __tablename__ = 'property_edge_cases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    
    # Edge case information
    edge_case_category = Column(String(100), nullable=False)  # 'price', 'area', 'location', etc.
    edge_case_type = Column(String(100), nullable=False)  # Specific type within category
    edge_case_pattern = Column(String(500))  # Regex pattern that matched
    edge_case_value = Column(Text)  # The actual edge case value found
    edge_case_context = Column(Text)  # Context around the edge case
    
    # Handling information
    handled = Column(Boolean, default=False)
    handling_strategy = Column(String(200))
    fallback_value = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    property = relationship("Property", back_populates="edge_cases")
    
    # Indexes
    __table_args__ = (
        Index('idx_edge_case_property', 'property_id'),
        Index('idx_edge_case_category', 'edge_case_category'),
        Index('idx_edge_case_handled', 'handled'),
    )


# Scraping Sessions Table
class ScrapingSession(Base):
    __tablename__ = 'scraping_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Session information
    session_name = Column(String(200))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(50))  # 'running', 'completed', 'failed', 'cancelled'
    
    # Configuration
    target_cities = Column(JSON)
    target_property_types = Column(JSON)
    max_pages = Column(Integer)
    max_properties = Column(Integer)
    
    # Results
    pages_scraped = Column(Integer, default=0)
    properties_found = Column(Integer, default=0)
    properties_saved = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_page_load_time = Column(Float)
    avg_extraction_time = Column(Float)
    success_rate = Column(Float)
    
    # Metadata
    scraper_version = Column(String(50))
    configuration = Column(JSON)
    error_log = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_session_time', 'start_time'),
        Index('idx_session_status', 'status'),
    )


# Data Quality Metrics Table
class DataQualityMetric(Base):
    __tablename__ = 'data_quality_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric information
    metric_date = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(100), nullable=False)  # 'field_completeness', 'edge_case_prevalence', etc.
    metric_category = Column(String(100))  # 'overall', 'by_city', 'by_property_type', etc.
    metric_subcategory = Column(String(100))  # Specific city, property type, etc.
    
    # Metric values
    metric_value = Column(Float, nullable=False)
    metric_count = Column(Integer)
    metric_percentage = Column(Float)
    
    # Additional data
    metric_details = Column(JSON)
    
    # Indexes
    __table_args__ = (
        Index('idx_metric_date_type', 'metric_date', 'metric_type'),
        Index('idx_metric_category', 'metric_category', 'metric_subcategory'),
    )


class EnhancedDataSchema:
    """
    Enhanced data schema manager for MagicBricks scraper
    """
    
    def __init__(self, database_url: str = "sqlite:///magicbricks_enhanced.db"):
        """Initialize enhanced data schema"""
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_all_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        print("[SUCCESS] All enhanced database tables created successfully")
    
    def drop_all_tables(self):
        """Drop all tables in the database"""
        Base.metadata.drop_all(bind=self.engine)
        print("🗑️ All database tables dropped")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_property(self, property_data: Dict[str, Any]) -> Property:
        """Create a new property record with enhanced schema support"""
        
        # Extract and validate property data
        property_record = Property(
            property_url=property_data.get('property_url'),
            magicbricks_id=property_data.get('magicbricks_id'),
            title=property_data.get('title'),
            property_type=self._parse_property_type(property_data.get('property_type')),
            transaction_type=self._parse_transaction_type(property_data.get('transaction_type', 'sale')),
            
            # Location
            city=property_data.get('city'),
            locality=property_data.get('locality'),
            society=property_data.get('society'),
            address=property_data.get('address'),
            
            # Configuration
            bedrooms=self._parse_int(property_data.get('bedrooms')),
            bathrooms=self._parse_int(property_data.get('bathrooms')),
            balconies=self._parse_int(property_data.get('balconies')),
            
            # Area
            area=self._parse_float(property_data.get('area')),
            super_area=self._parse_float(property_data.get('super_area')),
            carpet_area=self._parse_float(property_data.get('carpet_area')),
            plot_area=self._parse_float(property_data.get('plot_area')),
            area_unit=property_data.get('area_unit', 'sqft'),
            area_type=property_data.get('area_type'),
            area_approximate=property_data.get('area_approximate', False),
            area_range_min=self._parse_float(property_data.get('area_range_min')),
            area_range_max=self._parse_float(property_data.get('area_range_max')),
            
            # Price
            price=self._parse_float(property_data.get('price')),
            price_unit=property_data.get('price_unit'),
            price_type=self._parse_price_type(property_data.get('price_type', 'fixed')),
            price_negotiable=property_data.get('price_negotiable', False),
            price_on_request=property_data.get('price_on_request', False),
            price_range_min=self._parse_float(property_data.get('price_range_min')),
            price_range_max=self._parse_float(property_data.get('price_range_max')),
            price_per_sqft=self._parse_float(property_data.get('price_per_sqft')),
            
            # Details
            floor=property_data.get('floor'),
            total_floors=self._parse_int(property_data.get('total_floors')),
            age=property_data.get('age'),
            furnishing=self._parse_furnishing(property_data.get('furnishing')),
            facing=self._parse_facing(property_data.get('facing')),
            parking=property_data.get('parking'),
            status=self._parse_status(property_data.get('status')),
            possession=property_data.get('possession'),
            
            # Additional
            property_subtype=property_data.get('property_subtype'),
            original_configuration=property_data.get('original_configuration'),
            
            # Metadata
            source_page_url=property_data.get('source_page_url'),
            has_edge_cases=property_data.get('has_edge_cases', False),
            edge_case_severity=property_data.get('edge_case_severity'),
            data_completeness_score=property_data.get('data_completeness_score'),
            extraction_confidence=property_data.get('extraction_confidence'),
            
            # Raw data
            raw_html=property_data.get('raw_html'),
            raw_text=property_data.get('raw_text'),
            extraction_metadata=property_data.get('extraction_metadata')
        )
        
        return property_record
    
    def _parse_property_type(self, value: str) -> Optional[PropertyTypeEnum]:
        """Parse property type string to enum"""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        
        # Map common variations to enum values
        type_mapping = {
            'apartment': PropertyTypeEnum.APARTMENT,
            'flat': PropertyTypeEnum.APARTMENT,
            'house': PropertyTypeEnum.HOUSE,
            'independent house': PropertyTypeEnum.HOUSE,
            'villa': PropertyTypeEnum.VILLA,
            'floor': PropertyTypeEnum.FLOOR,
            'builder floor': PropertyTypeEnum.FLOOR,
            'independent floor': PropertyTypeEnum.FLOOR,
            'plot': PropertyTypeEnum.PLOT,
            'land': PropertyTypeEnum.PLOT,
            'penthouse': PropertyTypeEnum.PENTHOUSE,
            'studio': PropertyTypeEnum.STUDIO,
            'studio apartment': PropertyTypeEnum.STUDIO,
            'duplex': PropertyTypeEnum.DUPLEX,
            'triplex': PropertyTypeEnum.TRIPLEX,
            'farmhouse': PropertyTypeEnum.FARMHOUSE,
            'commercial cum residential': PropertyTypeEnum.COMMERCIAL_CUM_RESIDENTIAL,
            'mixed use': PropertyTypeEnum.MIXED_USE
        }
        
        return type_mapping.get(value_lower, PropertyTypeEnum.OTHER)
    
    def _parse_transaction_type(self, value: str) -> TransactionTypeEnum:
        """Parse transaction type string to enum"""
        if not value:
            return TransactionTypeEnum.SALE
        
        value_lower = value.lower().strip()
        
        if 'rent' in value_lower:
            return TransactionTypeEnum.RENT
        elif 'pg' in value_lower:
            return TransactionTypeEnum.PG
        elif 'lease' in value_lower:
            return TransactionTypeEnum.LEASE
        else:
            return TransactionTypeEnum.SALE
    
    def _parse_price_type(self, value: str) -> PriceTypeEnum:
        """Parse price type string to enum"""
        if not value:
            return PriceTypeEnum.FIXED
        
        value_lower = value.lower().strip()
        
        if 'negotiable' in value_lower:
            return PriceTypeEnum.NEGOTIABLE
        elif 'request' in value_lower:
            return PriceTypeEnum.ON_REQUEST
        elif 'starting' in value_lower or 'onwards' in value_lower:
            return PriceTypeEnum.STARTING_FROM
        elif 'range' in value_lower or '-' in value_lower:
            return PriceTypeEnum.RANGE
        else:
            return PriceTypeEnum.FIXED
    
    def _parse_furnishing(self, value: str) -> Optional[FurnishingEnum]:
        """Parse furnishing string to enum"""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        
        if 'furnished' in value_lower and 'semi' not in value_lower and 'un' not in value_lower:
            return FurnishingEnum.FURNISHED
        elif 'semi' in value_lower:
            return FurnishingEnum.SEMI_FURNISHED
        elif 'unfurnished' in value_lower or 'not furnished' in value_lower:
            return FurnishingEnum.UNFURNISHED
        else:
            return FurnishingEnum.UNKNOWN
    
    def _parse_facing(self, value: str) -> Optional[FacingEnum]:
        """Parse facing string to enum"""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        
        facing_mapping = {
            'north': FacingEnum.NORTH,
            'south': FacingEnum.SOUTH,
            'east': FacingEnum.EAST,
            'west': FacingEnum.WEST,
            'north east': FacingEnum.NORTH_EAST,
            'northeast': FacingEnum.NORTH_EAST,
            'north west': FacingEnum.NORTH_WEST,
            'northwest': FacingEnum.NORTH_WEST,
            'south east': FacingEnum.SOUTH_EAST,
            'southeast': FacingEnum.SOUTH_EAST,
            'south west': FacingEnum.SOUTH_WEST,
            'southwest': FacingEnum.SOUTH_WEST
        }
        
        return facing_mapping.get(value_lower, FacingEnum.UNKNOWN)
    
    def _parse_status(self, value: str) -> Optional[PropertyStatusEnum]:
        """Parse status string to enum"""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        
        if 'ready' in value_lower:
            return PropertyStatusEnum.READY_TO_MOVE
        elif 'under construction' in value_lower:
            return PropertyStatusEnum.UNDER_CONSTRUCTION
        elif 'pre launch' in value_lower:
            return PropertyStatusEnum.PRE_LAUNCH
        elif 'new launch' in value_lower:
            return PropertyStatusEnum.NEW_LAUNCH
        elif 'resale' in value_lower:
            return PropertyStatusEnum.RESALE
        else:
            return PropertyStatusEnum.UNKNOWN
    
    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer value"""
        if value is None:
            return None
        
        try:
            if isinstance(value, str):
                # Extract first number from string
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    return int(numbers[0])
                return None
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value) -> Optional[float]:
        """Safely parse float value"""
        if value is None:
            return None
        
        try:
            if isinstance(value, str):
                # Remove commas and extract first number
                import re
                value_clean = value.replace(',', '')
                numbers = re.findall(r'\d+\.?\d*', value_clean)
                if numbers:
                    return float(numbers[0])
                return None
            return float(value)
        except (ValueError, TypeError):
            return None


def main():
    """Main function to demonstrate enhanced data schema"""
    
    print("🗄️ Enhanced Data Schema for MagicBricks Scraper")
    print("="*60)
    
    # Initialize schema
    schema = EnhancedDataSchema()
    
    # Create tables
    print("📊 Creating enhanced database tables...")
    schema.create_all_tables()
    
    # Example property data
    example_property = {
        'property_url': 'https://www.magicbricks.com/property-for-sale/residential-real-estate?propid=12345',
        'magicbricks_id': 'MB12345',
        'title': '3 BHK Apartment for Sale in Gurgaon',
        'property_type': 'apartment',
        'city': 'Gurgaon',
        'locality': 'Sector 45',
        'society': 'DLF Phase 2',
        'bedrooms': 3,
        'bathrooms': 2,
        'area': 1200.0,
        'super_area': 1400.0,
        'price': 85.0,
        'price_unit': 'lac',
        'furnishing': 'semi furnished',
        'facing': 'north',
        'status': 'ready to move',
        'has_edge_cases': True,
        'edge_case_severity': 'medium',
        'data_completeness_score': 85.5,
        'extraction_confidence': 92.3
    }
    
    # Create property record
    print("🏠 Creating example property record...")
    session = schema.get_session()
    
    try:
        property_record = schema.create_property(example_property)
        session.add(property_record)
        session.commit()
        
        print(f"[SUCCESS] Property record created with ID: {property_record.id}")
        print(f"📊 Property type: {property_record.property_type}")
        print(f"💰 Price type: {property_record.price_type}")
        print(f"🏠 Furnishing: {property_record.furnishing}")
        
    except Exception as e:
        print(f"[ERROR] Error creating property record: {str(e)}")
        session.rollback()
    
    finally:
        session.close()
    
    print("\n[SUCCESS] Enhanced Data Schema demonstration complete!")
    print("[TARGET] Schema supports:")
    print("   • Comprehensive property information")
    print("   • Edge case handling and tracking")
    print("   • Data quality metrics")
    print("   • Flexible property types and configurations")
    print("   • Detailed amenities and images")
    print("   • Scraping session management")


if __name__ == "__main__":
    main()
