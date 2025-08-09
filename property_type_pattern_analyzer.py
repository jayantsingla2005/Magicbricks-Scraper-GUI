#!/usr/bin/env python3
"""
Property Type Pattern Analyzer
Analyzes if different property types (Apartment, Floor, Plot, House, Villa) 
have different HTML structures and data organization patterns.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import statistics

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class PropertyTypePatternAnalyzer:
    """
    Comprehensive analyzer for property type-specific HTML patterns
    """
    
    def __init__(self):
        """Initialize property type pattern analyzer"""
        
        # Target property types for analysis
        self.property_types = {
            'apartment': {
                'search_terms': ['apartment', 'flat', 'bhk'],
                'url_patterns': ['apartment', 'flat'],
                'expected_fields': ['bedrooms', 'bathrooms', 'balconies', 'furnishing', 'floor', 'society']
            },
            'house': {
                'search_terms': ['house', 'independent house', 'villa'],
                'url_patterns': ['house', 'independent'],
                'expected_fields': ['bedrooms', 'bathrooms', 'floors', 'parking', 'garden', 'society']
            },
            'floor': {
                'search_terms': ['builder floor', 'floor', 'independent floor'],
                'url_patterns': ['floor', 'builder'],
                'expected_fields': ['bedrooms', 'bathrooms', 'floor', 'total_floors', 'furnishing']
            },
            'plot': {
                'search_terms': ['plot', 'land', 'residential plot'],
                'url_patterns': ['plot', 'land'],
                'expected_fields': ['area', 'facing', 'boundary_wall', 'corner_plot']
            },
            'villa': {
                'search_terms': ['villa', 'bungalow', 'row house'],
                'url_patterns': ['villa', 'bungalow'],
                'expected_fields': ['bedrooms', 'bathrooms', 'floors', 'parking', 'garden', 'swimming_pool']
            }
        }
        
        # Analysis results
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'property_type_analysis': {},
            'structural_differences': {},
            'field_availability_by_type': {},
            'selector_effectiveness_by_type': {},
            'recommendations_by_type': {}
        }
        
        print("🏠 Property Type Pattern Analyzer Initialized")
        print(f"🎯 Analyzing {len(self.property_types)} property types")
        print(f"📊 Target Types: {', '.join(self.property_types.keys())}")
    
    def analyze_property_type_patterns(self) -> Dict[str, Any]:
        """
        Perform comprehensive property type pattern analysis
        """
        
        print("\n🚀 Starting Property Type Pattern Analysis")
        print("="*60)
        
        try:
            # Step 1: Collect samples for each property type
            print("📄 Step 1: Collecting Property Type Samples...")
            type_samples = self._collect_property_type_samples()
            
            if not type_samples:
                print("❌ No property type samples could be collected")
                return self.analysis_results
            
            # Step 2: Analyze structural differences
            print("\n🏗️ Step 2: Analyzing Structural Differences...")
            self._analyze_structural_differences(type_samples)
            
            # Step 3: Analyze field availability by type
            print("\n📊 Step 3: Analyzing Field Availability by Type...")
            self._analyze_field_availability_by_type(type_samples)
            
            # Step 4: Test selector effectiveness by type
            print("\n🧪 Step 4: Testing Selector Effectiveness by Type...")
            self._test_selector_effectiveness_by_type(type_samples)
            
            # Step 5: Generate type-specific recommendations
            print("\n💡 Step 5: Generating Type-Specific Recommendations...")
            self._generate_type_specific_recommendations()
            
            # Step 6: Save analysis results
            print("\n💾 Step 6: Saving Analysis Results...")
            self._save_analysis_results()
            
            print("\n✅ Property Type Pattern Analysis Complete!")
            self._print_analysis_summary()
            
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ Property type pattern analysis failed: {str(e)}")
            self.analysis_results['error'] = str(e)
            return self.analysis_results
    
    def _collect_property_type_samples(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect samples for each property type"""
        
        type_samples = {}
        
        for prop_type, config in self.property_types.items():
            print(f"🏠 Collecting samples for {prop_type}...")
            
            samples = self._collect_samples_for_type(prop_type, config)
            
            if samples:
                type_samples[prop_type] = samples
                print(f"✅ {prop_type}: Collected {len(samples)} samples")
            else:
                print(f"⚠️ {prop_type}: No samples found")
        
        return type_samples
    
    def _collect_samples_for_type(self, prop_type: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect samples for a specific property type"""
        
        driver = self._setup_browser()
        samples = []
        
        try:
            # Try different search strategies
            search_urls = self._generate_search_urls(prop_type, config)
            
            for search_url in search_urls[:2]:  # Try first 2 URLs
                try:
                    print(f"   📄 Searching: {search_url}")
                    
                    driver.get(search_url)
                    
                    # Wait for page load
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    time.sleep(3)
                    
                    # Parse page
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Find property cards
                    property_cards = soup.select('.mb-srp__card')
                    
                    # Filter cards that match property type
                    type_cards = self._filter_cards_by_type(property_cards, prop_type, config)
                    
                    for card in type_cards[:10]:  # Limit to 10 per URL
                        samples.append({
                            'property_type': prop_type,
                            'search_url': search_url,
                            'card_html': str(card),
                            'card_soup': card,
                            'title': self._extract_card_title(card),
                            'identified_type': self._identify_property_type_from_card(card)
                        })
                    
                    if len(samples) >= 15:  # Collect up to 15 samples per type
                        break
                
                except Exception as e:
                    print(f"   ❌ Error with search URL: {str(e)}")
                
                time.sleep(2)
        
        finally:
            driver.quit()
        
        return samples
    
    def _generate_search_urls(self, prop_type: str, config: Dict[str, Any]) -> List[str]:
        """Generate search URLs for property type"""
        
        base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
        
        urls = []
        
        # General search
        urls.append(base_url)
        
        # Type-specific searches
        for search_term in config['search_terms'][:2]:
            # Try with search parameter (if supported)
            search_url = f"{base_url}?search={search_term.replace(' ', '+')}"
            urls.append(search_url)
        
        return urls
    
    def _filter_cards_by_type(self, cards: List[Tag], prop_type: str, config: Dict[str, Any]) -> List[Tag]:
        """Filter cards that match the property type"""
        
        filtered_cards = []
        search_terms = [term.lower() for term in config['search_terms']]
        
        for card in cards:
            card_text = card.get_text().lower()
            
            # Check if card contains property type indicators
            if any(term in card_text for term in search_terms):
                filtered_cards.append(card)
            
            # Additional filtering based on property type
            if prop_type == 'plot' and any(term in card_text for term in ['sqft', 'sq yards', 'acres']):
                if not any(term in card_text for term in ['bhk', 'bedroom', 'bathroom']):
                    filtered_cards.append(card)
        
        return filtered_cards
    
    def _extract_card_title(self, card: Tag) -> str:
        """Extract title from property card"""
        
        try:
            # Try different title selectors
            title_selectors = [
                '.mb-srp__card--title a',
                '.mb-srp__card--title',
                'h2 a',
                'h3 a',
                'a[href*="pdpid"]'
            ]
            
            for selector in title_selectors:
                elements = card.select(selector)
                if elements:
                    return elements[0].get_text(strip=True)
            
            return "Title not found"
        
        except Exception:
            return "Title extraction error"
    
    def _identify_property_type_from_card(self, card: Tag) -> str:
        """Identify property type from card content"""
        
        card_text = card.get_text().lower()
        
        # Property type indicators
        type_indicators = {
            'apartment': ['apartment', 'flat', 'bhk', 'residential apartment'],
            'house': ['independent house', 'house', 'villa'],
            'floor': ['builder floor', 'independent floor', 'floor'],
            'plot': ['plot', 'land', 'residential plot', 'sq yards'],
            'villa': ['villa', 'bungalow', 'row house']
        }
        
        # Count matches for each type
        type_scores = {}
        for prop_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in card_text)
            type_scores[prop_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        
        return 'unknown'
    
    def _analyze_structural_differences(self, type_samples: Dict[str, List[Dict[str, Any]]]):
        """Analyze structural differences between property types"""
        
        print("🏗️ Analyzing structural differences between property types...")
        
        structural_analysis = {}
        
        for prop_type, samples in type_samples.items():
            print(f"   🏠 Analyzing {prop_type} structure...")
            
            # Analyze HTML structure patterns
            class_patterns = defaultdict(int)
            tag_patterns = defaultdict(int)
            content_patterns = defaultdict(int)
            
            for sample in samples:
                card = sample['card_soup']
                
                # Analyze class patterns
                for element in card.find_all():
                    classes = element.get('class', [])
                    for cls in classes:
                        class_patterns[cls] += 1
                
                # Analyze tag patterns
                for element in card.find_all():
                    tag_patterns[element.name] += 1
                
                # Analyze content patterns
                text_content = card.get_text().lower()
                
                # Look for property-specific content patterns
                if 'bhk' in text_content:
                    content_patterns['has_bhk'] += 1
                if 'sqft' in text_content:
                    content_patterns['has_area'] += 1
                if 'floor' in text_content:
                    content_patterns['has_floor_info'] += 1
                if 'parking' in text_content:
                    content_patterns['has_parking'] += 1
            
            # Store analysis for this property type
            structural_analysis[prop_type] = {
                'sample_count': len(samples),
                'top_classes': sorted(class_patterns.items(), key=lambda x: x[1], reverse=True)[:10],
                'top_tags': sorted(tag_patterns.items(), key=lambda x: x[1], reverse=True)[:10],
                'content_patterns': dict(content_patterns),
                'unique_classes': len(class_patterns),
                'avg_classes_per_card': sum(class_patterns.values()) / len(samples) if samples else 0
            }
        
        self.analysis_results['structural_differences'] = structural_analysis
    
    def _analyze_field_availability_by_type(self, type_samples: Dict[str, List[Dict[str, Any]]]):
        """Analyze field availability for each property type"""
        
        print("📊 Analyzing field availability by property type...")
        
        field_availability = {}
        
        # Common fields to check
        common_fields = [
            'price', 'area', 'bedrooms', 'bathrooms', 'balconies',
            'furnishing', 'floor', 'parking', 'age', 'facing'
        ]
        
        for prop_type, samples in type_samples.items():
            print(f"   📊 Analyzing {prop_type} field availability...")
            
            field_counts = defaultdict(int)
            
            for sample in samples:
                card = sample['card_soup']
                card_text = card.get_text().lower()
                
                # Check for field indicators
                for field in common_fields:
                    if self._field_present_in_card(card, card_text, field):
                        field_counts[field] += 1
            
            # Calculate availability percentages
            field_availability[prop_type] = {}
            for field in common_fields:
                availability = (field_counts[field] / len(samples) * 100) if samples else 0
                field_availability[prop_type][field] = {
                    'count': field_counts[field],
                    'total_samples': len(samples),
                    'availability_percentage': availability
                }
        
        self.analysis_results['field_availability_by_type'] = field_availability
    
    def _field_present_in_card(self, card: Tag, card_text: str, field: str) -> bool:
        """Check if a field is present in the card"""
        
        field_indicators = {
            'price': ['₹', 'lac', 'lakh', 'cr', 'crore'],
            'area': ['sqft', 'sq ft', 'sq.ft', 'square feet'],
            'bedrooms': ['bhk', 'bedroom', 'bed'],
            'bathrooms': ['bathroom', 'bath', 'toilet'],
            'balconies': ['balcony', 'balcon'],
            'furnishing': ['furnished', 'unfurnished', 'semi'],
            'floor': ['floor', 'ground', 'basement'],
            'parking': ['parking', 'car'],
            'age': ['year', 'old', 'new', 'ready'],
            'facing': ['facing', 'north', 'south', 'east', 'west']
        }
        
        indicators = field_indicators.get(field, [])
        return any(indicator in card_text for indicator in indicators)
    
    def _test_selector_effectiveness_by_type(self, type_samples: Dict[str, List[Dict[str, Any]]]):
        """Test selector effectiveness for each property type"""
        
        print("🧪 Testing selector effectiveness by property type...")
        
        # Load improved selectors
        try:
            with open('config/improved_scraper_config.json', 'r') as f:
                config = json.load(f)
                selectors = config.get('selectors', {})
        except FileNotFoundError:
            selectors = self._get_default_selectors()
        
        selector_effectiveness = {}
        
        for prop_type, samples in type_samples.items():
            print(f"   🧪 Testing selectors for {prop_type}...")
            
            type_effectiveness = {}
            
            # Test key selectors
            test_selectors = ['title', 'price', 'area', 'bedrooms', 'bathrooms']
            
            for field in test_selectors:
                selector = selectors.get(field)
                if selector:
                    success_count = 0
                    
                    for sample in samples:
                        card = sample['card_soup']
                        
                        try:
                            elements = card.select(selector)
                            if elements and elements[0].get_text(strip=True):
                                success_count += 1
                        except Exception:
                            pass
                    
                    effectiveness = (success_count / len(samples) * 100) if samples else 0
                    type_effectiveness[field] = {
                        'selector': selector,
                        'success_count': success_count,
                        'total_samples': len(samples),
                        'effectiveness_percentage': effectiveness
                    }
            
            selector_effectiveness[prop_type] = type_effectiveness
        
        self.analysis_results['selector_effectiveness_by_type'] = selector_effectiveness
    
    def _get_default_selectors(self) -> Dict[str, str]:
        """Get default selectors if config not available"""
        
        return {
            'title': '.mb-srp__card--title a',
            'price': '.mb-srp__card__price--amount',
            'area': '.mb-srp__card__price--size',
            'bedrooms': '.mb-srp__card__summary--value',
            'bathrooms': '.mb-srp__card__summary--value'
        }
    
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

    def _generate_type_specific_recommendations(self):
        """Generate type-specific recommendations based on analysis"""

        print("💡 Generating type-specific recommendations...")

        recommendations = {}

        # Analyze each property type
        for prop_type in self.property_types.keys():
            type_recommendations = []

            # Check structural differences
            structural = self.analysis_results['structural_differences'].get(prop_type, {})
            field_availability = self.analysis_results['field_availability_by_type'].get(prop_type, {})
            selector_effectiveness = self.analysis_results['selector_effectiveness_by_type'].get(prop_type, {})

            # Structural recommendations
            if structural.get('sample_count', 0) > 0:
                unique_classes = structural.get('unique_classes', 0)
                avg_classes = structural.get('avg_classes_per_card', 0)

                if unique_classes > 50:
                    type_recommendations.append({
                        'category': 'structure',
                        'priority': 'medium',
                        'recommendation': f"{prop_type} has complex structure ({unique_classes} unique classes). Consider type-specific selectors.",
                        'action': 'develop_type_specific_selectors'
                    })

                if avg_classes > 30:
                    type_recommendations.append({
                        'category': 'structure',
                        'priority': 'low',
                        'recommendation': f"{prop_type} has rich HTML structure ({avg_classes:.1f} avg classes). Good for detailed extraction.",
                        'action': 'leverage_rich_structure'
                    })

            # Field availability recommendations
            if field_availability:
                low_availability_fields = []
                high_availability_fields = []

                for field, data in field_availability.items():
                    availability = data.get('availability_percentage', 0)
                    if availability < 50:
                        low_availability_fields.append(field)
                    elif availability > 80:
                        high_availability_fields.append(field)

                if low_availability_fields:
                    type_recommendations.append({
                        'category': 'field_availability',
                        'priority': 'high',
                        'recommendation': f"{prop_type} has low availability for: {', '.join(low_availability_fields[:3])}",
                        'action': 'improve_field_extraction',
                        'affected_fields': low_availability_fields
                    })

                if high_availability_fields:
                    type_recommendations.append({
                        'category': 'field_availability',
                        'priority': 'low',
                        'recommendation': f"{prop_type} has excellent availability for: {', '.join(high_availability_fields[:3])}",
                        'action': 'maintain_current_approach',
                        'strong_fields': high_availability_fields
                    })

            # Selector effectiveness recommendations
            if selector_effectiveness:
                ineffective_selectors = []
                effective_selectors = []

                for field, data in selector_effectiveness.items():
                    effectiveness = data.get('effectiveness_percentage', 0)
                    if effectiveness < 60:
                        ineffective_selectors.append(field)
                    elif effectiveness > 85:
                        effective_selectors.append(field)

                if ineffective_selectors:
                    type_recommendations.append({
                        'category': 'selector_effectiveness',
                        'priority': 'high',
                        'recommendation': f"{prop_type} selectors need improvement for: {', '.join(ineffective_selectors)}",
                        'action': 'optimize_selectors',
                        'affected_selectors': ineffective_selectors
                    })

                if effective_selectors:
                    type_recommendations.append({
                        'category': 'selector_effectiveness',
                        'priority': 'low',
                        'recommendation': f"{prop_type} selectors work well for: {', '.join(effective_selectors)}",
                        'action': 'maintain_selectors',
                        'effective_selectors': effective_selectors
                    })

            recommendations[prop_type] = type_recommendations

        # Cross-type recommendations
        cross_type_recommendations = self._generate_cross_type_recommendations()
        recommendations['cross_type'] = cross_type_recommendations

        self.analysis_results['recommendations_by_type'] = recommendations

    def _generate_cross_type_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations that apply across property types"""

        cross_recommendations = []

        # Analyze consistency across types
        structural_data = self.analysis_results.get('structural_differences', {})

        if len(structural_data) > 1:
            # Check if all types use similar class patterns
            common_classes = set()
            first_type = True

            for prop_type, data in structural_data.items():
                top_classes = [cls for cls, count in data.get('top_classes', [])]

                if first_type:
                    common_classes = set(top_classes)
                    first_type = False
                else:
                    common_classes = common_classes.intersection(set(top_classes))

            if len(common_classes) > 5:
                cross_recommendations.append({
                    'category': 'consistency',
                    'priority': 'medium',
                    'recommendation': f"All property types share {len(common_classes)} common classes. Universal selectors possible.",
                    'action': 'develop_universal_selectors',
                    'common_classes': list(common_classes)[:10]
                })
            else:
                cross_recommendations.append({
                    'category': 'consistency',
                    'priority': 'high',
                    'recommendation': f"Property types have different structures. Type-specific selectors recommended.",
                    'action': 'implement_type_specific_logic',
                    'common_classes_count': len(common_classes)
                })

        # Analyze field availability consistency
        field_data = self.analysis_results.get('field_availability_by_type', {})

        if field_data:
            # Find fields that are consistently available across types
            consistent_fields = []
            inconsistent_fields = []

            all_fields = set()
            for type_data in field_data.values():
                all_fields.update(type_data.keys())

            for field in all_fields:
                availabilities = []
                for prop_type, type_data in field_data.items():
                    if field in type_data:
                        availabilities.append(type_data[field]['availability_percentage'])

                if availabilities:
                    avg_availability = sum(availabilities) / len(availabilities)
                    availability_range = max(availabilities) - min(availabilities)

                    if availability_range < 20 and avg_availability > 70:
                        consistent_fields.append(field)
                    elif availability_range > 40:
                        inconsistent_fields.append(field)

            if consistent_fields:
                cross_recommendations.append({
                    'category': 'field_consistency',
                    'priority': 'low',
                    'recommendation': f"Fields consistently available across types: {', '.join(consistent_fields[:5])}",
                    'action': 'prioritize_consistent_fields',
                    'consistent_fields': consistent_fields
                })

            if inconsistent_fields:
                cross_recommendations.append({
                    'category': 'field_consistency',
                    'priority': 'medium',
                    'recommendation': f"Fields with inconsistent availability: {', '.join(inconsistent_fields[:5])}",
                    'action': 'implement_type_aware_extraction',
                    'inconsistent_fields': inconsistent_fields
                })

        return cross_recommendations

    def _save_analysis_results(self):
        """Save analysis results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"property_type_pattern_analysis_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Analysis results saved: {filename}")

        # Save summary report
        summary_filename = f"property_type_analysis_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("PROPERTY TYPE PATTERN ANALYSIS SUMMARY\n")
            f.write("="*60 + "\n\n")

            # Property type overview
            f.write("PROPERTY TYPE OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            structural_data = self.analysis_results.get('structural_differences', {})
            for prop_type, data in structural_data.items():
                f.write(f"{prop_type.upper()}:\n")
                f.write(f"  Samples: {data.get('sample_count', 0)}\n")
                f.write(f"  Unique Classes: {data.get('unique_classes', 0)}\n")
                f.write(f"  Avg Classes/Card: {data.get('avg_classes_per_card', 0):.1f}\n\n")

            # Field availability summary
            f.write("FIELD AVAILABILITY BY TYPE:\n")
            f.write("-" * 30 + "\n")
            field_data = self.analysis_results.get('field_availability_by_type', {})
            for prop_type, type_data in field_data.items():
                f.write(f"{prop_type.upper()}:\n")
                for field, data in sorted(type_data.items(), key=lambda x: x[1]['availability_percentage'], reverse=True)[:5]:
                    f.write(f"  {field}: {data['availability_percentage']:.1f}%\n")
                f.write("\n")

            # Top recommendations
            f.write("TOP RECOMMENDATIONS:\n")
            f.write("-" * 30 + "\n")
            recommendations = self.analysis_results.get('recommendations_by_type', {})
            for prop_type, type_recs in recommendations.items():
                if prop_type != 'cross_type':
                    high_priority = [r for r in type_recs if r.get('priority') == 'high']
                    if high_priority:
                        f.write(f"{prop_type.upper()}:\n")
                        for rec in high_priority[:2]:
                            f.write(f"  - {rec['recommendation']}\n")
                        f.write("\n")

        print(f"📄 Summary report saved: {summary_filename}")

    def _print_analysis_summary(self):
        """Print comprehensive analysis summary"""

        print("\n📊 PROPERTY TYPE PATTERN ANALYSIS SUMMARY")
        print("="*60)

        # Property type overview
        structural_data = self.analysis_results.get('structural_differences', {})
        print(f"🏠 PROPERTY TYPES ANALYZED: {len(structural_data)}")

        for prop_type, data in structural_data.items():
            sample_count = data.get('sample_count', 0)
            unique_classes = data.get('unique_classes', 0)
            print(f"   📊 {prop_type.upper()}: {sample_count} samples, {unique_classes} unique classes")

        # Field availability insights
        field_data = self.analysis_results.get('field_availability_by_type', {})
        if field_data:
            print(f"\n📈 FIELD AVAILABILITY INSIGHTS:")

            # Find best and worst performing fields across types
            all_field_scores = defaultdict(list)
            for prop_type, type_data in field_data.items():
                for field, data in type_data.items():
                    all_field_scores[field].append(data['availability_percentage'])

            # Calculate average availability per field
            field_averages = {}
            for field, scores in all_field_scores.items():
                field_averages[field] = sum(scores) / len(scores)

            # Top performing fields
            top_fields = sorted(field_averages.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   🟢 Best Fields: {', '.join([f'{field} ({avg:.1f}%)' for field, avg in top_fields])}")

            # Worst performing fields
            worst_fields = sorted(field_averages.items(), key=lambda x: x[1])[:3]
            print(f"   🔴 Challenging Fields: {', '.join([f'{field} ({avg:.1f}%)' for field, avg in worst_fields])}")

        # Selector effectiveness insights
        selector_data = self.analysis_results.get('selector_effectiveness_by_type', {})
        if selector_data:
            print(f"\n🎯 SELECTOR EFFECTIVENESS:")

            for prop_type, type_data in selector_data.items():
                avg_effectiveness = sum(data['effectiveness_percentage'] for data in type_data.values()) / len(type_data) if type_data else 0
                status = "🟢" if avg_effectiveness > 80 else "🟡" if avg_effectiveness > 60 else "🔴"
                print(f"   {status} {prop_type.upper()}: {avg_effectiveness:.1f}% average effectiveness")

        # Top recommendations
        recommendations = self.analysis_results.get('recommendations_by_type', {})
        high_priority_count = 0
        for prop_type, type_recs in recommendations.items():
            high_priority_count += len([r for r in type_recs if r.get('priority') == 'high'])

        print(f"\n💡 RECOMMENDATIONS GENERATED:")
        print(f"   🔴 High Priority: {high_priority_count} recommendations")
        print(f"   📊 Total Types: {len([k for k in recommendations.keys() if k != 'cross_type'])}")

        # Cross-type insights
        cross_recs = recommendations.get('cross_type', [])
        if cross_recs:
            print(f"   🔄 Cross-Type: {len(cross_recs)} recommendations")


def main():
    """Main function for property type pattern analysis"""

    print("🏠 Property Type Pattern Analyzer")
    print("Analyzing HTML structure differences across property types...")
    print()

    try:
        # Initialize analyzer
        analyzer = PropertyTypePatternAnalyzer()

        # Run comprehensive analysis
        results = analyzer.analyze_property_type_patterns()

        if 'error' not in results:
            print("\n✅ PROPERTY TYPE PATTERN ANALYSIS COMPLETED SUCCESSFULLY!")

            structural_data = results.get('structural_differences', {})
            print(f"🏠 Property types analyzed: {len(structural_data)}")

            recommendations = results.get('recommendations_by_type', {})
            total_recommendations = sum(len(recs) for recs in recommendations.values())
            print(f"💡 Total recommendations: {total_recommendations}")

        else:
            print(f"\n❌ PROPERTY TYPE PATTERN ANALYSIS FAILED: {results['error']}")

        return results

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
