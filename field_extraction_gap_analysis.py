#!/usr/bin/env python3
"""
Field Extraction Gap Analysis and Enhancement Plan
Based on comprehensive field research findings
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class FieldExtractionGapAnalyzer:
    """Analyze field extraction gaps and create enhancement plan"""
    
    def __init__(self):
        """Initialize gap analyzer"""
        
        self.research_file = Path('./field_research_output/focused_field_analysis_20250810_155137.json')
        self.output_directory = Path('./field_research_output')
        
        # Load research results
        with open(self.research_file, 'r') as f:
            self.research_data = json.load(f)
        
        print("🔍 FIELD EXTRACTION GAP ANALYSIS")
        print("="*50)
        print(f"📊 Overall extraction rate: {self.research_data['overall_extraction_rate']:.1%}")
        print(f"🏙️ Cities analyzed: {self.research_data['cities_analyzed']}")
        print(f"📋 Properties analyzed: {self.research_data['total_properties']}")
    
    def analyze_critical_gaps(self) -> Dict[str, Any]:
        """Analyze critical gaps in field extraction"""
        
        print("\n🚨 CRITICAL GAP ANALYSIS")
        print("="*30)
        
        field_analysis = self.research_data['field_analysis']
        city_performance = self.research_data['city_performance']
        
        # Identify critical issues
        critical_gaps = {
            'completely_broken_fields': [],
            'poor_performing_fields': [],
            'city_specific_issues': [],
            'enhancement_priorities': []
        }
        
        # 1. Completely broken fields (0% extraction)
        for field, stats in field_analysis.items():
            if stats['average_rate'] == 0.0:
                critical_gaps['completely_broken_fields'].append({
                    'field': field,
                    'rate': stats['average_rate'],
                    'issue': 'Complete extraction failure across all cities'
                })
                print(f"🚨 CRITICAL: {field} - 0% extraction rate")
        
        # 2. Poor performing fields (<90% extraction)
        for field, stats in field_analysis.items():
            if 0.0 < stats['average_rate'] < 0.9:
                critical_gaps['poor_performing_fields'].append({
                    'field': field,
                    'rate': stats['average_rate'],
                    'min_rate': stats['min_rate'],
                    'max_rate': stats['max_rate'],
                    'issue': f'Inconsistent extraction: {stats["min_rate"]:.1%} to {stats["max_rate"]:.1%}'
                })
                print(f"⚠️ POOR: {field} - {stats['average_rate']:.1%} average rate")
        
        # 3. City-specific issues
        for city, performance in city_performance.items():
            if performance['extraction_rate'] < 0.6:
                critical_gaps['city_specific_issues'].append({
                    'city': city,
                    'rate': performance['extraction_rate'],
                    'issue': 'Major extraction failure - likely using fallback selectors'
                })
                print(f"🏙️ CITY ISSUE: {city} - {performance['extraction_rate']:.1%} extraction rate")
        
        # 4. Enhancement priorities
        priorities = [
            {
                'priority': 1,
                'issue': 'Date extraction completely broken',
                'fields': ['posting_date_text', 'parsed_posting_date'],
                'impact': 'HIGH - Critical for incremental scraping',
                'effort': 'MEDIUM - Need to implement date parsing logic'
            },
            {
                'priority': 2,
                'issue': 'Delhi city extraction failure',
                'fields': ['title', 'price', 'area'],
                'impact': 'HIGH - Major city not working',
                'effort': 'MEDIUM - Fix selector issues'
            },
            {
                'priority': 3,
                'issue': 'Overall extraction rate below target',
                'fields': ['all'],
                'impact': 'MEDIUM - Need 95%+ for production',
                'effort': 'HIGH - Comprehensive enhancement'
            }
        ]
        
        critical_gaps['enhancement_priorities'] = priorities
        
        return critical_gaps
    
    def create_enhancement_plan(self, gaps: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed enhancement plan"""
        
        print("\n🔧 ENHANCEMENT PLAN")
        print("="*25)
        
        enhancement_plan = {
            'immediate_fixes': [],
            'medium_term_improvements': [],
            'long_term_enhancements': [],
            'implementation_order': []
        }
        
        # Immediate fixes (Priority 1)
        immediate_fixes = [
            {
                'task': 'Fix Date Extraction',
                'description': 'Implement posting date extraction and parsing logic',
                'files_to_modify': [
                    'integrated_magicbricks_scraper.py',
                    'date_parsing_system.py'
                ],
                'specific_actions': [
                    'Add date extraction selectors to extract_property_data method',
                    'Implement date parsing in date_parsing_system',
                    'Add date fields to property data structure',
                    'Test date extraction across all cities'
                ],
                'expected_improvement': '+22.2% overall extraction rate',
                'effort_estimate': '2-3 hours'
            }
        ]
        
        # Medium term improvements (Priority 2)
        medium_term = [
            {
                'task': 'Fix Delhi City Extraction',
                'description': 'Resolve selector issues causing Delhi to use fallback selectors',
                'files_to_modify': [
                    'integrated_magicbricks_scraper.py'
                ],
                'specific_actions': [
                    'Debug why Delhi uses fallback selectors',
                    'Update selectors for Delhi-specific page structure',
                    'Test core field extraction (title, price, area)',
                    'Validate against multiple Delhi properties'
                ],
                'expected_improvement': '+8.9% overall extraction rate',
                'effort_estimate': '3-4 hours'
            },
            {
                'task': 'Enhance Selector Robustness',
                'description': 'Improve selector fallback logic and add more robust selectors',
                'files_to_modify': [
                    'integrated_magicbricks_scraper.py'
                ],
                'specific_actions': [
                    'Add more fallback selectors for title, price, area',
                    'Implement smart selector detection',
                    'Add city-specific selector variations',
                    'Test across all cities'
                ],
                'expected_improvement': '+5-10% overall extraction rate',
                'effort_estimate': '4-5 hours'
            }
        ]
        
        # Long term enhancements (Priority 3)
        long_term = [
            {
                'task': 'Comprehensive Field Expansion',
                'description': 'Add extraction for additional property fields',
                'files_to_modify': [
                    'integrated_magicbricks_scraper.py'
                ],
                'specific_actions': [
                    'Add bedrooms, bathrooms, furnishing extraction',
                    'Add amenities and description extraction',
                    'Add contact information extraction',
                    'Add image URL extraction'
                ],
                'expected_improvement': 'Comprehensive property data',
                'effort_estimate': '8-10 hours'
            }
        ]
        
        enhancement_plan['immediate_fixes'] = immediate_fixes
        enhancement_plan['medium_term_improvements'] = medium_term
        enhancement_plan['long_term_enhancements'] = long_term
        
        # Implementation order
        implementation_order = [
            'Fix Date Extraction (IMMEDIATE)',
            'Fix Delhi City Extraction (MEDIUM)',
            'Enhance Selector Robustness (MEDIUM)',
            'Comprehensive Field Expansion (LONG-TERM)'
        ]
        
        enhancement_plan['implementation_order'] = implementation_order
        
        print("📋 IMPLEMENTATION ORDER:")
        for i, task in enumerate(implementation_order, 1):
            print(f"   {i}. {task}")
        
        return enhancement_plan
    
    def estimate_final_performance(self, enhancement_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate performance after enhancements"""
        
        print("\n📈 PERFORMANCE PROJECTIONS")
        print("="*30)
        
        current_rate = self.research_data['overall_extraction_rate']
        
        projections = {
            'current_rate': current_rate,
            'after_immediate_fixes': current_rate + 0.222,  # +22.2% from date extraction
            'after_medium_term': current_rate + 0.222 + 0.089,  # +8.9% from Delhi fix
            'after_all_enhancements': current_rate + 0.222 + 0.089 + 0.075,  # +7.5% from robustness
            'target_rate': 0.95
        }
        
        print(f"📊 Current rate: {projections['current_rate']:.1%}")
        print(f"📊 After immediate fixes: {projections['after_immediate_fixes']:.1%}")
        print(f"📊 After medium-term: {projections['after_medium_term']:.1%}")
        print(f"📊 After all enhancements: {projections['after_all_enhancements']:.1%}")
        print(f"🎯 Target rate: {projections['target_rate']:.1%}")
        
        if projections['after_all_enhancements'] >= projections['target_rate']:
            print("✅ PROJECTED TO MEET 95% TARGET!")
        else:
            gap = projections['target_rate'] - projections['after_all_enhancements']
            print(f"⚠️ Still {gap:.1%} short of target - additional work needed")
        
        return projections
    
    def save_gap_analysis(self, gaps: Dict[str, Any], plan: Dict[str, Any], projections: Dict[str, Any]):
        """Save gap analysis results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        analysis_report = {
            'research_summary': {
                'overall_extraction_rate': self.research_data['overall_extraction_rate'],
                'cities_analyzed': self.research_data['cities_analyzed'],
                'total_properties': self.research_data['total_properties']
            },
            'critical_gaps': gaps,
            'enhancement_plan': plan,
            'performance_projections': projections,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Save gap analysis
        analysis_file = self.output_directory / f"gap_analysis_report_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\n💾 Gap analysis saved: {analysis_file}")
        
        return analysis_report
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete gap analysis"""
        
        # Analyze gaps
        gaps = self.analyze_critical_gaps()
        
        # Create enhancement plan
        plan = self.create_enhancement_plan(gaps)
        
        # Estimate performance
        projections = self.estimate_final_performance(plan)
        
        # Save results
        report = self.save_gap_analysis(gaps, plan, projections)
        
        return report


def main():
    """Run gap analysis"""
    
    try:
        print("🔍 MAGICBRICKS SCRAPER - FIELD EXTRACTION GAP ANALYSIS")
        print("="*60)
        
        # Initialize analyzer
        analyzer = FieldExtractionGapAnalyzer()
        
        # Run analysis
        report = analyzer.run_complete_analysis()
        
        # Final summary
        print(f"\n🎯 ANALYSIS COMPLETE")
        print("="*25)
        print("✅ Critical gaps identified")
        print("✅ Enhancement plan created")
        print("✅ Performance projections calculated")
        print("✅ Implementation roadmap defined")
        
        return True
        
    except Exception as e:
        print(f"❌ Gap analysis failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
