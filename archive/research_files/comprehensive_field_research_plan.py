#!/usr/bin/env python3
"""
Comprehensive Field Extraction Research Plan
Deep research across multiple cities, property types, and edge cases to ensure 100% data extraction coverage.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode
from multi_city_system import MultiCitySystem


@dataclass
class FieldExtractionResult:
    """Result of field extraction analysis"""
    field_name: str
    extracted: bool
    value: Any
    extraction_method: str
    confidence: float
    edge_case_type: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PropertyAnalysis:
    """Complete analysis of a single property"""
    url: str
    city: str
    property_type: str
    price_range: str
    listing_type: str
    field_results: List[FieldExtractionResult]
    overall_extraction_rate: float
    critical_fields_missing: List[str]
    timestamp: str


class ComprehensiveFieldResearcher:
    """
    Comprehensive field extraction researcher
    """
    
    def __init__(self):
        """Initialize comprehensive field researcher"""
        
        self.research_results = []
        self.field_statistics = {}
        self.edge_cases_found = []
        self.output_directory = Path('./field_research_output')
        self.output_directory.mkdir(exist_ok=True)
        
        # Initialize systems
        self.city_system = MultiCitySystem()
        
        # Define research scope
        self.research_scope = {
            'cities': {
                'metro': ['MUM', 'DEL', 'BLR', 'CHE', 'KOL', 'HYD'],  # 6 metro cities
                'tier1': ['PUN', 'AHM', 'SUR', 'VAD'],  # 4 tier-1 cities  
                'tier2': ['IND', 'BHO', 'LKO', 'KAN']   # 4 tier-2 cities
            },
            'property_types': ['apartment', 'house', 'plot', 'commercial'],
            'price_ranges': ['budget', 'mid_range', 'luxury'],
            'listing_types': ['new', 'featured', 'premium', 'regular'],
            'sample_size_per_category': 5  # 5 properties per category
        }
        
        # Define critical fields to validate
        self.critical_fields = [
            'title', 'price', 'location', 'area', 'property_type',
            'bedrooms', 'bathrooms', 'furnishing', 'age', 'floor',
            'amenities', 'description', 'contact_info', 'images',
            'url', 'date_posted', 'status'
        ]
        
        print("🔬 COMPREHENSIVE FIELD EXTRACTION RESEARCH")
        print("="*60)
        print(f"📁 Output directory: {self.output_directory}")
        print(f"🎯 Research scope: {len(self.research_scope['cities']['metro']) + len(self.research_scope['cities']['tier1']) + len(self.research_scope['cities']['tier2'])} cities")
        print(f"📊 Target sample size: ~{self.calculate_total_sample_size()} properties")
    
    def calculate_total_sample_size(self) -> int:
        """Calculate total expected sample size"""
        total_cities = sum(len(cities) for cities in self.research_scope['cities'].values())
        total_combinations = (
            len(self.research_scope['property_types']) *
            len(self.research_scope['price_ranges']) *
            self.research_scope['sample_size_per_category']
        )
        return total_cities * total_combinations
    
    def research_city_field_extraction(self, city_code: str, max_properties: int = 20) -> List[PropertyAnalysis]:
        """Research field extraction for a specific city"""
        
        print(f"\n🏙️ RESEARCHING CITY: {city_code}")
        print("-" * 50)
        
        city_results = []
        
        try:
            # Initialize scraper for research
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
            
            print(f"🚀 Starting field research for {city_code}...")
            print(f"   📋 Target: {max_properties} properties for comprehensive analysis")
            
            # Scrape properties for analysis
            result = scraper.scrape_properties_with_incremental(
                city=city_code.lower(),
                mode=ScrapingMode.FULL,
                max_pages=3  # 3 pages should give us enough variety
            )
            
            if result['success'] and scraper.properties:
                properties = scraper.properties[:max_properties]  # Limit to max_properties
                
                print(f"   ✅ Analyzing {len(properties)} properties...")
                
                for i, property_data in enumerate(properties, 1):
                    print(f"   📊 Analyzing property {i}/{len(properties)}")
                    
                    # Analyze field extraction for this property
                    analysis = self.analyze_property_field_extraction(
                        property_data, city_code, i
                    )
                    
                    if analysis:
                        city_results.append(analysis)
                
                print(f"   ✅ Completed analysis for {len(city_results)} properties")
                
            else:
                print(f"   ❌ Failed to scrape properties for {city_code}")
            
            scraper.close()
            
        except Exception as e:
            print(f"   ❌ Error researching {city_code}: {str(e)}")
        
        return city_results
    
    def analyze_property_field_extraction(self, property_data: Dict, city_code: str, property_index: int) -> Optional[PropertyAnalysis]:
        """Analyze field extraction for a single property"""
        
        try:
            field_results = []
            
            # Analyze each critical field
            for field_name in self.critical_fields:
                result = self.analyze_field_extraction(property_data, field_name)
                field_results.append(result)
            
            # Calculate overall extraction rate
            extracted_fields = [r for r in field_results if r.extracted]
            extraction_rate = len(extracted_fields) / len(field_results) if field_results else 0
            
            # Identify missing critical fields
            missing_fields = [r.field_name for r in field_results if not r.extracted]
            
            # Classify property
            property_type = self.classify_property_type(property_data)
            price_range = self.classify_price_range(property_data)
            listing_type = self.classify_listing_type(property_data)
            
            analysis = PropertyAnalysis(
                url=property_data.get('url', f'property_{property_index}'),
                city=city_code,
                property_type=property_type,
                price_range=price_range,
                listing_type=listing_type,
                field_results=field_results,
                overall_extraction_rate=extraction_rate,
                critical_fields_missing=missing_fields,
                timestamp=datetime.now().isoformat()
            )
            
            return analysis
            
        except Exception as e:
            print(f"     ❌ Error analyzing property {property_index}: {str(e)}")
            return None
    
    def analyze_field_extraction(self, property_data: Dict, field_name: str) -> FieldExtractionResult:
        """Analyze extraction of a specific field"""
        
        value = property_data.get(field_name)
        extracted = value is not None and value != '' and value != 'N/A'
        
        # Determine extraction method and confidence
        extraction_method = 'direct_key'
        confidence = 1.0 if extracted else 0.0
        edge_case_type = None
        notes = None
        
        # Check for edge cases
        if extracted:
            if isinstance(value, str):
                if 'price on request' in value.lower():
                    edge_case_type = 'price_on_request'
                elif 'under construction' in value.lower():
                    edge_case_type = 'under_construction'
                elif len(value.strip()) == 0:
                    extracted = False
                    edge_case_type = 'empty_string'
                elif value.strip() in ['--', 'N/A', 'Not Available', 'TBD']:
                    extracted = False
                    edge_case_type = 'placeholder_value'
        
        return FieldExtractionResult(
            field_name=field_name,
            extracted=extracted,
            value=value,
            extraction_method=extraction_method,
            confidence=confidence,
            edge_case_type=edge_case_type,
            notes=notes
        )
    
    def classify_property_type(self, property_data: Dict) -> str:
        """Classify property type"""
        prop_type = property_data.get('property_type', '').lower()
        
        if 'apartment' in prop_type or 'flat' in prop_type:
            return 'apartment'
        elif 'house' in prop_type or 'villa' in prop_type:
            return 'house'
        elif 'plot' in prop_type or 'land' in prop_type:
            return 'plot'
        elif 'commercial' in prop_type or 'office' in prop_type:
            return 'commercial'
        else:
            return 'unknown'
    
    def classify_price_range(self, property_data: Dict) -> str:
        """Classify price range"""
        price_str = str(property_data.get('price', '')).lower()
        
        # Extract numeric value (simplified)
        if 'crore' in price_str:
            if any(x in price_str for x in ['1 crore', '2 crore', '3 crore']):
                return 'luxury'
            else:
                return 'mid_range'
        elif 'lakh' in price_str:
            return 'budget'
        else:
            return 'unknown'
    
    def classify_listing_type(self, property_data: Dict) -> str:
        """Classify listing type"""
        # This would need to be enhanced based on actual data structure
        return 'regular'  # Default for now
    
    def run_comprehensive_field_research(self) -> Dict[str, Any]:
        """Run comprehensive field research across all cities"""
        
        print("🔬 STARTING COMPREHENSIVE FIELD RESEARCH")
        print("="*60)
        
        all_results = []
        
        # Research each city category
        for category, cities in self.research_scope['cities'].items():
            print(f"\n📊 RESEARCHING {category.upper()} CITIES")
            print("="*40)
            
            for city_code in cities:
                city_results = self.research_city_field_extraction(city_code, max_properties=15)
                all_results.extend(city_results)
                
                # Brief pause between cities
                time.sleep(2)
        
        # Analyze results
        analysis = self.analyze_research_results(all_results)
        
        # Save results
        self.save_research_results(all_results, analysis)
        
        return analysis
    
    def analyze_research_results(self, results: List[PropertyAnalysis]) -> Dict[str, Any]:
        """Analyze comprehensive research results"""
        
        print("\n📊 ANALYZING RESEARCH RESULTS")
        print("="*40)
        
        if not results:
            return {'error': 'No results to analyze'}
        
        # Field-by-field analysis
        field_stats = {}
        for field_name in self.critical_fields:
            field_extractions = []
            for result in results:
                field_result = next((fr for fr in result.field_results if fr.field_name == field_name), None)
                if field_result:
                    field_extractions.append(field_result.extracted)
            
            if field_extractions:
                success_rate = sum(field_extractions) / len(field_extractions)
                field_stats[field_name] = {
                    'success_rate': success_rate,
                    'total_samples': len(field_extractions),
                    'successful_extractions': sum(field_extractions)
                }
        
        # Overall statistics
        overall_rates = [r.overall_extraction_rate for r in results]
        overall_avg = sum(overall_rates) / len(overall_rates) if overall_rates else 0
        
        # City-wise analysis
        city_stats = {}
        for result in results:
            if result.city not in city_stats:
                city_stats[result.city] = []
            city_stats[result.city].append(result.overall_extraction_rate)
        
        for city, rates in city_stats.items():
            city_stats[city] = {
                'average_extraction_rate': sum(rates) / len(rates),
                'properties_analyzed': len(rates)
            }
        
        analysis = {
            'total_properties_analyzed': len(results),
            'overall_average_extraction_rate': overall_avg,
            'field_statistics': field_stats,
            'city_statistics': city_stats,
            'research_timestamp': datetime.now().isoformat(),
            'research_scope': self.research_scope
        }
        
        print(f"✅ Analysis complete:")
        print(f"   📊 Properties analyzed: {len(results)}")
        print(f"   📈 Overall extraction rate: {overall_avg:.1%}")
        print(f"   🏙️ Cities covered: {len(city_stats)}")
        
        return analysis
    
    def save_research_results(self, results: List[PropertyAnalysis], analysis: Dict[str, Any]):
        """Save research results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = self.output_directory / f"field_research_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        
        # Save analysis summary
        analysis_file = self.output_directory / f"field_research_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Results saved:")
        print(f"   📄 Detailed results: {results_file}")
        print(f"   📊 Analysis summary: {analysis_file}")


def main():
    """Run comprehensive field research"""
    
    try:
        print("🔬 MAGICBRICKS SCRAPER - COMPREHENSIVE FIELD RESEARCH")
        print("="*60)
        
        # Initialize researcher
        researcher = ComprehensiveFieldResearcher()
        
        # Run comprehensive research
        analysis = researcher.run_comprehensive_field_research()
        
        # Final assessment
        if analysis.get('overall_average_extraction_rate', 0) >= 0.95:
            print("\n🎉 FIELD EXTRACTION IS PRODUCTION READY!")
            print("✅ 95%+ extraction rate achieved across all scenarios")
        else:
            print("\n⚠️ FIELD EXTRACTION NEEDS IMPROVEMENT")
            print(f"❌ Current rate: {analysis.get('overall_average_extraction_rate', 0):.1%}")
            print("🔧 Gaps identified - enhancement needed")
        
        return analysis.get('overall_average_extraction_rate', 0) >= 0.95
        
    except Exception as e:
        print(f"❌ Comprehensive field research failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
