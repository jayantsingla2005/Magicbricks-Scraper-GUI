#!/usr/bin/env python3
"""
Property Quality Scorer
Calculates data quality scores based on field completeness and content richness.
"""

from typing import Dict, Any


class PropertyQualityScorer:
    """
    Calculates data quality scores for scraped property data
    """
    
    def __init__(self):
        """Initialize quality scorer with field weights"""
        
        # Define important fields and their weights
        self.field_weights = {
            'title': 0.15,
            'price': 0.20,
            'area': 0.15,
            'locality': 0.10,
            'property_type': 0.10,
            'bhk': 0.05,
            'amenities': 0.10,
            'description': 0.05,
            'images': 0.05,
            'contact_info': 0.05
        }
    
    def calculate_quality_score(self, property_data: Dict[str, Any]) -> float:
        """
        Calculate data quality score based on completeness and validity
        
        Args:
            property_data: Dictionary containing property information
        
        Returns:
            Quality score between 0.0 and 1.0
        """
        
        total_score = 0.0
        
        for field, weight in self.field_weights.items():
            value = property_data.get(field)
            
            if value and value != 'N/A' and str(value).strip():
                # Field has value
                field_score = weight
                
                # Bonus for rich content
                if field == 'description' and len(str(value)) > 100:
                    field_score *= 1.2
                elif field == 'amenities' and isinstance(value, list) and len(value) > 3:
                    field_score *= 1.2
                elif field == 'images' and isinstance(value, list) and len(value) > 2:
                    field_score *= 1.2
                
                total_score += field_score
        
        # Normalize to 0-1 range
        return min(total_score, 1.0)
    
    def get_field_weights(self) -> Dict[str, float]:
        """Get current field weights"""
        return self.field_weights.copy()
    
    def update_field_weights(self, new_weights: Dict[str, float]):
        """Update field weights for quality calculation"""
        self.field_weights.update(new_weights)

