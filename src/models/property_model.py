"""
Property Data Model - Database-ready structure for MagicBricks properties
Designed for easy migration from CSV/JSON to database storage
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import re


@dataclass
class PropertyModel:
    """
    Comprehensive property data model with database-ready structure
    All fields are designed to map directly to database columns
    """
    
    # Primary identification
    property_id: Optional[str] = None
    property_url: Optional[str] = None
    
    # Basic property information
    title: Optional[str] = None
    property_type: Optional[str] = None  # Apartment, Villa, Plot, etc.
    transaction_type: Optional[str] = None  # Sale, Resale, New
    
    # Pricing information
    price: Optional[str] = None
    price_numeric: Optional[float] = None  # For database queries
    price_per_sqft: Optional[str] = None
    price_per_sqft_numeric: Optional[float] = None
    
    # Area details
    super_area: Optional[str] = None
    super_area_numeric: Optional[float] = None
    carpet_area: Optional[str] = None
    carpet_area_numeric: Optional[float] = None
    area_unit: Optional[str] = "sqft"
    
    # Property specifications
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    balconies: Optional[int] = None
    floor: Optional[str] = None
    total_floors: Optional[int] = None
    current_floor: Optional[int] = None
    
    # Property status and features
    furnishing: Optional[str] = None  # Furnished, Semi-Furnished, Unfurnished
    status: Optional[str] = None  # Ready to Move, Under Construction
    possession_date: Optional[str] = None
    age: Optional[str] = None
    facing: Optional[str] = None
    overlooking: Optional[str] = None
    ownership: Optional[str] = None  # Freehold, Leasehold
    
    # Parking and amenities
    parking: Optional[str] = None
    parking_covered: Optional[int] = None
    parking_open: Optional[int] = None
    
    # Location information
    locality: Optional[str] = None
    society: Optional[str] = None
    builder: Optional[str] = None
    sector: Optional[str] = None
    city: str = "Gurgaon"
    state: str = "Haryana"
    
    # Contact information
    owner_type: Optional[str] = None  # Owner, Agent, Builder
    owner_name: Optional[str] = None
    contact_number: Optional[str] = None
    
    # Media and additional info
    image_url: Optional[str] = None
    image_count: Optional[int] = None
    description: Optional[str] = None
    
    # Coordinates (for future enhancement)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Metadata for tracking
    scraped_at: Optional[datetime] = None
    page_number: Optional[int] = None
    position_on_page: Optional[int] = None
    data_quality_score: Optional[float] = None
    
    def __post_init__(self):
        """Post-initialization processing for data cleaning and validation"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        
        # Clean and extract numeric values
        self._extract_numeric_price()
        self._extract_numeric_area()
        self._extract_floor_details()
        self._extract_parking_details()
        self._calculate_quality_score()
    
    def _extract_numeric_price(self):
        """Extract numeric price values for database storage"""
        if self.price:
            # Extract price in rupees
            price_match = re.search(r'₹\s*([\d.,]+)\s*(Cr|Lakh|crore|lakh)?', self.price, re.IGNORECASE)
            if price_match:
                amount = float(price_match.group(1).replace(',', ''))
                unit = price_match.group(2)
                
                if unit and unit.lower() in ['cr', 'crore']:
                    self.price_numeric = amount * 10000000  # Convert crores to rupees
                elif unit and unit.lower() in ['lakh']:
                    self.price_numeric = amount * 100000  # Convert lakhs to rupees
                else:
                    self.price_numeric = amount
        
        # Extract price per sqft
        if self.price_per_sqft:
            sqft_match = re.search(r'₹\s*([\d.,]+)', self.price_per_sqft)
            if sqft_match:
                self.price_per_sqft_numeric = float(sqft_match.group(1).replace(',', ''))
    
    def _extract_numeric_area(self):
        """Extract numeric area values"""
        for area_field in ['super_area', 'carpet_area']:
            area_value = getattr(self, area_field)
            if area_value:
                area_match = re.search(r'([\d.,]+)\s*sqft', area_value, re.IGNORECASE)
                if area_match:
                    numeric_field = f"{area_field}_numeric"
                    setattr(self, numeric_field, float(area_match.group(1).replace(',', '')))
    
    def _extract_floor_details(self):
        """Extract floor information"""
        if self.floor:
            # Pattern: "7 out of 12" or "Ground Floor" or "7th Floor"
            floor_match = re.search(r'(\d+)\s*out\s*of\s*(\d+)', self.floor, re.IGNORECASE)
            if floor_match:
                self.current_floor = int(floor_match.group(1))
                self.total_floors = int(floor_match.group(2))
            else:
                # Try to extract single floor number
                single_floor = re.search(r'(\d+)', self.floor)
                if single_floor:
                    self.current_floor = int(single_floor.group(1))
    
    def _extract_parking_details(self):
        """Extract parking information"""
        if self.parking:
            covered_match = re.search(r'(\d+)\s*covered', self.parking, re.IGNORECASE)
            open_match = re.search(r'(\d+)\s*open', self.parking, re.IGNORECASE)
            
            if covered_match:
                self.parking_covered = int(covered_match.group(1))
            if open_match:
                self.parking_open = int(open_match.group(1))
    
    def _calculate_quality_score(self):
        """Calculate data quality score based on field completeness"""
        total_fields = 0
        filled_fields = 0
        
        important_fields = [
            'title', 'price', 'property_type', 'bedrooms', 'bathrooms',
            'super_area', 'locality', 'society', 'furnishing', 'status'
        ]
        
        for field in important_fields:
            total_fields += 1
            if getattr(self, field) is not None:
                filled_fields += 1
        
        self.data_quality_score = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        data = asdict(self)
        # Convert datetime to string for JSON serialization
        if data['scraped_at']:
            data['scraped_at'] = data['scraped_at'].isoformat()
        return data
    
    def to_csv_row(self) -> Dict[str, Any]:
        """Convert to CSV-friendly format"""
        data = self.to_dict()
        # Flatten complex fields for CSV
        return {k: str(v) if v is not None else '' for k, v in data.items()}
    
    def is_valid(self) -> bool:
        """Check if property has minimum required data"""
        return bool(self.title and (self.price or self.price_numeric))
    
    def get_database_schema(self) -> str:
        """Return SQL schema for database table creation"""
        return """
        CREATE TABLE IF NOT EXISTS properties (
            id SERIAL PRIMARY KEY,
            property_id VARCHAR(100) UNIQUE,
            property_url TEXT,
            title TEXT NOT NULL,
            property_type VARCHAR(50),
            transaction_type VARCHAR(50),
            price VARCHAR(50),
            price_numeric DECIMAL(15,2),
            price_per_sqft VARCHAR(50),
            price_per_sqft_numeric DECIMAL(10,2),
            super_area VARCHAR(50),
            super_area_numeric DECIMAL(10,2),
            carpet_area VARCHAR(50),
            carpet_area_numeric DECIMAL(10,2),
            area_unit VARCHAR(10),
            bedrooms INTEGER,
            bathrooms INTEGER,
            balconies INTEGER,
            floor VARCHAR(50),
            total_floors INTEGER,
            current_floor INTEGER,
            furnishing VARCHAR(50),
            status VARCHAR(100),
            possession_date VARCHAR(50),
            age VARCHAR(50),
            facing VARCHAR(50),
            overlooking TEXT,
            ownership VARCHAR(50),
            parking TEXT,
            parking_covered INTEGER,
            parking_open INTEGER,
            locality VARCHAR(100),
            society VARCHAR(100),
            builder VARCHAR(100),
            sector VARCHAR(50),
            city VARCHAR(50),
            state VARCHAR(50),
            owner_type VARCHAR(50),
            owner_name VARCHAR(100),
            contact_number VARCHAR(20),
            image_url TEXT,
            image_count INTEGER,
            description TEXT,
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            scraped_at TIMESTAMP,
            page_number INTEGER,
            position_on_page INTEGER,
            data_quality_score DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_properties_locality ON properties(locality);
        CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price_numeric);
        CREATE INDEX IF NOT EXISTS idx_properties_bedrooms ON properties(bedrooms);
        CREATE INDEX IF NOT EXISTS idx_properties_scraped_at ON properties(scraped_at);
        """


# Export list for easy imports
__all__ = ['PropertyModel']
