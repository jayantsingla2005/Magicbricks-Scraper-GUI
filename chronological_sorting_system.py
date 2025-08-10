#!/usr/bin/env python3
"""
Chronological Sorting System Implementation
Implement sort=date_desc URL parameter forcing and validate chronological ordering.
Based on comprehensive research findings.
"""

import requests
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin, urlparse, parse_qs, urlencode


class ChronologicalSortingSystem:
    """
    System to force chronological sorting and validate ordering works correctly
    """
    
    def __init__(self):
        """Initialize chronological sorting system"""
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Research-validated sorting parameters
        self.sorting_parameters = {
            'primary': 'sort=date_desc',
            'alternatives': ['sort=date', 'sort=recent', 'sort=latest'],
            'backup': 'orderby=date&order=desc'
        }
        
        print("🔄 Chronological Sorting System Initialized")
    
    def build_chronological_url(self, base_url: str, sorting_method: str = 'primary') -> str:
        """Build URL with chronological sorting parameters"""
        
        try:
            # Parse the base URL
            parsed_url = urlparse(base_url)
            query_params = parse_qs(parsed_url.query)
            
            # Add chronological sorting parameter
            if sorting_method == 'primary':
                sort_param = self.sorting_parameters['primary']
            elif sorting_method in self.sorting_parameters['alternatives']:
                sort_param = f"sort={sorting_method}"
            else:
                sort_param = self.sorting_parameters['backup']
            
            # Parse sort parameter
            if '=' in sort_param:
                key, value = sort_param.split('=', 1)
                query_params[key] = [value]
            
            # Rebuild URL with sorting
            new_query = urlencode(query_params, doseq=True)
            chronological_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
            
            print(f"🔗 Built chronological URL: {chronological_url}")
            return chronological_url
            
        except Exception as e:
            print(f"❌ Error building chronological URL: {str(e)}")
            return base_url
    
    def extract_date_information(self, property_element) -> Dict[str, Any]:
        """Extract date information from property element"""
        
        try:
            element_text = property_element.get_text()
            
            # Date patterns based on research findings
            date_patterns = [
                (r'(\d+)\s+hours?\s+ago', 'hours_ago'),
                (r'(\d+)\s+days?\s+ago', 'days_ago'),
                (r'(\d+)\s+weeks?\s+ago', 'weeks_ago'),
                (r'(\d+)\s+months?\s+ago', 'months_ago'),
                (r'(today)', 'today'),
                (r'(yesterday)', 'yesterday'),
                (r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'absolute_date')
            ]
            
            date_info = {
                'raw_text': None,
                'pattern_type': None,
                'numeric_value': None,
                'parsed_datetime': None,
                'confidence': 0.0
            }
            
            for pattern, pattern_type in date_patterns:
                matches = re.findall(pattern, element_text, re.IGNORECASE)
                if matches:
                    date_info['raw_text'] = matches[0]
                    date_info['pattern_type'] = pattern_type
                    date_info['confidence'] = 1.0
                    
                    # Parse to datetime
                    current_time = datetime.now()
                    
                    if pattern_type == 'hours_ago':
                        hours = int(matches[0])
                        date_info['numeric_value'] = hours
                        date_info['parsed_datetime'] = current_time - timedelta(hours=hours)
                    elif pattern_type == 'days_ago':
                        days = int(matches[0])
                        date_info['numeric_value'] = days
                        date_info['parsed_datetime'] = current_time - timedelta(days=days)
                    elif pattern_type == 'weeks_ago':
                        weeks = int(matches[0])
                        date_info['numeric_value'] = weeks
                        date_info['parsed_datetime'] = current_time - timedelta(weeks=weeks)
                    elif pattern_type == 'months_ago':
                        months = int(matches[0])
                        date_info['numeric_value'] = months
                        date_info['parsed_datetime'] = current_time - timedelta(days=months*30)
                    elif pattern_type == 'today':
                        date_info['parsed_datetime'] = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
                    elif pattern_type == 'yesterday':
                        date_info['parsed_datetime'] = current_time - timedelta(days=1)
                    
                    break
            
            return date_info
            
        except Exception as e:
            print(f"⚠️ Error extracting date information: {str(e)}")
            return {
                'raw_text': None,
                'pattern_type': None,
                'numeric_value': None,
                'parsed_datetime': None,
                'confidence': 0.0
            }
    
    def validate_chronological_ordering(self, url: str, pages_to_check: int = 3) -> Dict[str, Any]:
        """Validate that chronological sorting is working correctly"""
        
        print(f"🔍 Validating chronological ordering for: {url}")
        
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
            for page_num in range(1, pages_to_check + 1):
                print(f"   📊 Analyzing page {page_num}...")
                
                # Build page URL
                if page_num == 1:
                    page_url = url
                else:
                    separator = '&' if '?' in url else '?'
                    page_url = f"{url}{separator}page={page_num}"
                
                # Make request
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.get(page_url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    validation_results['issues_found'].append(f"Page {page_num}: HTTP {response.status_code}")
                    continue
                
                # Parse properties
                soup = BeautifulSoup(response.content, 'html.parser')
                property_cards = soup.find_all('div', class_='mb-srp__card')
                
                if not property_cards:
                    validation_results['issues_found'].append(f"Page {page_num}: No properties found")
                    continue
                
                # Extract dates from properties
                page_dates = []
                for i, card in enumerate(property_cards[:10]):  # Check first 10 properties
                    date_info = self.extract_date_information(card)
                    if date_info['parsed_datetime']:
                        page_dates.append({
                            'property_index': i,
                            'date_info': date_info,
                            'datetime': date_info['parsed_datetime']
                        })
                
                validation_results['pages_tested'] += 1
                validation_results['properties_analyzed'] += len(page_dates)
                
                # Analyze date progression on this page
                if page_dates:
                    page_analysis = {
                        'page': page_num,
                        'properties_with_dates': len(page_dates),
                        'date_range': {
                            'newest': max(page_dates, key=lambda x: x['datetime'])['datetime'],
                            'oldest': min(page_dates, key=lambda x: x['datetime'])['datetime']
                        },
                        'is_sorted': self._check_page_sorting(page_dates),
                        'date_samples': [d['date_info']['raw_text'] for d in page_dates[:5]]
                    }
                    
                    validation_results['date_progression'].append(page_analysis)
                
                time.sleep(2)  # Respectful delay
            
            # Analyze overall chronological ordering
            validation_results = self._analyze_overall_ordering(validation_results)
            
            return validation_results
            
        except Exception as e:
            validation_results['issues_found'].append(f"Validation error: {str(e)}")
            return validation_results
    
    def _check_page_sorting(self, page_dates: List[Dict]) -> bool:
        """Check if dates on a single page are sorted chronologically"""
        
        if len(page_dates) < 2:
            return True
        
        # Check if dates are in descending order (newest first)
        for i in range(len(page_dates) - 1):
            if page_dates[i]['datetime'] < page_dates[i + 1]['datetime']:
                return False
        
        return True
    
    def _analyze_overall_ordering(self, validation_results: Dict) -> Dict:
        """Analyze overall chronological ordering across pages"""
        
        try:
            if not validation_results['date_progression']:
                validation_results['recommendation'] = 'No date information found for analysis'
                return validation_results
            
            # Check if each page is internally sorted
            pages_sorted = sum(1 for page in validation_results['date_progression'] if page['is_sorted'])
            total_pages = len(validation_results['date_progression'])
            
            # Check if dates progress correctly across pages
            cross_page_progression = True
            for i in range(len(validation_results['date_progression']) - 1):
                current_page = validation_results['date_progression'][i]
                next_page = validation_results['date_progression'][i + 1]
                
                if (current_page['date_range']['oldest'] < 
                    next_page['date_range']['newest']):
                    cross_page_progression = False
                    validation_results['issues_found'].append(
                        f"Date overlap between page {current_page['page']} and {next_page['page']}"
                    )
            
            # Calculate confidence score
            page_sorting_score = pages_sorted / total_pages if total_pages > 0 else 0
            cross_page_score = 1.0 if cross_page_progression else 0.5
            
            validation_results['confidence_score'] = (page_sorting_score + cross_page_score) / 2
            validation_results['is_chronological'] = validation_results['confidence_score'] > 0.7
            
            # Generate recommendation
            if validation_results['is_chronological']:
                validation_results['recommendation'] = 'Chronological sorting is working correctly'
            elif validation_results['confidence_score'] > 0.5:
                validation_results['recommendation'] = 'Partial chronological sorting - usable with caution'
            else:
                validation_results['recommendation'] = 'Chronological sorting not reliable - use alternative approach'
            
            return validation_results
            
        except Exception as e:
            validation_results['issues_found'].append(f"Analysis error: {str(e)}")
            validation_results['recommendation'] = 'Analysis failed - manual verification needed'
            return validation_results
    
    def test_sorting_parameters(self, base_url: str) -> Dict[str, Any]:
        """Test different sorting parameters to find the most effective one"""
        
        print(f"🧪 Testing sorting parameters for: {base_url}")
        
        test_results = {
            'best_parameter': None,
            'parameter_results': {},
            'recommendation': ''
        }
        
        # Test primary and alternative parameters
        parameters_to_test = ['date_desc'] + self.sorting_parameters['alternatives']
        
        for param in parameters_to_test:
            print(f"   🔬 Testing parameter: {param}")
            
            try:
                # Build URL with this parameter
                if param == 'date_desc':
                    test_url = self.build_chronological_url(base_url, 'primary')
                else:
                    test_url = self.build_chronological_url(base_url, param)
                
                # Validate ordering
                validation = self.validate_chronological_ordering(test_url, pages_to_check=2)
                
                test_results['parameter_results'][param] = {
                    'confidence_score': validation['confidence_score'],
                    'is_chronological': validation['is_chronological'],
                    'properties_analyzed': validation['properties_analyzed'],
                    'issues_count': len(validation['issues_found'])
                }
                
                print(f"      ✅ Confidence: {validation['confidence_score']:.2f}")
                
                time.sleep(3)  # Delay between tests
                
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
    
    def implement_chronological_sorting(self, cities: List[str] = None) -> Dict[str, Any]:
        """Complete implementation and testing of chronological sorting"""
        
        print("🚀 IMPLEMENTING CHRONOLOGICAL SORTING SYSTEM")
        print("="*70)
        
        if cities is None:
            cities = ['gurgaon', 'mumbai', 'bangalore']
        
        implementation_results = {
            'cities_tested': [],
            'overall_success': False,
            'recommended_parameters': {},
            'implementation_notes': []
        }
        
        try:
            for city in cities:
                print(f"\n🏙️ Testing chronological sorting for {city.upper()}...")
                
                base_url = f"https://www.magicbricks.com/property-for-sale-in-{city}-pppfs"
                
                # Test sorting parameters
                test_results = self.test_sorting_parameters(base_url)
                
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
                                   any(r.get('confidence_score', 0) > 0.7 
                                       for r in c['test_results'].values())])
            
            implementation_results['overall_success'] = successful_cities >= len(cities) * 0.7
            
            if implementation_results['overall_success']:
                implementation_results['implementation_notes'].append(
                    'Chronological sorting successfully implemented across cities'
                )
            else:
                implementation_results['implementation_notes'].append(
                    'Partial success - some cities may need alternative approaches'
                )
            
            print(f"\n🎉 CHRONOLOGICAL SORTING IMPLEMENTATION COMPLETE!")
            print("="*70)
            print(f"✅ Cities tested: {len(cities)}")
            print(f"✅ Successful implementations: {successful_cities}")
            print(f"✅ Overall success: {implementation_results['overall_success']}")
            
            return implementation_results
            
        except Exception as e:
            print(f"❌ Implementation failed: {str(e)}")
            implementation_results['implementation_notes'].append(f'Implementation error: {str(e)}')
            return implementation_results


def main():
    """Main function for chronological sorting implementation"""
    
    try:
        sorting_system = ChronologicalSortingSystem()
        results = sorting_system.implement_chronological_sorting()
        
        if results['overall_success']:
            print("\n✅ Chronological sorting implementation successful!")
            return True
        else:
            print("\n⚠️ Chronological sorting implementation had issues!")
            return False
            
    except Exception as e:
        print(f"❌ Chronological sorting implementation failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
