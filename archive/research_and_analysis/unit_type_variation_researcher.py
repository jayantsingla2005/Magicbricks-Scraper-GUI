#!/usr/bin/env python3
"""
Unit Type Variation Research Tool
Analyzes different area units (sqft, sq yards, acres), price units (Lac, Cr, per sqft),
and measurement standards across MagicBricks listings to ensure robust parsing.
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


class UnitTypeVariationResearcher:
    """
    Comprehensive researcher for unit type variations across MagicBricks
    """
    
    def __init__(self):
        """Initialize unit type variation researcher"""
        
        # Unit types to research
        self.unit_categories = {
            'area_units': {
                'patterns': [
                    r'(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|square\s*feet?)',
                    r'(\d+(?:\.\d+)?)\s*(sq\.?\s*yards?|square\s*yards?)',
                    r'(\d+(?:\.\d+)?)\s*(acres?)',
                    r'(\d+(?:\.\d+)?)\s*(sq\.?\s*m|square\s*meters?)',
                    r'(\d+(?:\.\d+)?)\s*(bigha|katha|gunta|cent)'
                ],
                'expected_units': ['sqft', 'sq ft', 'sq yards', 'acres', 'sq m', 'bigha', 'katha']
            },
            'price_units': {
                'patterns': [
                    r'₹\s*(\d+(?:\.\d+)?)\s*(lac|lakh)',
                    r'₹\s*(\d+(?:\.\d+)?)\s*(cr|crore)',
                    r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*per\s*(sqft|sq\.?\s*ft)',
                    r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*per\s*(sq\.?\s*yards?)',
                    r'(\d+(?:\.\d+)?)\s*(lac|lakh|cr|crore)\s*onwards?',
                    r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(lac|lakh|cr|crore)'
                ],
                'expected_units': ['lac', 'lakh', 'cr', 'crore', 'per sqft', 'per sq yards', 'onwards']
            },
            'measurement_standards': {
                'patterns': [
                    r'carpet\s*area:?\s*(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft)',
                    r'built\s*up\s*area:?\s*(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft)',
                    r'super\s*area:?\s*(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft)',
                    r'plot\s*area:?\s*(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sq\.?\s*yards?)',
                    r'land\s*area:?\s*(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|acres?)'
                ],
                'expected_standards': ['carpet area', 'built up area', 'super area', 'plot area', 'land area']
            }
        }
        
        # Research results
        self.research_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_analyzed': 0,
            'properties_analyzed': 0,
            'unit_patterns_found': {},
            'unit_frequency_analysis': {},
            'parsing_challenges': {},
            'standardization_recommendations': {},
            'extraction_patterns': {}
        }
        
        # Test URLs for different property types
        self.test_urls = [
            'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs',  # Mixed properties
            'https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs',   # High-value properties
            'https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs' # Tech hub properties
        ]
        
        print("📏 Unit Type Variation Researcher Initialized")
        print(f"🎯 Researching {len(self.unit_categories)} unit categories")
        print(f"📊 Target URLs: {len(self.test_urls)}")
    
    def research_unit_type_variations(self) -> Dict[str, Any]:
        """
        Perform comprehensive unit type variation research
        """
        
        print("\n🚀 Starting Unit Type Variation Research")
        print("="*60)
        
        try:
            # Step 1: Collect unit data from multiple sources
            print("📄 Step 1: Collecting Unit Data from Multiple Sources...")
            unit_data = self._collect_unit_data()
            
            if not unit_data:
                print("❌ No unit data could be collected")
                return self.research_results
            
            # Step 2: Analyze unit patterns
            print("\n📊 Step 2: Analyzing Unit Patterns...")
            self._analyze_unit_patterns(unit_data)
            
            # Step 3: Analyze frequency distributions
            print("\n📈 Step 3: Analyzing Frequency Distributions...")
            self._analyze_frequency_distributions(unit_data)
            
            # Step 4: Identify parsing challenges
            print("\n🔍 Step 4: Identifying Parsing Challenges...")
            self._identify_parsing_challenges(unit_data)
            
            # Step 5: Develop extraction patterns
            print("\n⚡ Step 5: Developing Extraction Patterns...")
            self._develop_extraction_patterns()
            
            # Step 6: Generate standardization recommendations
            print("\n💡 Step 6: Generating Standardization Recommendations...")
            self._generate_standardization_recommendations()
            
            # Step 7: Save research results
            print("\n💾 Step 7: Saving Research Results...")
            self._save_research_results()
            
            print("\n✅ Unit Type Variation Research Complete!")
            self._print_research_summary()
            
            return self.research_results
            
        except Exception as e:
            print(f"❌ Unit type variation research failed: {str(e)}")
            self.research_results['error'] = str(e)
            return self.research_results
    
    def _collect_unit_data(self) -> List[Dict[str, Any]]:
        """Collect unit data from multiple property sources"""
        
        all_unit_data = []
        
        for i, url in enumerate(self.test_urls, 1):
            print(f"📄 Collecting from source {i}/{len(self.test_urls)}...")
            
            try:
                source_data = self._collect_from_single_source(url)
                if source_data:
                    all_unit_data.extend(source_data)
                    print(f"✅ Source {i}: Collected {len(source_data)} property data points")
                else:
                    print(f"⚠️ Source {i}: No data collected")
                
                # Delay between sources
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Source {i}: Collection failed - {str(e)}")
        
        self.research_results['pages_analyzed'] = len(self.test_urls)
        self.research_results['properties_analyzed'] = len(all_unit_data)
        
        return all_unit_data
    
    def _collect_from_single_source(self, url: str) -> List[Dict[str, Any]]:
        """Collect unit data from a single source"""
        
        driver = self._setup_browser()
        
        try:
            # Navigate to page
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find property cards
            property_cards = soup.select('.mb-srp__card')
            
            source_data = []
            
            for i, card in enumerate(property_cards[:25]):  # Analyze first 25 properties
                try:
                    property_data = self._extract_unit_data_from_card(card, i)
                    if property_data:
                        property_data['source_url'] = url
                        source_data.append(property_data)
                
                except Exception as e:
                    print(f"   ⚠️ Error extracting from card {i}: {str(e)}")
            
            return source_data
            
        finally:
            driver.quit()
    
    def _extract_unit_data_from_card(self, card: Tag, card_index: int) -> Optional[Dict[str, Any]]:
        """Extract unit data from a property card"""
        
        try:
            # Get all text content from the card
            card_text = card.get_text()
            
            # Extract different types of units
            property_data = {
                'card_index': card_index,
                'raw_text': card_text,
                'area_units_found': [],
                'price_units_found': [],
                'measurement_standards_found': [],
                'parsing_issues': []
            }
            
            # Extract area units
            for pattern in self.unit_categories['area_units']['patterns']:
                matches = re.findall(pattern, card_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value, unit = match
                        property_data['area_units_found'].append({
                            'value': value,
                            'unit': unit.strip(),
                            'full_match': f"{value} {unit}",
                            'pattern_used': pattern
                        })
            
            # Extract price units
            for pattern in self.unit_categories['price_units']['patterns']:
                matches = re.findall(pattern, card_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            value, unit = match
                            property_data['price_units_found'].append({
                                'value': value,
                                'unit': unit.strip(),
                                'full_match': f"{value} {unit}",
                                'pattern_used': pattern
                            })
                        elif len(match) == 3:  # Range pattern
                            value1, value2, unit = match
                            property_data['price_units_found'].append({
                                'value': f"{value1}-{value2}",
                                'unit': unit.strip(),
                                'full_match': f"{value1}-{value2} {unit}",
                                'pattern_used': pattern,
                                'type': 'range'
                            })
            
            # Extract measurement standards
            for pattern in self.unit_categories['measurement_standards']['patterns']:
                matches = re.findall(pattern, card_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value, unit = match
                        # Extract the measurement type from the pattern
                        measurement_type = self._extract_measurement_type(pattern)
                        property_data['measurement_standards_found'].append({
                            'measurement_type': measurement_type,
                            'value': value,
                            'unit': unit.strip(),
                            'full_match': f"{measurement_type}: {value} {unit}",
                            'pattern_used': pattern
                        })
            
            # Check for parsing issues
            property_data['parsing_issues'] = self._identify_card_parsing_issues(card_text)
            
            return property_data
            
        except Exception as e:
            return None
    
    def _extract_measurement_type(self, pattern: str) -> str:
        """Extract measurement type from regex pattern"""
        
        if 'carpet' in pattern:
            return 'carpet area'
        elif 'built' in pattern:
            return 'built up area'
        elif 'super' in pattern:
            return 'super area'
        elif 'plot' in pattern:
            return 'plot area'
        elif 'land' in pattern:
            return 'land area'
        else:
            return 'unknown'
    
    def _identify_card_parsing_issues(self, card_text: str) -> List[str]:
        """Identify potential parsing issues in card text"""
        
        issues = []
        
        # Check for ambiguous units
        if re.search(r'\d+\s*sq\s*(?!ft|yards|m)', card_text, re.IGNORECASE):
            issues.append('ambiguous_sq_unit')
        
        # Check for missing currency symbols
        if re.search(r'(?<![₹])\d+\s*(lac|lakh|cr|crore)', card_text, re.IGNORECASE):
            issues.append('missing_currency_symbol')
        
        # Check for multiple area measurements
        area_count = len(re.findall(r'\d+\s*(sqft|sq\.?\s*ft)', card_text, re.IGNORECASE))
        if area_count > 2:
            issues.append('multiple_area_measurements')
        
        # Check for unconventional formats
        if re.search(r'\d+\s*[a-zA-Z]+\s*\d+', card_text):
            issues.append('unconventional_format')
        
        # Check for range without clear indicators
        if re.search(r'\d+\s*-\s*\d+(?!\s*(lac|lakh|cr|crore|sqft))', card_text, re.IGNORECASE):
            issues.append('unclear_range')
        
        return issues
    
    def _analyze_unit_patterns(self, unit_data: List[Dict[str, Any]]):
        """Analyze patterns in unit usage"""
        
        print("📊 Analyzing unit patterns...")
        
        patterns_found = {
            'area_units': defaultdict(int),
            'price_units': defaultdict(int),
            'measurement_standards': defaultdict(int)
        }
        
        # Count occurrences of each unit type
        for property_data in unit_data:
            # Area units
            for area_unit in property_data.get('area_units_found', []):
                unit = area_unit['unit'].lower().strip()
                patterns_found['area_units'][unit] += 1
            
            # Price units
            for price_unit in property_data.get('price_units_found', []):
                unit = price_unit['unit'].lower().strip()
                patterns_found['price_units'][unit] += 1
            
            # Measurement standards
            for measurement in property_data.get('measurement_standards_found', []):
                measurement_type = measurement['measurement_type']
                patterns_found['measurement_standards'][measurement_type] += 1
        
        # Convert to regular dicts and sort by frequency
        for category in patterns_found:
            sorted_patterns = sorted(patterns_found[category].items(), 
                                   key=lambda x: x[1], reverse=True)
            patterns_found[category] = dict(sorted_patterns)
        
        self.research_results['unit_patterns_found'] = patterns_found
    
    def _analyze_frequency_distributions(self, unit_data: List[Dict[str, Any]]):
        """Analyze frequency distributions of different units"""
        
        print("📈 Analyzing frequency distributions...")
        
        frequency_analysis = {}
        
        # Analyze area unit frequencies
        area_units = []
        for property_data in unit_data:
            for area_unit in property_data.get('area_units_found', []):
                area_units.append(area_unit['unit'].lower().strip())
        
        if area_units:
            area_counter = Counter(area_units)
            total_area = len(area_units)
            
            frequency_analysis['area_units'] = {
                'total_occurrences': total_area,
                'unique_units': len(area_counter),
                'most_common': area_counter.most_common(5),
                'percentages': {unit: (count/total_area*100) for unit, count in area_counter.items()}
            }
        
        # Analyze price unit frequencies
        price_units = []
        for property_data in unit_data:
            for price_unit in property_data.get('price_units_found', []):
                price_units.append(price_unit['unit'].lower().strip())
        
        if price_units:
            price_counter = Counter(price_units)
            total_price = len(price_units)
            
            frequency_analysis['price_units'] = {
                'total_occurrences': total_price,
                'unique_units': len(price_counter),
                'most_common': price_counter.most_common(5),
                'percentages': {unit: (count/total_price*100) for unit, count in price_counter.items()}
            }
        
        # Analyze measurement standard frequencies
        measurement_standards = []
        for property_data in unit_data:
            for measurement in property_data.get('measurement_standards_found', []):
                measurement_standards.append(measurement['measurement_type'])
        
        if measurement_standards:
            measurement_counter = Counter(measurement_standards)
            total_measurements = len(measurement_standards)
            
            frequency_analysis['measurement_standards'] = {
                'total_occurrences': total_measurements,
                'unique_standards': len(measurement_counter),
                'most_common': measurement_counter.most_common(5),
                'percentages': {standard: (count/total_measurements*100) for standard, count in measurement_counter.items()}
            }
        
        self.research_results['unit_frequency_analysis'] = frequency_analysis
    
    def _identify_parsing_challenges(self, unit_data: List[Dict[str, Any]]):
        """Identify common parsing challenges"""
        
        print("🔍 Identifying parsing challenges...")
        
        challenges = {
            'common_issues': defaultdict(int),
            'problematic_patterns': [],
            'edge_cases': [],
            'standardization_needs': []
        }
        
        # Analyze parsing issues
        for property_data in unit_data:
            for issue in property_data.get('parsing_issues', []):
                challenges['common_issues'][issue] += 1
        
        # Identify problematic patterns
        for property_data in unit_data:
            # Check for properties with no units found
            if (not property_data.get('area_units_found') and 
                not property_data.get('price_units_found')):
                challenges['problematic_patterns'].append({
                    'type': 'no_units_found',
                    'card_index': property_data['card_index'],
                    'sample_text': property_data['raw_text'][:200]
                })
            
            # Check for properties with too many units (potential confusion)
            total_units = (len(property_data.get('area_units_found', [])) + 
                          len(property_data.get('price_units_found', [])))
            if total_units > 5:
                challenges['edge_cases'].append({
                    'type': 'too_many_units',
                    'card_index': property_data['card_index'],
                    'unit_count': total_units,
                    'sample_text': property_data['raw_text'][:200]
                })
        
        # Identify standardization needs
        area_patterns = self.research_results.get('unit_patterns_found', {}).get('area_units', {})
        
        # Check for similar units with different representations
        sqft_variants = [unit for unit in area_patterns.keys() if 'sq' in unit and 'ft' in unit]
        if len(sqft_variants) > 2:
            challenges['standardization_needs'].append({
                'category': 'area_units',
                'issue': 'multiple_sqft_representations',
                'variants': sqft_variants
            })
        
        self.research_results['parsing_challenges'] = challenges
    
    def _develop_extraction_patterns(self):
        """Develop robust extraction patterns based on research"""
        
        print("⚡ Developing extraction patterns...")
        
        # Based on frequency analysis, develop optimized patterns
        frequency_data = self.research_results.get('unit_frequency_analysis', {})
        
        extraction_patterns = {
            'area_extraction': {
                'primary_patterns': [],
                'fallback_patterns': [],
                'normalization_rules': {}
            },
            'price_extraction': {
                'primary_patterns': [],
                'fallback_patterns': [],
                'normalization_rules': {}
            },
            'measurement_extraction': {
                'primary_patterns': [],
                'fallback_patterns': [],
                'normalization_rules': {}
            }
        }
        
        # Develop area extraction patterns
        area_data = frequency_data.get('area_units', {})
        if area_data:
            most_common_area = area_data.get('most_common', [])
            
            # Primary patterns for most common units
            for unit, count in most_common_area[:3]:
                if 'sqft' in unit or 'sq ft' in unit:
                    extraction_patterns['area_extraction']['primary_patterns'].append(
                        r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:sqft|sq\.?\s*ft|square\s*feet?)'
                    )
                elif 'yards' in unit:
                    extraction_patterns['area_extraction']['primary_patterns'].append(
                        r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:sq\.?\s*yards?|square\s*yards?)'
                    )
            
            # Normalization rules
            extraction_patterns['area_extraction']['normalization_rules'] = {
                'sq ft': 'sqft',
                'square feet': 'sqft',
                'sq.ft': 'sqft',
                'sq yards': 'sq_yards',
                'square yards': 'sq_yards'
            }
        
        # Develop price extraction patterns
        price_data = frequency_data.get('price_units', {})
        if price_data:
            most_common_price = price_data.get('most_common', [])
            
            # Primary patterns for most common units
            for unit, count in most_common_price[:3]:
                if 'lac' in unit or 'lakh' in unit:
                    extraction_patterns['price_extraction']['primary_patterns'].append(
                        r'₹\s*(\d+(?:\.\d+)?)\s*(?:lac|lakh)'
                    )
                elif 'cr' in unit or 'crore' in unit:
                    extraction_patterns['price_extraction']['primary_patterns'].append(
                        r'₹\s*(\d+(?:\.\d+)?)\s*(?:cr|crore)'
                    )
            
            # Normalization rules
            extraction_patterns['price_extraction']['normalization_rules'] = {
                'lakh': 'lac',
                'crore': 'cr'
            }
        
        self.research_results['extraction_patterns'] = extraction_patterns
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for research"""
        
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

    def _generate_standardization_recommendations(self):
        """Generate recommendations for unit standardization"""

        print("💡 Generating standardization recommendations...")

        recommendations = {
            'area_unit_standardization': [],
            'price_unit_standardization': [],
            'measurement_standardization': [],
            'parsing_improvements': [],
            'implementation_priorities': []
        }

        # Analyze area unit standardization needs
        area_patterns = self.research_results.get('unit_patterns_found', {}).get('area_units', {})

        if area_patterns:
            # Check for sqft variations
            sqft_variants = [unit for unit in area_patterns.keys() if 'sq' in unit and 'ft' in unit]
            if len(sqft_variants) > 1:
                recommendations['area_unit_standardization'].append({
                    'issue': 'multiple_sqft_formats',
                    'variants': sqft_variants,
                    'recommendation': 'Standardize all sqft variations to "sqft"',
                    'priority': 'high'
                })

            # Check for yards variations
            yards_variants = [unit for unit in area_patterns.keys() if 'yard' in unit]
            if len(yards_variants) > 1:
                recommendations['area_unit_standardization'].append({
                    'issue': 'multiple_yards_formats',
                    'variants': yards_variants,
                    'recommendation': 'Standardize all yards variations to "sq_yards"',
                    'priority': 'medium'
                })

        # Analyze price unit standardization needs
        price_patterns = self.research_results.get('unit_patterns_found', {}).get('price_units', {})

        if price_patterns:
            # Check for lac/lakh variations
            lac_variants = [unit for unit in price_patterns.keys() if 'lac' in unit or 'lakh' in unit]
            if len(lac_variants) > 1:
                recommendations['price_unit_standardization'].append({
                    'issue': 'lac_lakh_variations',
                    'variants': lac_variants,
                    'recommendation': 'Standardize lakh to "lac" for consistency',
                    'priority': 'high'
                })

            # Check for crore variations
            crore_variants = [unit for unit in price_patterns.keys() if 'cr' in unit or 'crore' in unit]
            if len(crore_variants) > 1:
                recommendations['price_unit_standardization'].append({
                    'issue': 'crore_variations',
                    'variants': crore_variants,
                    'recommendation': 'Standardize crore to "cr" for consistency',
                    'priority': 'high'
                })

        # Analyze parsing improvements needed
        challenges = self.research_results.get('parsing_challenges', {})
        common_issues = challenges.get('common_issues', {})

        for issue, count in common_issues.items():
            if count > 5:  # Issues occurring in more than 5 properties
                if issue == 'ambiguous_sq_unit':
                    recommendations['parsing_improvements'].append({
                        'issue': issue,
                        'frequency': count,
                        'recommendation': 'Improve regex patterns to handle ambiguous sq units',
                        'priority': 'high'
                    })
                elif issue == 'missing_currency_symbol':
                    recommendations['parsing_improvements'].append({
                        'issue': issue,
                        'frequency': count,
                        'recommendation': 'Add fallback patterns for prices without ₹ symbol',
                        'priority': 'medium'
                    })
                elif issue == 'multiple_area_measurements':
                    recommendations['parsing_improvements'].append({
                        'issue': issue,
                        'frequency': count,
                        'recommendation': 'Implement logic to prioritize super area over other measurements',
                        'priority': 'medium'
                    })

        # Generate implementation priorities
        frequency_data = self.research_results.get('unit_frequency_analysis', {})

        # Priority 1: Most common units
        area_freq = frequency_data.get('area_units', {})
        if area_freq:
            most_common_area = area_freq.get('most_common', [])[:2]
            recommendations['implementation_priorities'].append({
                'priority': 1,
                'category': 'area_units',
                'focus': 'most_common_units',
                'units': [unit for unit, count in most_common_area],
                'recommendation': 'Prioritize robust extraction for most common area units'
            })

        price_freq = frequency_data.get('price_units', {})
        if price_freq:
            most_common_price = price_freq.get('most_common', [])[:2]
            recommendations['implementation_priorities'].append({
                'priority': 1,
                'category': 'price_units',
                'focus': 'most_common_units',
                'units': [unit for unit, count in most_common_price],
                'recommendation': 'Prioritize robust extraction for most common price units'
            })

        # Priority 2: Standardization
        recommendations['implementation_priorities'].append({
            'priority': 2,
            'category': 'standardization',
            'focus': 'unit_normalization',
            'recommendation': 'Implement unit normalization rules for consistent output'
        })

        # Priority 3: Edge cases
        recommendations['implementation_priorities'].append({
            'priority': 3,
            'category': 'edge_cases',
            'focus': 'parsing_improvements',
            'recommendation': 'Handle edge cases and ambiguous formats'
        })

        self.research_results['standardization_recommendations'] = recommendations

    def _save_research_results(self):
        """Save research results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unit_type_variation_research_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.research_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Research results saved: {filename}")

        # Save summary report
        summary_filename = f"unit_variation_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("UNIT TYPE VARIATION RESEARCH SUMMARY\n")
            f.write("="*50 + "\n\n")

            f.write(f"Pages Analyzed: {self.research_results['pages_analyzed']}\n")
            f.write(f"Properties Analyzed: {self.research_results['properties_analyzed']}\n\n")

            # Unit patterns found
            f.write("UNIT PATTERNS FOUND:\n")
            f.write("-" * 25 + "\n")
            patterns = self.research_results.get('unit_patterns_found', {})

            for category, units in patterns.items():
                f.write(f"{category.upper()}:\n")
                for unit, count in list(units.items())[:5]:
                    f.write(f"  {unit}: {count} occurrences\n")
                f.write("\n")

            # Frequency analysis
            f.write("FREQUENCY ANALYSIS:\n")
            f.write("-" * 25 + "\n")
            frequency_data = self.research_results.get('unit_frequency_analysis', {})

            for category, data in frequency_data.items():
                f.write(f"{category.upper()}:\n")
                f.write(f"  Total occurrences: {data.get('total_occurrences', 0)}\n")
                f.write(f"  Unique units: {data.get('unique_units', 0)}\n")
                most_common = data.get('most_common', [])[:3]
                for unit, count in most_common:
                    percentage = data.get('percentages', {}).get(unit, 0)
                    f.write(f"  {unit}: {count} ({percentage:.1f}%)\n")
                f.write("\n")

            # Top recommendations
            f.write("TOP RECOMMENDATIONS:\n")
            f.write("-" * 25 + "\n")
            recommendations = self.research_results.get('standardization_recommendations', {})

            # High priority recommendations
            for category, recs in recommendations.items():
                if category != 'implementation_priorities':
                    high_priority = [r for r in recs if r.get('priority') == 'high']
                    for rec in high_priority[:2]:
                        f.write(f"- {rec['recommendation']}\n")

        print(f"📄 Summary report saved: {summary_filename}")

    def _print_research_summary(self):
        """Print comprehensive research summary"""

        print("\n📊 UNIT TYPE VARIATION RESEARCH SUMMARY")
        print("="*60)

        print(f"📄 Pages Analyzed: {self.research_results['pages_analyzed']}")
        print(f"🏠 Properties Analyzed: {self.research_results['properties_analyzed']}")

        # Unit patterns overview
        patterns = self.research_results.get('unit_patterns_found', {})
        print(f"\n📏 UNIT PATTERNS DISCOVERED:")

        for category, units in patterns.items():
            unique_units = len(units)
            total_occurrences = sum(units.values())
            print(f"   📊 {category.replace('_', ' ').title()}: {unique_units} unique units, {total_occurrences} total occurrences")

        # Most common units
        frequency_data = self.research_results.get('unit_frequency_analysis', {})

        if frequency_data:
            print(f"\n🔝 MOST COMMON UNITS:")

            for category, data in frequency_data.items():
                most_common = data.get('most_common', [])[:3]
                if most_common:
                    print(f"   📈 {category.replace('_', ' ').title()}:")
                    for unit, count in most_common:
                        percentage = data.get('percentages', {}).get(unit, 0)
                        print(f"      • {unit}: {count} occurrences ({percentage:.1f}%)")

        # Parsing challenges
        challenges = self.research_results.get('parsing_challenges', {})
        common_issues = challenges.get('common_issues', {})

        if common_issues:
            print(f"\n⚠️ PARSING CHALLENGES:")
            for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"   🔴 {issue.replace('_', ' ').title()}: {count} occurrences")

        # Standardization needs
        recommendations = self.research_results.get('standardization_recommendations', {})

        # Count high priority recommendations
        high_priority_count = 0
        for category, recs in recommendations.items():
            if category != 'implementation_priorities':
                high_priority_count += len([r for r in recs if r.get('priority') == 'high'])

        print(f"\n💡 STANDARDIZATION RECOMMENDATIONS:")
        print(f"   🔴 High Priority: {high_priority_count} recommendations")

        # Implementation priorities
        impl_priorities = recommendations.get('implementation_priorities', [])
        if impl_priorities:
            print(f"   📋 Implementation Phases: {len(impl_priorities)}")

        # Overall assessment
        total_units = sum(len(units) for units in patterns.values())

        if total_units > 15:
            print(f"\n🔴 HIGH COMPLEXITY: {total_units} unique unit variations require comprehensive standardization")
        elif total_units > 8:
            print(f"\n🟡 MODERATE COMPLEXITY: {total_units} unit variations need targeted improvements")
        else:
            print(f"\n🟢 LOW COMPLEXITY: {total_units} unit variations are manageable with current approach")


def main():
    """Main function for unit type variation research"""

    print("📏 Unit Type Variation Research Tool")
    print("Analyzing different area units, price units, and measurement standards...")
    print()

    try:
        # Initialize researcher
        researcher = UnitTypeVariationResearcher()

        # Run comprehensive research
        results = researcher.research_unit_type_variations()

        if 'error' not in results:
            print("\n✅ UNIT TYPE VARIATION RESEARCH COMPLETED SUCCESSFULLY!")

            properties_analyzed = results.get('properties_analyzed', 0)
            patterns = results.get('unit_patterns_found', {})
            total_units = sum(len(units) for units in patterns.values())

            print(f"🏠 Properties analyzed: {properties_analyzed}")
            print(f"📏 Unique unit variations: {total_units}")

            # Complexity assessment
            if total_units > 15:
                print(f"🔴 High complexity detected - comprehensive standardization needed")
            elif total_units > 8:
                print(f"🟡 Moderate complexity - targeted improvements recommended")
            else:
                print(f"🟢 Low complexity - current approach sufficient")

        else:
            print(f"\n❌ UNIT TYPE VARIATION RESEARCH FAILED: {results['error']}")

        return results

    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
