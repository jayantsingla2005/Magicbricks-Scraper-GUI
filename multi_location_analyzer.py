#!/usr/bin/env python3
"""
Multi-Location Analysis Tool
Tests extraction across different cities and price ranges to identify regional variations
and ensure universal selector compatibility across all major Indian real estate markets.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import statistics

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class MultiLocationAnalyzer:
    """
    Comprehensive analyzer for multi-location and price range variations
    """
    
    def __init__(self):
        """Initialize multi-location analyzer"""
        
        # Target cities for analysis
        self.target_cities = {
            'gurgaon': {
                'url': 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs',
                'region': 'NCR',
                'tier': 'tier1',
                'expected_properties': 'high'
            },
            'mumbai': {
                'url': 'https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs',
                'region': 'West',
                'tier': 'tier1',
                'expected_properties': 'high'
            },
            'bangalore': {
                'url': 'https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs',
                'region': 'South',
                'tier': 'tier1',
                'expected_properties': 'high'
            },
            'delhi': {
                'url': 'https://www.magicbricks.com/property-for-sale-in-delhi-pppfs',
                'region': 'NCR',
                'tier': 'tier1',
                'expected_properties': 'high'
            },
            'pune': {
                'url': 'https://www.magicbricks.com/property-for-sale-in-pune-pppfs',
                'region': 'West',
                'tier': 'tier1',
                'expected_properties': 'medium'
            }
        }
        
        # Price range analysis (based on typical ranges in each city)
        self.price_ranges = {
            'budget': {'min': 0, 'max': 100, 'unit': 'lac'},  # <1 Cr
            'mid': {'min': 100, 'max': 300, 'unit': 'lac'},   # 1-3 Cr
            'premium': {'min': 300, 'max': 1000, 'unit': 'lac'}, # 3-10 Cr
            'luxury': {'min': 1000, 'max': 10000, 'unit': 'lac'} # >10 Cr
        }
        
        # Key fields to test across locations
        self.test_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'society', 'locality', 'status', 'property_type'
        ]
        
        # Current selectors (from previous analysis)
        self.selectors = {
            'property_card': '.mb-srp__card',
            'title': '.mb-srp__card--title a',
            'price': '.mb-srp__card__price--amount',
            'area': '.mb-srp__card__price--size',
            'super_area': '.mb-srp__card__summary--value',
            'bedrooms': '.mb-srp__card__summary--value',
            'bathrooms': '.mb-srp__card__summary--value',
            'society': '.mb-srp__card__society',
            'locality': '.mb-srp__card__ads--locality',
            'status': '.mb-srp__card__summary__list--item',
            'property_type': '.mb-srp__card__summary--value'
        }
        
        # Analysis results
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'cities_analyzed': 0,
            'total_properties_analyzed': 0,
            'city_performance': {},
            'regional_analysis': {},
            'price_range_analysis': {},
            'selector_consistency': {},
            'regional_variations': {},
            'recommendations': []
        }
        
        print("🌍 Multi-Location Analyzer Initialized")
        print(f"🎯 Target Cities: {', '.join(self.target_cities.keys())}")
        print(f"💰 Price Ranges: {', '.join(self.price_ranges.keys())}")
        print(f"📊 Test Fields: {len(self.test_fields)}")
    
    def analyze_multi_location_variations(self) -> Dict[str, Any]:
        """
        Perform comprehensive multi-location analysis
        """
        
        print("\n🚀 Starting Multi-Location Analysis")
        print("="*60)
        
        try:
            # Step 1: Analyze each city
            print("🌍 Step 1: Analyzing Individual Cities...")
            city_data = self._analyze_individual_cities()
            
            if not city_data:
                print("❌ No city data could be collected")
                return self.analysis_results
            
            # Step 2: Analyze regional patterns
            print("\n🗺️ Step 2: Analyzing Regional Patterns...")
            self._analyze_regional_patterns(city_data)
            
            # Step 3: Analyze price range variations
            print("\n💰 Step 3: Analyzing Price Range Variations...")
            self._analyze_price_range_variations(city_data)
            
            # Step 4: Test selector consistency
            print("\n🎯 Step 4: Testing Selector Consistency...")
            self._test_selector_consistency(city_data)
            
            # Step 5: Identify regional variations
            print("\n🔍 Step 5: Identifying Regional Variations...")
            self._identify_regional_variations()
            
            # Step 6: Generate recommendations
            print("\n💡 Step 6: Generating Recommendations...")
            self._generate_multi_location_recommendations()
            
            # Step 7: Save analysis results
            print("\n💾 Step 7: Saving Analysis Results...")
            self._save_analysis_results()
            
            print("\n✅ Multi-Location Analysis Complete!")
            self._print_analysis_summary()
            
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ Multi-location analysis failed: {str(e)}")
            self.analysis_results['error'] = str(e)
            return self.analysis_results
    
    def _analyze_individual_cities(self) -> Dict[str, Dict[str, Any]]:
        """Analyze each city individually"""
        
        city_data = {}
        
        for city, config in self.target_cities.items():
            print(f"🌍 Analyzing {city.upper()}...")
            
            try:
                city_analysis = self._analyze_single_city(city, config)
                
                if city_analysis:
                    city_data[city] = city_analysis
                    self.analysis_results['cities_analyzed'] += 1
                    
                    properties_count = city_analysis.get('properties_analyzed', 0)
                    self.analysis_results['total_properties_analyzed'] += properties_count
                    
                    print(f"✅ {city.upper()}: Analyzed {properties_count} properties")
                else:
                    print(f"⚠️ {city.upper()}: No data collected")
                
                # Delay between cities
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ {city.upper()}: Analysis failed - {str(e)}")
        
        return city_data
    
    def _analyze_single_city(self, city: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single city"""
        
        driver = self._setup_browser()
        
        try:
            # Navigate to city page
            driver.get(config['url'])
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find property cards
            property_cards = soup.select(self.selectors['property_card'])
            
            if not property_cards:
                return None
            
            # Analyze properties
            city_analysis = {
                'city': city,
                'config': config,
                'properties_analyzed': len(property_cards),
                'field_performance': {},
                'price_distribution': {},
                'property_type_distribution': {},
                'sample_data': []
            }
            
            # Test field extraction
            for field in self.test_fields:
                field_performance = self._test_field_in_city(property_cards, field)
                city_analysis['field_performance'][field] = field_performance
            
            # Analyze price distribution
            city_analysis['price_distribution'] = self._analyze_price_distribution(property_cards)
            
            # Analyze property type distribution
            city_analysis['property_type_distribution'] = self._analyze_property_type_distribution(property_cards)
            
            # Collect sample data
            city_analysis['sample_data'] = self._collect_sample_data(property_cards[:5])
            
            return city_analysis
            
        finally:
            driver.quit()
    
    def _test_field_in_city(self, cards: List[Tag], field: str) -> Dict[str, Any]:
        """Test field extraction in a specific city"""
        
        selector = self.selectors.get(field)
        if not selector:
            return {'success_rate': 0, 'successful': 0, 'total': len(cards)}
        
        successful = 0
        sample_values = []
        
        for card in cards:
            try:
                extracted_value = self._extract_field_value(card, field, selector)
                
                if extracted_value and extracted_value.strip():
                    successful += 1
                    
                    if len(sample_values) < 3:
                        sample_values.append(extracted_value.strip()[:50])
            
            except Exception:
                pass
        
        success_rate = (successful / len(cards)) * 100 if cards else 0
        
        return {
            'success_rate': success_rate,
            'successful': successful,
            'total': len(cards),
            'sample_values': sample_values
        }
    
    def _extract_field_value(self, card: Tag, field: str, selector: str) -> Optional[str]:
        """Extract field value using selector"""
        
        try:
            elements = card.select(selector)
            
            if not elements:
                return None
            
            element = elements[0]
            
            if field == 'property_url':
                return element.get('href')
            elif field in ['super_area', 'bedrooms', 'bathrooms', 'property_type']:
                # For summary fields, try to find specific content
                text = element.get_text(strip=True)
                
                if field == 'super_area' and ('sqft' in text.lower() or 'sq' in text.lower()):
                    return text
                elif field == 'bedrooms' and ('bhk' in text.lower() or 'bed' in text.lower()):
                    return text
                elif field == 'bathrooms' and ('bath' in text.lower() or 'toilet' in text.lower()):
                    return text
                elif field == 'property_type' and any(ptype in text.lower() for ptype in ['apartment', 'house', 'villa', 'floor', 'plot']):
                    return text
                else:
                    return text if text else None
            else:
                return element.get_text(strip=True)
        
        except Exception:
            return None
    
    def _analyze_price_distribution(self, cards: List[Tag]) -> Dict[str, Any]:
        """Analyze price distribution in the city"""
        
        price_data = []
        price_ranges = defaultdict(int)
        
        for card in cards:
            try:
                price_element = card.select(self.selectors['price'])
                if price_element:
                    price_text = price_element[0].get_text(strip=True)
                    
                    # Extract numeric value and unit
                    price_info = self._parse_price(price_text)
                    if price_info:
                        price_data.append(price_info)
                        
                        # Categorize into price ranges
                        price_category = self._categorize_price(price_info)
                        price_ranges[price_category] += 1
            
            except Exception:
                pass
        
        return {
            'total_properties_with_price': len(price_data),
            'price_range_distribution': dict(price_ranges),
            'sample_prices': price_data[:10]
        }
    
    def _parse_price(self, price_text: str) -> Optional[Dict[str, Any]]:
        """Parse price text to extract value and unit"""
        
        try:
            # Remove currency symbol and clean text
            clean_text = price_text.replace('₹', '').strip().lower()
            
            # Extract number and unit
            if 'cr' in clean_text or 'crore' in clean_text:
                numbers = re.findall(r'[\d.]+', clean_text)
                if numbers:
                    return {'value': float(numbers[0]), 'unit': 'crore', 'original': price_text}
            elif 'lac' in clean_text or 'lakh' in clean_text:
                numbers = re.findall(r'[\d.]+', clean_text)
                if numbers:
                    return {'value': float(numbers[0]), 'unit': 'lac', 'original': price_text}
            
            return None
        
        except Exception:
            return None
    
    def _categorize_price(self, price_info: Dict[str, Any]) -> str:
        """Categorize price into range"""
        
        value = price_info['value']
        unit = price_info['unit']
        
        # Convert to lac for comparison
        if unit == 'crore':
            value_in_lac = value * 100
        else:
            value_in_lac = value
        
        if value_in_lac < 100:
            return 'budget'
        elif value_in_lac < 300:
            return 'mid'
        elif value_in_lac < 1000:
            return 'premium'
        else:
            return 'luxury'
    
    def _analyze_property_type_distribution(self, cards: List[Tag]) -> Dict[str, int]:
        """Analyze property type distribution"""
        
        type_distribution = defaultdict(int)
        
        for card in cards:
            try:
                # Look for property type indicators in card text
                card_text = card.get_text().lower()
                
                if 'apartment' in card_text or 'flat' in card_text:
                    type_distribution['apartment'] += 1
                elif 'house' in card_text and 'independent' in card_text:
                    type_distribution['house'] += 1
                elif 'villa' in card_text:
                    type_distribution['villa'] += 1
                elif 'floor' in card_text and 'builder' in card_text:
                    type_distribution['floor'] += 1
                elif 'plot' in card_text or 'land' in card_text:
                    type_distribution['plot'] += 1
                else:
                    type_distribution['other'] += 1
            
            except Exception:
                type_distribution['unknown'] += 1
        
        return dict(type_distribution)
    
    def _collect_sample_data(self, cards: List[Tag]) -> List[Dict[str, Any]]:
        """Collect sample data from cards"""
        
        samples = []
        
        for i, card in enumerate(cards):
            sample = {'card_index': i}
            
            for field in self.test_fields:
                try:
                    selector = self.selectors.get(field)
                    if selector:
                        value = self._extract_field_value(card, field, selector)
                        sample[field] = value[:100] if value else None  # Limit to 100 chars
                except Exception:
                    sample[field] = None
            
            samples.append(sample)
        
        return samples
    
    def _analyze_regional_patterns(self, city_data: Dict[str, Dict[str, Any]]):
        """Analyze patterns by region"""
        
        print("🗺️ Analyzing regional patterns...")
        
        regional_data = defaultdict(list)
        
        # Group cities by region
        for city, data in city_data.items():
            region = self.target_cities[city]['region']
            regional_data[region].append((city, data))
        
        regional_analysis = {}
        
        for region, cities in regional_data.items():
            print(f"   📍 Analyzing {region} region...")
            
            # Calculate regional averages
            total_properties = sum(data['properties_analyzed'] for _, data in cities)
            
            # Field performance averages
            field_averages = {}
            for field in self.test_fields:
                field_rates = []
                for _, data in cities:
                    field_perf = data['field_performance'].get(field, {})
                    field_rates.append(field_perf.get('success_rate', 0))
                
                field_averages[field] = statistics.mean(field_rates) if field_rates else 0
            
            regional_analysis[region] = {
                'cities': [city for city, _ in cities],
                'total_properties': total_properties,
                'avg_field_performance': field_averages,
                'overall_avg_performance': statistics.mean(field_averages.values()) if field_averages else 0
            }
        
        self.analysis_results['regional_analysis'] = regional_analysis
    
    def _analyze_price_range_variations(self, city_data: Dict[str, Dict[str, Any]]):
        """Analyze variations across price ranges"""
        
        print("💰 Analyzing price range variations...")
        
        # Aggregate price range data across all cities
        combined_price_data = defaultdict(int)
        
        for city, data in city_data.items():
            price_dist = data.get('price_distribution', {}).get('price_range_distribution', {})
            for price_range, count in price_dist.items():
                combined_price_data[price_range] += count
        
        # Calculate percentages
        total_properties = sum(combined_price_data.values())
        price_percentages = {}
        
        for price_range, count in combined_price_data.items():
            percentage = (count / total_properties * 100) if total_properties > 0 else 0
            price_percentages[price_range] = {
                'count': count,
                'percentage': percentage
            }
        
        self.analysis_results['price_range_analysis'] = {
            'total_properties_with_price': total_properties,
            'range_distribution': price_percentages,
            'dominant_range': max(combined_price_data, key=combined_price_data.get) if combined_price_data else None
        }
    
    def _test_selector_consistency(self, city_data: Dict[str, Dict[str, Any]]):
        """Test selector consistency across cities"""
        
        print("🎯 Testing selector consistency across cities...")
        
        consistency_analysis = {}
        
        for field in self.test_fields:
            field_rates = []
            city_performances = {}
            
            for city, data in city_data.items():
                field_perf = data['field_performance'].get(field, {})
                success_rate = field_perf.get('success_rate', 0)
                field_rates.append(success_rate)
                city_performances[city] = success_rate
            
            if field_rates:
                consistency_analysis[field] = {
                    'average_success_rate': statistics.mean(field_rates),
                    'min_success_rate': min(field_rates),
                    'max_success_rate': max(field_rates),
                    'success_rate_range': max(field_rates) - min(field_rates),
                    'consistency_score': 100 - (max(field_rates) - min(field_rates)),  # Higher is more consistent
                    'city_performances': city_performances
                }
        
        self.analysis_results['selector_consistency'] = consistency_analysis
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for analysis"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def _identify_regional_variations(self):
        """Identify significant regional variations"""

        print("🔍 Identifying regional variations...")

        variations = {}

        # Analyze selector consistency
        consistency_data = self.analysis_results.get('selector_consistency', {})

        # Identify fields with high variation across cities
        high_variation_fields = []
        low_variation_fields = []

        for field, data in consistency_data.items():
            consistency_score = data.get('consistency_score', 0)
            success_range = data.get('success_rate_range', 0)

            if consistency_score < 70 or success_range > 30:
                high_variation_fields.append({
                    'field': field,
                    'consistency_score': consistency_score,
                    'success_range': success_range,
                    'city_performances': data.get('city_performances', {})
                })
            elif consistency_score > 90 and success_range < 10:
                low_variation_fields.append({
                    'field': field,
                    'consistency_score': consistency_score,
                    'success_range': success_range
                })

        # Analyze regional performance differences
        regional_data = self.analysis_results.get('regional_analysis', {})
        regional_differences = {}

        if len(regional_data) > 1:
            # Compare regional averages
            regional_averages = {region: data['overall_avg_performance']
                               for region, data in regional_data.items()}

            max_region = max(regional_averages, key=regional_averages.get)
            min_region = min(regional_averages, key=regional_averages.get)

            performance_gap = regional_averages[max_region] - regional_averages[min_region]

            regional_differences = {
                'best_performing_region': max_region,
                'worst_performing_region': min_region,
                'performance_gap': performance_gap,
                'regional_averages': regional_averages
            }

        variations = {
            'high_variation_fields': high_variation_fields,
            'low_variation_fields': low_variation_fields,
            'regional_performance_differences': regional_differences,
            'overall_consistency': self._calculate_overall_consistency()
        }

        self.analysis_results['regional_variations'] = variations

    def _calculate_overall_consistency(self) -> Dict[str, Any]:
        """Calculate overall consistency metrics"""

        consistency_data = self.analysis_results.get('selector_consistency', {})

        if not consistency_data:
            return {}

        consistency_scores = [data['consistency_score'] for data in consistency_data.values()]
        success_ranges = [data['success_rate_range'] for data in consistency_data.values()]

        return {
            'average_consistency_score': statistics.mean(consistency_scores) if consistency_scores else 0,
            'average_success_range': statistics.mean(success_ranges) if success_ranges else 0,
            'fields_with_high_consistency': sum(1 for score in consistency_scores if score > 90),
            'fields_with_low_consistency': sum(1 for score in consistency_scores if score < 70),
            'total_fields_tested': len(consistency_scores)
        }

    def _generate_multi_location_recommendations(self):
        """Generate recommendations based on multi-location analysis"""

        print("💡 Generating multi-location recommendations...")

        recommendations = []

        # Analyze overall consistency
        overall_consistency = self.analysis_results.get('regional_variations', {}).get('overall_consistency', {})
        avg_consistency = overall_consistency.get('average_consistency_score', 0)

        if avg_consistency > 85:
            recommendations.append({
                'category': 'consistency',
                'priority': 'low',
                'recommendation': f"Excellent selector consistency across cities ({avg_consistency:.1f}%). Current selectors are universally effective.",
                'action': 'maintain_current_selectors'
            })
        elif avg_consistency > 70:
            recommendations.append({
                'category': 'consistency',
                'priority': 'medium',
                'recommendation': f"Good selector consistency ({avg_consistency:.1f}%) with room for improvement.",
                'action': 'optimize_inconsistent_selectors'
            })
        else:
            recommendations.append({
                'category': 'consistency',
                'priority': 'high',
                'recommendation': f"Low selector consistency ({avg_consistency:.1f}%) across cities. Regional variations detected.",
                'action': 'implement_location_specific_selectors'
            })

        # Analyze high variation fields
        variations = self.analysis_results.get('regional_variations', {})
        high_variation_fields = variations.get('high_variation_fields', [])

        if high_variation_fields:
            field_names = [field['field'] for field in high_variation_fields[:3]]
            recommendations.append({
                'category': 'field_variation',
                'priority': 'high',
                'recommendation': f"High variation detected in fields: {', '.join(field_names)}",
                'action': 'investigate_field_specific_variations',
                'affected_fields': field_names
            })

        # Analyze regional performance
        regional_diffs = variations.get('regional_performance_differences', {})
        performance_gap = regional_diffs.get('performance_gap', 0)

        if performance_gap > 20:
            best_region = regional_diffs.get('best_performing_region', 'unknown')
            worst_region = regional_diffs.get('worst_performing_region', 'unknown')

            recommendations.append({
                'category': 'regional_performance',
                'priority': 'high',
                'recommendation': f"Significant performance gap ({performance_gap:.1f}%) between {best_region} and {worst_region} regions.",
                'action': 'investigate_regional_differences',
                'best_region': best_region,
                'worst_region': worst_region
            })
        elif performance_gap > 10:
            recommendations.append({
                'category': 'regional_performance',
                'priority': 'medium',
                'recommendation': f"Moderate performance gap ({performance_gap:.1f}%) between regions.",
                'action': 'monitor_regional_performance'
            })
        else:
            recommendations.append({
                'category': 'regional_performance',
                'priority': 'low',
                'recommendation': f"Minimal performance gap ({performance_gap:.1f}%) between regions. Good consistency.",
                'action': 'maintain_current_approach'
            })

        # Price range recommendations
        price_analysis = self.analysis_results.get('price_range_analysis', {})
        dominant_range = price_analysis.get('dominant_range')

        if dominant_range:
            recommendations.append({
                'category': 'price_range',
                'priority': 'low',
                'recommendation': f"Dominant price range is {dominant_range}. Ensure selectors work well for this segment.",
                'action': 'validate_dominant_price_range',
                'dominant_range': dominant_range
            })

        # Cities analyzed
        cities_analyzed = self.analysis_results.get('cities_analyzed', 0)

        if cities_analyzed >= 4:
            recommendations.append({
                'category': 'coverage',
                'priority': 'low',
                'recommendation': f"Good geographical coverage with {cities_analyzed} cities analyzed.",
                'action': 'maintain_multi_city_validation'
            })
        else:
            recommendations.append({
                'category': 'coverage',
                'priority': 'medium',
                'recommendation': f"Limited geographical coverage with {cities_analyzed} cities. Consider expanding analysis.",
                'action': 'expand_geographical_coverage'
            })

        self.analysis_results['recommendations'] = recommendations

    def _save_analysis_results(self):
        """Save analysis results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_location_analysis_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Analysis results saved: {filename}")

        # Save summary report
        summary_filename = f"multi_location_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("MULTI-LOCATION ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")

            f.write(f"Cities Analyzed: {self.analysis_results['cities_analyzed']}\n")
            f.write(f"Total Properties: {self.analysis_results['total_properties_analyzed']}\n\n")

            # Regional analysis
            f.write("REGIONAL PERFORMANCE:\n")
            f.write("-" * 25 + "\n")
            regional_data = self.analysis_results.get('regional_analysis', {})
            for region, data in regional_data.items():
                f.write(f"{region.upper()}:\n")
                f.write(f"  Cities: {', '.join(data['cities'])}\n")
                f.write(f"  Properties: {data['total_properties']}\n")
                f.write(f"  Avg Performance: {data['overall_avg_performance']:.1f}%\n\n")

            # Consistency analysis
            f.write("SELECTOR CONSISTENCY:\n")
            f.write("-" * 25 + "\n")
            consistency_data = self.analysis_results.get('selector_consistency', {})
            for field, data in sorted(consistency_data.items(), key=lambda x: x[1]['consistency_score'], reverse=True)[:5]:
                f.write(f"{field}: {data['consistency_score']:.1f}% consistency\n")

            # Top recommendations
            f.write("\nTOP RECOMMENDATIONS:\n")
            f.write("-" * 25 + "\n")
            recommendations = self.analysis_results.get('recommendations', [])
            high_priority = [r for r in recommendations if r.get('priority') == 'high']
            for i, rec in enumerate(high_priority[:3], 1):
                f.write(f"{i}. {rec['recommendation']}\n")

        print(f"📄 Summary report saved: {summary_filename}")

    def _print_analysis_summary(self):
        """Print comprehensive analysis summary"""

        print("\n📊 MULTI-LOCATION ANALYSIS SUMMARY")
        print("="*50)

        print(f"🌍 Cities Analyzed: {self.analysis_results['cities_analyzed']}")
        print(f"🏠 Total Properties: {self.analysis_results['total_properties_analyzed']}")

        # Regional performance
        regional_data = self.analysis_results.get('regional_analysis', {})
        if regional_data:
            print(f"\n🗺️ REGIONAL PERFORMANCE:")
            for region, data in regional_data.items():
                cities = ', '.join(data['cities'])
                performance = data['overall_avg_performance']
                status = "🟢" if performance > 80 else "🟡" if performance > 60 else "🔴"
                print(f"   {status} {region.upper()}: {performance:.1f}% ({cities})")

        # Consistency analysis
        consistency_data = self.analysis_results.get('selector_consistency', {})
        if consistency_data:
            print(f"\n🎯 SELECTOR CONSISTENCY:")

            # Top consistent fields
            consistent_fields = sorted(consistency_data.items(),
                                     key=lambda x: x[1]['consistency_score'], reverse=True)[:5]

            for field, data in consistent_fields:
                consistency = data['consistency_score']
                status = "🟢" if consistency > 90 else "🟡" if consistency > 70 else "🔴"
                print(f"   {status} {field}: {consistency:.1f}% consistency")

        # Overall consistency
        overall_consistency = self.analysis_results.get('regional_variations', {}).get('overall_consistency', {})
        avg_consistency = overall_consistency.get('average_consistency_score', 0)
        print(f"\n📈 OVERALL CONSISTENCY: {avg_consistency:.1f}%")

        # Price range analysis
        price_analysis = self.analysis_results.get('price_range_analysis', {})
        dominant_range = price_analysis.get('dominant_range')
        if dominant_range:
            print(f"💰 DOMINANT PRICE RANGE: {dominant_range}")

        # Top recommendations
        recommendations = self.analysis_results.get('recommendations', [])
        high_priority = [r for r in recommendations if r.get('priority') == 'high']

        if high_priority:
            print(f"\n🔴 HIGH PRIORITY RECOMMENDATIONS:")
            for i, rec in enumerate(high_priority[:3], 1):
                print(f"   {i}. {rec['recommendation']}")

        # Summary status
        if avg_consistency > 85:
            print(f"\n✅ EXCELLENT: Selectors work consistently across all cities")
        elif avg_consistency > 70:
            print(f"\n🟡 GOOD: Minor variations detected, selectors generally effective")
        else:
            print(f"\n🔴 ATTENTION: Significant regional variations require investigation")


def main():
    """Main function for multi-location analysis"""

    print("🌍 Multi-Location Analysis Tool")
    print("Testing extraction across different cities and price ranges...")
    print()

    try:
        # Initialize analyzer
        analyzer = MultiLocationAnalyzer()

        # Run comprehensive analysis
        results = analyzer.analyze_multi_location_variations()

        if 'error' not in results:
            print("\n✅ MULTI-LOCATION ANALYSIS COMPLETED SUCCESSFULLY!")

            cities_analyzed = results.get('cities_analyzed', 0)
            total_properties = results.get('total_properties_analyzed', 0)

            print(f"🌍 Cities analyzed: {cities_analyzed}")
            print(f"🏠 Properties analyzed: {total_properties}")

            # Overall consistency
            overall_consistency = results.get('regional_variations', {}).get('overall_consistency', {})
            avg_consistency = overall_consistency.get('average_consistency_score', 0)
            print(f"📊 Overall consistency: {avg_consistency:.1f}%")

        else:
            print(f"\n❌ MULTI-LOCATION ANALYSIS FAILED: {results['error']}")

        return results

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
