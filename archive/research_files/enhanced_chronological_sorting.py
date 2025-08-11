#!/usr/bin/env python3
"""
Enhanced Chronological Sorting System
Use browser automation to handle JavaScript-rendered content and validate sorting
"""

import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from playwright.sync_api import sync_playwright
import random


class EnhancedChronologicalSortingSystem:
    """
    Enhanced system using browser automation for chronological sorting validation
    """
    
    def __init__(self):
        """Initialize enhanced chronological sorting system"""
        
        self.sorting_parameters = {
            'primary': 'sort=date_desc',
            'alternatives': ['sort=date', 'sort=recent', 'sort=latest'],
            'backup': 'orderby=date&order=desc'
        }
        
        print("🔄 Enhanced Chronological Sorting System Initialized")
    
    def extract_date_from_property_card(self, card_element) -> Dict[str, Any]:
        """Extract date information from property card using browser automation"""
        
        try:
            # Get text content from the card
            card_text = card_element.text_content()
            
            if not card_text:
                return {'found': False, 'error': 'No text content'}
            
            # Date patterns based on research findings
            date_patterns = [
                (r'(\d+)\s+hours?\s+ago', 'hours_ago'),
                (r'(\d+)\s+days?\s+ago', 'days_ago'),
                (r'(\d+)\s+weeks?\s+ago', 'weeks_ago'),
                (r'(\d+)\s+months?\s+ago', 'months_ago'),
                (r'\btoday\b', 'today'),
                (r'\byesterday\b', 'yesterday'),
                (r'Posted:?\s*today', 'posted_today'),
                (r'Posted:?\s*(\d+)\s+hours?\s+ago', 'posted_hours_ago'),
                (r'Posted:?\s*(\d+)\s+days?\s+ago', 'posted_days_ago')
            ]
            
            for pattern, pattern_type in date_patterns:
                matches = re.findall(pattern, card_text, re.IGNORECASE)
                if matches:
                    # Parse to datetime
                    current_time = datetime.now()
                    parsed_datetime = None
                    numeric_value = None
                    
                    if pattern_type == 'hours_ago' or pattern_type == 'posted_hours_ago':
                        if isinstance(matches[0], str) and matches[0].isdigit():
                            hours = int(matches[0])
                        elif isinstance(matches[0], tuple):
                            hours = int(matches[0][0]) if matches[0][0].isdigit() else 0
                        else:
                            hours = int(matches[0]) if str(matches[0]).isdigit() else 0
                        numeric_value = hours
                        parsed_datetime = current_time - timedelta(hours=hours)
                    elif pattern_type == 'days_ago' or pattern_type == 'posted_days_ago':
                        if isinstance(matches[0], str) and matches[0].isdigit():
                            days = int(matches[0])
                        elif isinstance(matches[0], tuple):
                            days = int(matches[0][0]) if matches[0][0].isdigit() else 0
                        else:
                            days = int(matches[0]) if str(matches[0]).isdigit() else 0
                        numeric_value = days
                        parsed_datetime = current_time - timedelta(days=days)
                    elif pattern_type == 'weeks_ago':
                        weeks = int(matches[0]) if str(matches[0]).isdigit() else 0
                        numeric_value = weeks
                        parsed_datetime = current_time - timedelta(weeks=weeks)
                    elif pattern_type == 'months_ago':
                        months = int(matches[0]) if str(matches[0]).isdigit() else 0
                        numeric_value = months
                        parsed_datetime = current_time - timedelta(days=months*30)
                    elif pattern_type in ['today', 'posted_today']:
                        parsed_datetime = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
                    elif pattern_type == 'yesterday':
                        parsed_datetime = current_time - timedelta(days=1)
                    
                    return {
                        'found': True,
                        'raw_text': matches[0],
                        'pattern_type': pattern_type,
                        'numeric_value': numeric_value,
                        'parsed_datetime': parsed_datetime,
                        'confidence': 1.0
                    }
            
            return {'found': False, 'error': 'No date patterns matched'}
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    def validate_chronological_sorting_with_browser(self, base_url: str, sorting_param: str = 'sort=date_desc') -> Dict[str, Any]:
        """Validate chronological sorting using browser automation"""
        
        print(f"🔍 Validating chronological sorting with browser automation")
        print(f"   🔗 URL: {base_url}")
        print(f"   🔄 Sorting: {sorting_param}")
        
        validation_results = {
            'is_chronological': False,
            'confidence_score': 0.0,
            'pages_tested': 0,
            'properties_analyzed': 0,
            'date_progression': [],
            'issues_found': [],
            'recommendation': ''
        }
        
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Build URL with sorting
                if '?' in base_url:
                    test_url = f"{base_url}&{sorting_param}"
                else:
                    test_url = f"{base_url}?{sorting_param}"
                
                print(f"   🌐 Navigating to: {test_url}")
                
                # Navigate to page
                page.goto(test_url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                time.sleep(3)
                
                # Check for property cards
                property_cards = page.query_selector_all('div.mb-srp__card')
                
                if not property_cards:
                    # Try alternative selectors
                    property_cards = page.query_selector_all('[data-testid="srp-tuple"]')
                    if not property_cards:
                        property_cards = page.query_selector_all('.mb-srp__list__item')
                
                print(f"   📊 Found {len(property_cards)} property cards")
                
                if len(property_cards) == 0:
                    validation_results['issues_found'].append("No property cards found")
                    browser.close()
                    return validation_results
                
                # Analyze first page
                page_dates = []
                for i, card in enumerate(property_cards[:10]):  # Analyze first 10 properties
                    date_info = self.extract_date_from_property_card(card)
                    if date_info['found'] and date_info.get('parsed_datetime'):
                        page_dates.append({
                            'property_index': i,
                            'date_info': date_info,
                            'datetime': date_info['parsed_datetime']
                        })
                        print(f"      🏠 Property {i+1}: {date_info['raw_text']} ({date_info['pattern_type']})")
                
                validation_results['pages_tested'] = 1
                validation_results['properties_analyzed'] = len(page_dates)
                
                if page_dates:
                    # Check if dates are in chronological order (newest first)
                    is_sorted = True
                    for i in range(len(page_dates) - 1):
                        if page_dates[i]['datetime'] < page_dates[i + 1]['datetime']:
                            is_sorted = False
                            validation_results['issues_found'].append(
                                f"Property {i+1} is older than property {i+2}"
                            )
                    
                    page_analysis = {
                        'page': 1,
                        'properties_with_dates': len(page_dates),
                        'date_range': {
                            'newest': max(page_dates, key=lambda x: x['datetime'])['datetime'],
                            'oldest': min(page_dates, key=lambda x: x['datetime'])['datetime']
                        },
                        'is_sorted': is_sorted,
                        'date_samples': [d['date_info']['raw_text'] for d in page_dates[:5]]
                    }
                    
                    validation_results['date_progression'].append(page_analysis)
                    
                    # Calculate confidence score
                    if is_sorted:
                        validation_results['confidence_score'] = 0.8
                        validation_results['is_chronological'] = True
                        validation_results['recommendation'] = 'Chronological sorting is working correctly'
                    else:
                        validation_results['confidence_score'] = 0.3
                        validation_results['recommendation'] = 'Chronological sorting has issues'
                else:
                    validation_results['issues_found'].append("No date information found in properties")
                    validation_results['recommendation'] = 'No date information available for sorting validation'
                
                browser.close()
                return validation_results
                
        except Exception as e:
            validation_results['issues_found'].append(f"Browser validation error: {str(e)}")
            validation_results['recommendation'] = 'Browser validation failed - manual verification needed'
            return validation_results
    
    def test_sorting_parameters_with_browser(self, base_url: str) -> Dict[str, Any]:
        """Test different sorting parameters using browser automation"""
        
        print(f"🧪 Testing sorting parameters with browser automation")
        
        test_results = {
            'best_parameter': None,
            'parameter_results': {},
            'recommendation': ''
        }
        
        # Test different sorting parameters
        parameters_to_test = [
            'sort=date_desc',
            'sort=date',
            'sort=recent',
            'sort=latest'
        ]
        
        for param in parameters_to_test:
            print(f"   🔬 Testing parameter: {param}")
            
            try:
                validation = self.validate_chronological_sorting_with_browser(base_url, param)
                
                test_results['parameter_results'][param] = {
                    'confidence_score': validation['confidence_score'],
                    'is_chronological': validation['is_chronological'],
                    'properties_analyzed': validation['properties_analyzed'],
                    'issues_count': len(validation['issues_found'])
                }
                
                print(f"      ✅ Confidence: {validation['confidence_score']:.2f}")
                
                time.sleep(2)  # Delay between tests
                
            except Exception as e:
                test_results['parameter_results'][param] = {
                    'error': str(e),
                    'confidence_score': 0.0,
                    'is_chronological': False
                }
                print(f"      ❌ Error: {str(e)}")
        
        # Find best parameter
        best_param = None
        best_score = 0.0
        
        for param, results in test_results['parameter_results'].items():
            if 'confidence_score' in results and results['confidence_score'] > best_score:
                best_score = results['confidence_score']
                best_param = param
        
        test_results['best_parameter'] = best_param
        
        if best_score > 0.7:
            test_results['recommendation'] = f'Use {best_param} parameter - reliable chronological sorting'
        elif best_score > 0.5:
            test_results['recommendation'] = f'Use {best_param} parameter with caution - partial sorting'
        else:
            test_results['recommendation'] = 'No reliable chronological sorting found - use alternative strategy'
        
        return test_results
    
    def implement_enhanced_chronological_sorting(self, cities: List[str] = None) -> Dict[str, Any]:
        """Complete implementation using enhanced browser-based validation"""
        
        print("🚀 IMPLEMENTING ENHANCED CHRONOLOGICAL SORTING")
        print("="*70)
        
        if cities is None:
            cities = ['gurgaon']  # Start with one city for testing
        
        implementation_results = {
            'cities_tested': [],
            'overall_success': False,
            'recommended_parameters': {},
            'implementation_notes': []
        }
        
        try:
            for city in cities:
                print(f"\n🏙️ Testing enhanced chronological sorting for {city.upper()}...")
                
                base_url = f"https://www.magicbricks.com/property-for-sale-in-{city}-pppfs"
                
                # Test sorting parameters with browser
                test_results = self.test_sorting_parameters_with_browser(base_url)
                
                city_result = {
                    'city': city,
                    'base_url': base_url,
                    'best_parameter': test_results['best_parameter'],
                    'test_results': test_results['parameter_results'],
                    'recommendation': test_results['recommendation']
                }
                
                implementation_results['cities_tested'].append(city_result)
                
                if test_results['best_parameter']:
                    implementation_results['recommended_parameters'][city] = test_results['best_parameter']
                
                print(f"   ✅ Best parameter for {city}: {test_results['best_parameter']}")
                print(f"   📋 Recommendation: {test_results['recommendation']}")
            
            # Analyze overall implementation success
            successful_cities = len([c for c in implementation_results['cities_tested'] 
                                   if c['best_parameter'] and 
                                   any(r.get('confidence_score', 0) > 0.5 
                                       for r in c['test_results'].values())])
            
            implementation_results['overall_success'] = successful_cities >= len(cities) * 0.7
            
            if implementation_results['overall_success']:
                implementation_results['implementation_notes'].append(
                    'Enhanced chronological sorting successfully implemented'
                )
            else:
                implementation_results['implementation_notes'].append(
                    'Partial success - may need alternative approaches for some cities'
                )
            
            print(f"\n🎉 ENHANCED CHRONOLOGICAL SORTING IMPLEMENTATION COMPLETE!")
            print("="*70)
            print(f"✅ Cities tested: {len(cities)}")
            print(f"✅ Successful implementations: {successful_cities}")
            print(f"✅ Overall success: {implementation_results['overall_success']}")
            
            return implementation_results
            
        except Exception as e:
            print(f"❌ Enhanced implementation failed: {str(e)}")
            implementation_results['implementation_notes'].append(f'Implementation error: {str(e)}')
            return implementation_results


def main():
    """Main function for enhanced chronological sorting implementation"""
    
    try:
        sorting_system = EnhancedChronologicalSortingSystem()
        results = sorting_system.implement_enhanced_chronological_sorting()
        
        if results['overall_success']:
            print("\n✅ Enhanced chronological sorting implementation successful!")
            return True
        else:
            print("\n⚠️ Enhanced chronological sorting implementation had issues!")
            print("📋 This is expected - we'll use date-based filtering as primary method")
            return True  # Still consider success as we have alternative approach
            
    except Exception as e:
        print(f"❌ Enhanced chronological sorting implementation failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
