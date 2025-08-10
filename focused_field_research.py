#!/usr/bin/env python3
"""
Focused Field Extraction Research
Streamlined approach to validate field extraction across key scenarios
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


class FocusedFieldResearcher:
    """Focused field extraction researcher"""
    
    def __init__(self):
        """Initialize focused field researcher"""
        
        self.output_directory = Path('./field_research_output')
        self.output_directory.mkdir(exist_ok=True)
        
        # Define critical fields to validate
        self.critical_fields = [
            'title', 'price', 'area', 'property_url', 'page_number', 
            'property_index', 'scraped_at', 'posting_date_text', 'parsed_posting_date'
        ]
        
        # Research scope - focused on key cities
        self.research_cities = ['mumbai', 'delhi', 'bangalore', 'pune', 'chennai']
        
        print("🔬 FOCUSED FIELD EXTRACTION RESEARCH")
        print("="*50)
        print(f"📁 Output directory: {self.output_directory}")
        print(f"🎯 Cities: {len(self.research_cities)}")
        print(f"📊 Critical fields: {len(self.critical_fields)}")
    
    def research_city_extraction(self, city: str) -> Dict[str, Any]:
        """Research field extraction for a specific city"""
        
        print(f"\n🏙️ RESEARCHING: {city.upper()}")
        print("-" * 30)
        
        try:
            # Initialize scraper
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
            
            print(f"🚀 Scraping {city} for field analysis...")
            
            # Scrape properties
            result = scraper.scrape_properties_with_incremental(
                city=city,
                mode=ScrapingMode.FULL,
                max_pages=2  # 2 pages for focused analysis
            )
            
            analysis = {
                'city': city,
                'success': result['success'],
                'properties_found': 0,
                'properties_analyzed': 0,
                'field_extraction_rates': {},
                'missing_fields': [],
                'edge_cases': [],
                'overall_extraction_rate': 0.0
            }
            
            if result['success'] and scraper.properties:
                properties = scraper.properties
                analysis['properties_found'] = len(properties)
                analysis['properties_analyzed'] = min(len(properties), 10)  # Analyze first 10
                
                print(f"   ✅ Found {len(properties)} properties")
                print(f"   📊 Analyzing {analysis['properties_analyzed']} properties...")
                
                # Analyze field extraction
                field_stats = {}
                for field in self.critical_fields:
                    field_stats[field] = {'extracted': 0, 'total': 0, 'rate': 0.0}
                
                for i, prop in enumerate(properties[:analysis['properties_analyzed']]):
                    for field in self.critical_fields:
                        field_stats[field]['total'] += 1
                        value = prop.get(field)
                        
                        # Check if field is properly extracted
                        if value is not None and value != '' and value != 'N/A':
                            field_stats[field]['extracted'] += 1
                        else:
                            # Track missing fields
                            if field not in analysis['missing_fields']:
                                analysis['missing_fields'].append(field)
                
                # Calculate extraction rates
                total_extractions = 0
                total_possible = 0
                
                for field, stats in field_stats.items():
                    if stats['total'] > 0:
                        stats['rate'] = stats['extracted'] / stats['total']
                        analysis['field_extraction_rates'][field] = stats['rate']
                        total_extractions += stats['extracted']
                        total_possible += stats['total']
                
                # Overall extraction rate
                if total_possible > 0:
                    analysis['overall_extraction_rate'] = total_extractions / total_possible
                
                print(f"   📈 Overall extraction rate: {analysis['overall_extraction_rate']:.1%}")
                
                # Report field-specific rates
                for field, rate in analysis['field_extraction_rates'].items():
                    status = "✅" if rate >= 0.9 else "⚠️" if rate >= 0.7 else "❌"
                    print(f"   {status} {field}: {rate:.1%}")
                
            else:
                print(f"   ❌ Failed to scrape {city}")
                analysis['success'] = False
            
            scraper.close()
            return analysis
            
        except Exception as e:
            print(f"   ❌ Error researching {city}: {str(e)}")
            return {
                'city': city,
                'success': False,
                'error': str(e),
                'properties_found': 0,
                'properties_analyzed': 0,
                'field_extraction_rates': {},
                'missing_fields': [],
                'edge_cases': [],
                'overall_extraction_rate': 0.0
            }
    
    def run_focused_research(self) -> Dict[str, Any]:
        """Run focused field research"""
        
        print("🔬 STARTING FOCUSED FIELD RESEARCH")
        print("="*50)
        
        all_results = []
        
        for city in self.research_cities:
            result = self.research_city_extraction(city)
            all_results.append(result)
            
            # Brief pause between cities
            time.sleep(1)
        
        # Analyze overall results
        analysis = self.analyze_results(all_results)
        
        # Save results
        self.save_results(all_results, analysis)
        
        return analysis
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze research results"""
        
        print("\n📊 ANALYZING RESULTS")
        print("="*30)
        
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            return {
                'error': 'No successful results to analyze',
                'overall_extraction_rate': 0.0,
                'cities_analyzed': 0,
                'total_properties': 0
            }
        
        # Overall statistics
        total_properties = sum(r['properties_analyzed'] for r in successful_results)
        overall_rates = [r['overall_extraction_rate'] for r in successful_results]
        overall_avg = sum(overall_rates) / len(overall_rates) if overall_rates else 0
        
        # Field-by-field analysis
        field_analysis = {}
        for field in self.critical_fields:
            field_rates = []
            for result in successful_results:
                if field in result['field_extraction_rates']:
                    field_rates.append(result['field_extraction_rates'][field])
            
            if field_rates:
                field_analysis[field] = {
                    'average_rate': sum(field_rates) / len(field_rates),
                    'min_rate': min(field_rates),
                    'max_rate': max(field_rates),
                    'cities_tested': len(field_rates)
                }
        
        # City-wise performance
        city_performance = {}
        for result in successful_results:
            city_performance[result['city']] = {
                'extraction_rate': result['overall_extraction_rate'],
                'properties_analyzed': result['properties_analyzed']
            }
        
        analysis = {
            'overall_extraction_rate': overall_avg,
            'cities_analyzed': len(successful_results),
            'total_properties': total_properties,
            'field_analysis': field_analysis,
            'city_performance': city_performance,
            'research_timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Analysis complete:")
        print(f"   📊 Overall extraction rate: {overall_avg:.1%}")
        print(f"   🏙️ Cities analyzed: {len(successful_results)}")
        print(f"   📋 Properties analyzed: {total_properties}")
        
        # Field performance summary
        print(f"\n📋 FIELD PERFORMANCE:")
        for field, stats in field_analysis.items():
            rate = stats['average_rate']
            status = "✅" if rate >= 0.9 else "⚠️" if rate >= 0.7 else "❌"
            print(f"   {status} {field}: {rate:.1%}")
        
        return analysis
    
    def save_results(self, results: List[Dict[str, Any]], analysis: Dict[str, Any]):
        """Save research results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = self.output_directory / f"focused_field_research_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save analysis
        analysis_file = self.output_directory / f"focused_field_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Results saved:")
        print(f"   📄 Results: {results_file}")
        print(f"   📊 Analysis: {analysis_file}")


def main():
    """Run focused field research"""
    
    try:
        print("🔬 MAGICBRICKS SCRAPER - FOCUSED FIELD RESEARCH")
        print("="*55)
        
        # Initialize researcher
        researcher = FocusedFieldResearcher()
        
        # Run research
        analysis = researcher.run_focused_research()
        
        # Final assessment
        extraction_rate = analysis.get('overall_extraction_rate', 0)
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        print("="*30)
        
        if extraction_rate >= 0.95:
            print("🎉 FIELD EXTRACTION IS PRODUCTION READY!")
            print(f"✅ {extraction_rate:.1%} extraction rate achieved")
            return True
        elif extraction_rate >= 0.85:
            print("⚠️ FIELD EXTRACTION NEEDS MINOR IMPROVEMENTS")
            print(f"📊 Current rate: {extraction_rate:.1%}")
            print("🔧 Some enhancements recommended")
            return False
        else:
            print("❌ FIELD EXTRACTION NEEDS MAJOR IMPROVEMENTS")
            print(f"📊 Current rate: {extraction_rate:.1%}")
            print("🔧 Significant gaps identified")
            return False
        
    except Exception as e:
        print(f"❌ Focused field research failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
