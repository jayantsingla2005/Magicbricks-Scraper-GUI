#!/usr/bin/env python3
"""
Comprehensive Property Research Tool
Expanded analysis across 50+ properties covering all property types, price ranges, and locations
to validate implementation across the full MagicBricks spectrum.
"""

import time
import json
import csv
import random
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
from selenium.common.exceptions import TimeoutException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup


class ComprehensivePropertyResearcher:
    """
    Comprehensive property research across diverse property types and characteristics
    """
    
    def __init__(self):
        """Initialize comprehensive property researcher"""
        
        # Expanded research configuration
        self.research_config = {
            'target_sample_size': 50,  # Minimum 50 properties
            'property_type_targets': {
                'apartment': 20,  # 2-3 BHK apartments (most common)
                'house': 10,     # Independent houses
                'plot': 8,       # Residential plots
                'villa': 7,      # Luxury villas
                'floor': 5       # Builder floors
            },
            'price_range_targets': {
                'budget': 15,    # <1 Crore
                'mid': 20,       # 1-3 Crore
                'premium': 15    # >3 Crore
            },
            'location_diversity_targets': {
                'gurgaon_sectors': 25,     # Various Gurgaon sectors
                'new_gurgaon': 10,         # New Gurgaon areas
                'dwarka_expressway': 8,    # Dwarka Expressway
                'sohna_road': 7            # Sohna Road corridor
            },
            'request_delay_range': (4.5, 6.0),  # Conservative delays for large sample
            'batch_size': 10,  # Process in batches
            'max_retries': 2
        }
        
        # Target data sections for validation
        self.target_sections = [
            'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
            'project_info', 'specifications', 'location_details', 'images'
        ]
        
        # Comprehensive research results
        self.research_results = {
            'metadata': {
                'start_time': None,
                'end_time': None,
                'total_properties_analyzed': 0,
                'successful_analyses': 0,
                'failed_analyses': 0,
                'research_config': self.research_config
            },
            'property_analyses': [],
            'type_analysis': {},
            'price_range_analysis': {},
            'location_analysis': {},
            'data_availability_by_type': {},
            'performance_metrics_by_type': {},
            'comprehensive_recommendations': []
        }
        
        print("🔬 Comprehensive Property Research Tool Initialized")
        print(f"🎯 Target: {self.research_config['target_sample_size']} properties across all types")
        print(f"🏠 Property Types: {list(self.research_config['property_type_targets'].keys())}")
        print(f"💰 Price Ranges: {list(self.research_config['price_range_targets'].keys())}")
    
    def conduct_comprehensive_research(self) -> Dict[str, Any]:
        """
        Conduct comprehensive property research across diverse property portfolio
        """
        
        print("\n🚀 Starting Comprehensive Property Research")
        print("="*70)
        
        self.research_results['metadata']['start_time'] = datetime.now()
        
        try:
            # Step 1: Load and categorize property URLs
            print("📊 Step 1: Loading and Categorizing Property URLs...")
            categorized_urls = self._load_and_categorize_properties()
            
            if not categorized_urls:
                print("❌ No property URLs available for comprehensive research")
                return self.research_results
            
            # Step 2: Validate sample diversity
            print("\n📈 Step 2: Validating Sample Diversity...")
            sample_validation = self._validate_sample_diversity(categorized_urls)
            
            # Step 3: Conduct comprehensive analysis
            print(f"\n🔍 Step 3: Analyzing {len(categorized_urls)} Diverse Properties...")
            self._analyze_diverse_properties(categorized_urls)
            
            # Step 4: Analyze by property type
            print("\n🏠 Step 4: Property Type Analysis...")
            self._analyze_by_property_type()
            
            # Step 5: Analyze by price range
            print("\n💰 Step 5: Price Range Analysis...")
            self._analyze_by_price_range()
            
            # Step 6: Analyze by location
            print("\n📍 Step 6: Location Analysis...")
            self._analyze_by_location()
            
            # Step 7: Cross-category validation
            print("\n🔄 Step 7: Cross-Category Validation...")
            self._cross_category_validation()
            
            # Step 8: Generate comprehensive recommendations
            print("\n💡 Step 8: Generating Comprehensive Recommendations...")
            self._generate_comprehensive_recommendations()
            
            # Finalize results
            self.research_results['metadata']['end_time'] = datetime.now()
            
            # Save comprehensive results
            self._save_comprehensive_results()
            
            print("\n✅ Comprehensive Property Research Complete!")
            self._print_comprehensive_summary()
            
            return self.research_results
            
        except Exception as e:
            print(f"❌ Comprehensive research failed: {str(e)}")
            self.research_results['metadata']['error'] = str(e)
            return self.research_results
    
    def _load_and_categorize_properties(self) -> List[Dict[str, Any]]:
        """Load properties from CSV and categorize by type, price, location"""
        
        # Load from existing CSV files
        all_properties = []
        
        # Look for CSV files
        import os
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'properties' in f.lower()]
        
        if not csv_files:
            print("❌ No CSV files found for property analysis")
            return []
        
        print(f"📄 Loading properties from {len(csv_files)} CSV files...")
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        if 'property_url' in row and row['property_url']:
                            url = row['property_url'].strip()
                            
                            if url.startswith('http') and 'magicbricks.com' in url:
                                # Categorize property
                                property_data = self._categorize_property(row)
                                if property_data:
                                    all_properties.append(property_data)
                
                print(f"✅ Loaded {len(all_properties)} properties from {csv_file}")
                
            except Exception as e:
                print(f"⚠️ Error reading {csv_file}: {str(e)}")
        
        # Select diverse sample
        diverse_sample = self._select_diverse_sample(all_properties)
        
        print(f"🎯 Selected {len(diverse_sample)} diverse properties for analysis")
        return diverse_sample
    
    def _categorize_property(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Categorize a property by type, price range, and location"""
        
        try:
            # Extract basic info
            title = row.get('title', '').lower()
            price_str = row.get('price', '')
            locality = row.get('locality', '')
            bedrooms = row.get('bedrooms', '')
            
            # Determine property type
            property_type = 'apartment'  # default
            if 'house' in title or 'independent' in title:
                property_type = 'house'
            elif 'plot' in title or 'land' in title:
                property_type = 'plot'
            elif 'villa' in title:
                property_type = 'villa'
            elif 'floor' in title or 'builder floor' in title:
                property_type = 'floor'
            
            # Determine price range
            price_range = 'mid'  # default
            if price_str:
                # Extract numeric price
                price_match = re.search(r'₹([\d.]+)\s*(lac|lakh|cr|crore)', price_str.lower())
                if price_match:
                    amount = float(price_match.group(1))
                    unit = price_match.group(2)
                    
                    # Convert to crores
                    if unit in ['lac', 'lakh']:
                        amount_cr = amount / 100
                    else:
                        amount_cr = amount
                    
                    if amount_cr < 1:
                        price_range = 'budget'
                    elif amount_cr > 3:
                        price_range = 'premium'
                    else:
                        price_range = 'mid'
            
            # Determine location category
            location_category = 'gurgaon_sectors'  # default
            if locality:
                locality_lower = locality.lower()
                if 'dwarka' in locality_lower or 'expressway' in locality_lower:
                    location_category = 'dwarka_expressway'
                elif 'sohna' in locality_lower:
                    location_category = 'sohna_road'
                elif any(sector in locality_lower for sector in ['sector 99', 'sector 100', 'sector 101', 'sector 102', 'sector 103', 'sector 104', 'sector 105']):
                    location_category = 'new_gurgaon'
            
            return {
                'url': row['property_url'],
                'title': row.get('title', ''),
                'price': price_str,
                'locality': locality,
                'bedrooms': bedrooms,
                'property_type': property_type,
                'price_range': price_range,
                'location_category': location_category,
                'source_row': row
            }
            
        except Exception as e:
            print(f"⚠️ Error categorizing property: {str(e)}")
            return None
    
    def _select_diverse_sample(self, all_properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select a diverse sample meeting target distributions"""
        
        # Group properties by categories
        by_type = defaultdict(list)
        by_price = defaultdict(list)
        by_location = defaultdict(list)
        
        for prop in all_properties:
            by_type[prop['property_type']].append(prop)
            by_price[prop['price_range']].append(prop)
            by_location[prop['location_category']].append(prop)
        
        print(f"📊 Available distribution:")
        print(f"   🏠 By Type: {dict((k, len(v)) for k, v in by_type.items())}")
        print(f"   💰 By Price: {dict((k, len(v)) for k, v in by_price.items())}")
        print(f"   📍 By Location: {dict((k, len(v)) for k, v in by_location.items())}")
        
        # Select diverse sample
        selected_properties = []
        used_urls = set()
        
        # Try to meet type targets
        for prop_type, target_count in self.research_config['property_type_targets'].items():
            available = by_type.get(prop_type, [])
            sample_size = min(target_count, len(available))
            
            if sample_size > 0:
                sample = random.sample(available, sample_size)
                for prop in sample:
                    if prop['url'] not in used_urls:
                        selected_properties.append(prop)
                        used_urls.add(prop['url'])
        
        # Fill remaining slots with any available properties
        remaining_target = self.research_config['target_sample_size'] - len(selected_properties)
        if remaining_target > 0:
            remaining_props = [p for p in all_properties if p['url'] not in used_urls]
            if remaining_props:
                additional_sample = random.sample(remaining_props, min(remaining_target, len(remaining_props)))
                selected_properties.extend(additional_sample)
        
        return selected_properties
    
    def _validate_sample_diversity(self, sample: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that the sample meets diversity requirements"""
        
        # Count distributions
        type_counts = defaultdict(int)
        price_counts = defaultdict(int)
        location_counts = defaultdict(int)
        
        for prop in sample:
            type_counts[prop['property_type']] += 1
            price_counts[prop['price_range']] += 1
            location_counts[prop['location_category']] += 1
        
        validation = {
            'total_sample_size': len(sample),
            'type_distribution': dict(type_counts),
            'price_distribution': dict(price_counts),
            'location_distribution': dict(location_counts),
            'diversity_score': self._calculate_diversity_score(type_counts, price_counts, location_counts)
        }
        
        print(f"✅ Sample Validation:")
        print(f"   📊 Total Sample: {validation['total_sample_size']}")
        print(f"   🏠 Type Distribution: {validation['type_distribution']}")
        print(f"   💰 Price Distribution: {validation['price_distribution']}")
        print(f"   📍 Location Distribution: {validation['location_distribution']}")
        print(f"   🎯 Diversity Score: {validation['diversity_score']:.2f}/1.0")
        
        return validation
    
    def _calculate_diversity_score(self, type_counts, price_counts, location_counts) -> float:
        """Calculate diversity score based on distribution evenness"""

        import math

        def entropy(counts):
            total = sum(counts.values())
            if total == 0:
                return 0
            return -sum((count/total) * math.log2(count/total) for count in counts.values() if count > 0)

        type_entropy = entropy(type_counts)
        price_entropy = entropy(price_counts)
        location_entropy = entropy(location_counts)

        # Normalize to 0-1 scale
        max_type_entropy = math.log2(len(self.research_config['property_type_targets'])) if len(self.research_config['property_type_targets']) > 1 else 1
        max_price_entropy = math.log2(len(self.research_config['price_range_targets'])) if len(self.research_config['price_range_targets']) > 1 else 1
        max_location_entropy = math.log2(len(self.research_config['location_diversity_targets'])) if len(self.research_config['location_diversity_targets']) > 1 else 1

        normalized_score = (
            (type_entropy / max_type_entropy if max_type_entropy > 0 else 0) +
            (price_entropy / max_price_entropy if max_price_entropy > 0 else 0) +
            (location_entropy / max_location_entropy if max_location_entropy > 0 else 0)
        ) / 3

        return normalized_score
    
    def _analyze_diverse_properties(self, properties: List[Dict[str, Any]]):
        """Analyze diverse properties with comprehensive data collection"""
        
        # Setup browser
        driver = self._setup_research_browser()
        
        try:
            batch_size = self.research_config['batch_size']
            total_properties = len(properties)
            
            for batch_start in range(0, total_properties, batch_size):
                batch_end = min(batch_start + batch_size, total_properties)
                batch_properties = properties[batch_start:batch_end]
                
                print(f"\n🔄 Processing batch {batch_start//batch_size + 1}: "
                      f"Properties {batch_start + 1}-{batch_end} of {total_properties}")
                
                for i, prop_data in enumerate(batch_properties, batch_start + 1):
                    try:
                        print(f"\n🔍 Analyzing property {i}/{total_properties}")
                        print(f"🏠 Type: {prop_data['property_type']} | 💰 Price: {prop_data['price_range']} | 📍 Location: {prop_data['location_category']}")
                        print(f"🌐 URL: {prop_data['url']}")
                        
                        # Analyze single property
                        analysis_result = self._analyze_single_comprehensive_property(driver, prop_data)
                        
                        # Store result
                        self.research_results['property_analyses'].append(analysis_result)
                        self.research_results['metadata']['successful_analyses'] += 1
                        
                        print(f"✅ Analysis complete - Sections found: {analysis_result.get('sections_found', 0)}/8")
                        
                    except Exception as e:
                        print(f"❌ Analysis failed: {str(e)}")
                        
                        # Store failed analysis
                        failed_analysis = {
                            'url': prop_data['url'],
                            'property_data': prop_data,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }
                        self.research_results['property_analyses'].append(failed_analysis)
                        self.research_results['metadata']['failed_analyses'] += 1
                    
                    # Delay between requests
                    if i < total_properties:
                        delay = random.uniform(*self.research_config['request_delay_range'])
                        print(f"⏱️ Waiting {delay:.1f}s before next request...")
                        time.sleep(delay)
                    
                    self.research_results['metadata']['total_properties_analyzed'] += 1
                
                # Longer delay between batches
                if batch_end < total_properties:
                    print(f"🔄 Batch {batch_start//batch_size + 1} complete. Taking extended break...")
                    time.sleep(10)
        
        finally:
            driver.quit()
    
    def _analyze_single_comprehensive_property(self, driver: webdriver.Chrome, 
                                             prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single property with comprehensive data collection"""
        
        url = prop_data['url']
        analysis_start = time.time()
        
        try:
            # Navigate to property page
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Comprehensive analysis
            analysis_result = {
                'url': url,
                'property_data': prop_data,
                'timestamp': datetime.now().isoformat(),
                'page_load_time': time.time() - analysis_start,
                'page_accessible': True,
                'page_size_kb': len(driver.page_source) / 1024,
                'data_sections_analysis': self._analyze_comprehensive_data_sections(soup),
                'structure_analysis': self._analyze_comprehensive_structure(soup),
                'content_quality_analysis': self._analyze_comprehensive_content_quality(soup),
                'extraction_complexity': self._assess_extraction_complexity(soup, prop_data),
                'sections_found': 0  # Will be calculated
            }
            
            # Calculate sections found
            analysis_result['sections_found'] = len([
                section for section, data in analysis_result['data_sections_analysis'].items()
                if data.get('found', False)
            ])
            
            # Set total analysis time
            analysis_result['total_analysis_time'] = time.time() - analysis_start
            
            return analysis_result
            
        except Exception as e:
            processing_time = time.time() - analysis_start
            
            return {
                'url': url,
                'property_data': prop_data,
                'timestamp': datetime.now().isoformat(),
                'page_accessible': False,
                'error': str(e),
                'processing_time': processing_time,
                'sections_found': 0
            }
    
    def _setup_research_browser(self) -> webdriver.Chrome:
        """Setup optimized browser for comprehensive research"""
        
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
        
        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _analyze_comprehensive_data_sections(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Comprehensive analysis of data sections availability"""
        
        sections = {}
        page_text = soup.get_text().lower()
        
        # Enhanced search patterns for each section
        enhanced_patterns = {
            'amenities': {
                'keywords': ['amenity', 'amenities', 'feature', 'facilities', 'club', 'gym', 'pool', 'garden', 'parking', 'security'],
                'class_patterns': ['amenity', 'feature', 'facility'],
                'content_indicators': ['swimming pool', 'gymnasium', 'clubhouse', 'garden', 'parking']
            },
            'floor_plan': {
                'keywords': ['floor', 'plan', 'layout', 'blueprint', 'room', 'bhk', 'configuration'],
                'class_patterns': ['floor', 'plan', 'layout'],
                'content_indicators': ['floor plan', 'room layout', 'bhk', 'bedroom', 'bathroom']
            },
            'neighborhood': {
                'keywords': ['nearby', 'locality', 'neighborhood', 'surrounding', 'schools', 'hospital', 'metro', 'connectivity'],
                'class_patterns': ['nearby', 'locality', 'connectivity'],
                'content_indicators': ['schools nearby', 'hospitals', 'metro station', 'connectivity']
            },
            'pricing_details': {
                'keywords': ['price', 'cost', 'payment', 'emi', 'charges', 'booking', 'registration', 'maintenance'],
                'class_patterns': ['price', 'cost', 'payment'],
                'content_indicators': ['price breakdown', 'emi', 'booking amount', 'maintenance charges']
            },
            'project_info': {
                'keywords': ['project', 'builder', 'developer', 'rera', 'possession', 'ready', 'construction'],
                'class_patterns': ['project', 'builder', 'developer'],
                'content_indicators': ['project details', 'builder name', 'rera number', 'possession date']
            },
            'specifications': {
                'keywords': ['specification', 'specs', 'details', 'construction', 'material', 'flooring', 'fittings'],
                'class_patterns': ['specification', 'specs', 'construction'],
                'content_indicators': ['specifications', 'construction details', 'flooring', 'fittings']
            },
            'location_details': {
                'keywords': ['location', 'address', 'map', 'coordinates', 'direction', 'landmark'],
                'class_patterns': ['location', 'address', 'map'],
                'content_indicators': ['location details', 'address', 'landmarks', 'directions']
            },
            'images': {
                'keywords': ['image', 'photo', 'gallery', 'picture', 'view'],
                'class_patterns': ['image', 'photo', 'gallery'],
                'content_indicators': ['photo gallery', 'images', 'property photos']
            }
        }
        
        for section_name, patterns in enhanced_patterns.items():
            section_analysis = {
                'found': False,
                'confidence_score': 0,
                'indicators_found': [],
                'content_samples': [],
                'extraction_complexity': 'medium'
            }
            
            confidence_score = 0
            
            # Check keywords in text
            keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in page_text)
            if keyword_matches > 0:
                confidence_score += min(keyword_matches * 10, 30)
                section_analysis['indicators_found'].append(f"keywords:{keyword_matches}")
            
            # Check class patterns
            for pattern in patterns['class_patterns']:
                elements = soup.find_all(class_=lambda x: x and pattern in x.lower())
                if elements:
                    confidence_score += 20
                    section_analysis['indicators_found'].append(f"classes:{pattern}")
                    
                    # Get content samples
                    for elem in elements[:2]:
                        content = elem.get_text(strip=True)[:100]
                        if content:
                            section_analysis['content_samples'].append(content)
            
            # Check content indicators
            content_matches = sum(1 for indicator in patterns['content_indicators'] if indicator in page_text)
            if content_matches > 0:
                confidence_score += min(content_matches * 15, 40)
                section_analysis['indicators_found'].append(f"content:{content_matches}")
            
            # Determine if section is found (confidence threshold: 25)
            section_analysis['found'] = confidence_score >= 25
            section_analysis['confidence_score'] = min(confidence_score, 100)
            
            # Assess extraction complexity
            if confidence_score >= 70:
                section_analysis['extraction_complexity'] = 'easy'
            elif confidence_score >= 40:
                section_analysis['extraction_complexity'] = 'medium'
            else:
                section_analysis['extraction_complexity'] = 'hard'
            
            sections[section_name] = section_analysis
        
        return sections
    
    def _analyze_comprehensive_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Comprehensive page structure analysis"""
        
        return {
            'total_elements': len(soup.find_all()),
            'div_count': len(soup.find_all('div')),
            'section_count': len(soup.find_all('section')),
            'image_count': len(soup.find_all('img')),
            'link_count': len(soup.find_all('a')),
            'form_count': len(soup.find_all('form')),
            'script_count': len(soup.find_all('script')),
            'table_count': len(soup.find_all('table')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'class_diversity': len(set([
                cls for elem in soup.find_all(class_=True) 
                for cls in elem.get('class', [])
            ])),
            'id_count': len([elem for elem in soup.find_all() if elem.get('id')]),
            'data_attribute_count': len([elem for elem in soup.find_all() if any(attr.startswith('data-') for attr in elem.attrs)]),
            'structured_data_present': bool(soup.find_all('script', type='application/ld+json')),
            'meta_property_count': len(soup.find_all('meta', property=True))
        }
    
    def _analyze_comprehensive_content_quality(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Comprehensive content quality analysis"""
        
        text_content = soup.get_text()
        
        return {
            'total_text_length': len(text_content),
            'word_count': len(text_content.split()),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'has_substantial_content': len(text_content.split()) > 200,
            'has_property_details': any(keyword in text_content.lower() for keyword in ['bhk', 'sqft', 'apartment', 'house', 'villa']),
            'has_contact_info': any(keyword in text_content.lower() for keyword in ['contact', 'phone', 'email', 'agent']),
            'has_price_info': any(keyword in text_content.lower() for keyword in ['₹', 'crore', 'lakh', 'price', 'cost']),
            'has_location_info': any(keyword in text_content.lower() for keyword in ['sector', 'gurgaon', 'delhi', 'noida']),
            'content_richness_score': self._calculate_content_richness(soup, text_content)
        }
    
    def _calculate_content_richness(self, soup: BeautifulSoup, text_content: str) -> float:
        """Calculate content richness score"""
        
        score = 0
        
        # Text content richness
        word_count = len(text_content.split())
        if word_count > 500:
            score += 20
        elif word_count > 200:
            score += 10
        
        # Structural richness
        if soup.find_all('table'):
            score += 15
        if soup.find_all(['ul', 'ol']):
            score += 10
        if soup.find_all('img'):
            score += 15
        
        # Property-specific content
        property_keywords = ['bhk', 'sqft', 'amenities', 'location', 'price', 'builder', 'project']
        keyword_matches = sum(1 for keyword in property_keywords if keyword in text_content.lower())
        score += min(keyword_matches * 5, 25)
        
        # Interactive elements
        if soup.find_all('form'):
            score += 10
        if soup.find_all('button'):
            score += 5
        
        return min(score, 100)
    
    def _assess_extraction_complexity(self, soup: BeautifulSoup, prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess extraction complexity for different property types"""
        
        complexity_factors = {
            'page_structure_complexity': 'medium',
            'dynamic_content_indicators': 0,
            'anti_scraping_indicators': 0,
            'data_organization_quality': 'good',
            'extraction_difficulty_score': 50  # 0-100, lower is easier
        }
        
        # Assess page structure complexity
        total_elements = len(soup.find_all())
        if total_elements > 2000:
            complexity_factors['page_structure_complexity'] = 'high'
            complexity_factors['extraction_difficulty_score'] += 20
        elif total_elements < 500:
            complexity_factors['page_structure_complexity'] = 'low'
            complexity_factors['extraction_difficulty_score'] -= 10
        
        # Check for dynamic content indicators
        scripts = soup.find_all('script')
        if len(scripts) > 10:
            complexity_factors['dynamic_content_indicators'] += 1
        
        # Check for anti-scraping indicators
        if soup.find_all(style=lambda x: x and 'display:none' in x):
            complexity_factors['anti_scraping_indicators'] += 1
        
        # Assess data organization
        structured_sections = len(soup.find_all(['section', 'article', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['section', 'block', 'container', 'content']
        )))
        
        if structured_sections > 5:
            complexity_factors['data_organization_quality'] = 'excellent'
            complexity_factors['extraction_difficulty_score'] -= 15
        elif structured_sections < 2:
            complexity_factors['data_organization_quality'] = 'poor'
            complexity_factors['extraction_difficulty_score'] += 15
        
        return complexity_factors

    def _analyze_by_property_type(self):
        """Analyze results by property type"""

        print("🏠 Analyzing results by property type...")

        successful_analyses = [
            analysis for analysis in self.research_results['property_analyses']
            if 'data_sections_analysis' in analysis
        ]

        type_analysis = {}

        for prop_type in self.research_config['property_type_targets'].keys():
            type_properties = [
                analysis for analysis in successful_analyses
                if analysis['property_data']['property_type'] == prop_type
            ]

            if type_properties:
                type_analysis[prop_type] = {
                    'count': len(type_properties),
                    'avg_sections_found': statistics.mean([p['sections_found'] for p in type_properties]),
                    'section_availability': {},
                    'avg_processing_time': statistics.mean([p.get('total_analysis_time', 0) for p in type_properties]),
                    'success_rate': len(type_properties) / len([
                        a for a in self.research_results['property_analyses']
                        if a.get('property_data', {}).get('property_type') == prop_type
                    ]) * 100
                }

                # Calculate section availability for this type
                for section in self.target_sections:
                    section_count = sum(1 for p in type_properties
                                      if p['data_sections_analysis'].get(section, {}).get('found', False))
                    type_analysis[prop_type]['section_availability'][section] = (section_count / len(type_properties)) * 100

        self.research_results['type_analysis'] = type_analysis

    def _analyze_by_price_range(self):
        """Analyze results by price range"""

        print("💰 Analyzing results by price range...")

        successful_analyses = [
            analysis for analysis in self.research_results['property_analyses']
            if 'data_sections_analysis' in analysis
        ]

        price_analysis = {}

        for price_range in self.research_config['price_range_targets'].keys():
            price_properties = [
                analysis for analysis in successful_analyses
                if analysis['property_data']['price_range'] == price_range
            ]

            if price_properties:
                price_analysis[price_range] = {
                    'count': len(price_properties),
                    'avg_sections_found': statistics.mean([p['sections_found'] for p in price_properties]),
                    'section_availability': {},
                    'avg_processing_time': statistics.mean([p.get('total_analysis_time', 0) for p in price_properties]),
                    'content_richness': statistics.mean([
                        p.get('content_quality_analysis', {}).get('content_richness_score', 0)
                        for p in price_properties
                    ])
                }

                # Calculate section availability for this price range
                for section in self.target_sections:
                    section_count = sum(1 for p in price_properties
                                      if p['data_sections_analysis'].get(section, {}).get('found', False))
                    price_analysis[price_range]['section_availability'][section] = (section_count / len(price_properties)) * 100

        self.research_results['price_range_analysis'] = price_analysis

    def _analyze_by_location(self):
        """Analyze results by location category"""

        print("📍 Analyzing results by location...")

        successful_analyses = [
            analysis for analysis in self.research_results['property_analyses']
            if 'data_sections_analysis' in analysis
        ]

        location_analysis = {}

        for location_cat in self.research_config['location_diversity_targets'].keys():
            location_properties = [
                analysis for analysis in successful_analyses
                if analysis['property_data']['location_category'] == location_cat
            ]

            if location_properties:
                location_analysis[location_cat] = {
                    'count': len(location_properties),
                    'avg_sections_found': statistics.mean([p['sections_found'] for p in location_properties]),
                    'section_availability': {},
                    'avg_processing_time': statistics.mean([p.get('total_analysis_time', 0) for p in location_properties])
                }

                # Calculate section availability for this location
                for section in self.target_sections:
                    section_count = sum(1 for p in location_properties
                                      if p['data_sections_analysis'].get(section, {}).get('found', False))
                    location_analysis[location_cat]['section_availability'][section] = (section_count / len(location_properties)) * 100

        self.research_results['location_analysis'] = location_analysis

    def _cross_category_validation(self):
        """Perform cross-category validation analysis"""

        print("🔄 Performing cross-category validation...")

        successful_analyses = [
            analysis for analysis in self.research_results['property_analyses']
            if 'data_sections_analysis' in analysis
        ]

        # Overall statistics
        overall_stats = {
            'total_analyzed': len(successful_analyses),
            'overall_avg_sections': statistics.mean([p['sections_found'] for p in successful_analyses]) if successful_analyses else 0,
            'overall_section_availability': {},
            'consistency_scores': {}
        }

        # Calculate overall section availability
        for section in self.target_sections:
            section_count = sum(1 for p in successful_analyses
                              if p['data_sections_analysis'].get(section, {}).get('found', False))
            overall_stats['overall_section_availability'][section] = (section_count / len(successful_analyses)) * 100 if successful_analyses else 0

        # Calculate consistency scores across categories
        type_availabilities = self.research_results.get('type_analysis', {})
        price_availabilities = self.research_results.get('price_range_analysis', {})

        for section in self.target_sections:
            # Type consistency
            type_rates = [data['section_availability'].get(section, 0) for data in type_availabilities.values()]
            type_consistency = 100 - (max(type_rates) - min(type_rates)) if type_rates else 0

            # Price consistency
            price_rates = [data['section_availability'].get(section, 0) for data in price_availabilities.values()]
            price_consistency = 100 - (max(price_rates) - min(price_rates)) if price_rates else 0

            overall_stats['consistency_scores'][section] = {
                'type_consistency': type_consistency,
                'price_consistency': price_consistency,
                'overall_consistency': (type_consistency + price_consistency) / 2
            }

        self.research_results['cross_category_validation'] = overall_stats

    def _generate_comprehensive_recommendations(self):
        """Generate comprehensive recommendations based on analysis"""

        print("💡 Generating comprehensive recommendations...")

        recommendations = []

        # Overall data availability recommendations
        overall_availability = self.research_results.get('cross_category_validation', {}).get('overall_section_availability', {})

        high_availability_sections = [
            section for section, rate in overall_availability.items() if rate > 80
        ]

        medium_availability_sections = [
            section for section, rate in overall_availability.items() if 50 <= rate <= 80
        ]

        low_availability_sections = [
            section for section, rate in overall_availability.items() if rate < 50
        ]

        if high_availability_sections:
            recommendations.append({
                'category': 'high_priority_extraction',
                'priority': 'critical',
                'recommendation': f"Prioritize extraction of high-availability sections: {', '.join(high_availability_sections)} (>80% availability)",
                'impact': 'high',
                'implementation_complexity': 'low'
            })

        if medium_availability_sections:
            recommendations.append({
                'category': 'medium_priority_extraction',
                'priority': 'high',
                'recommendation': f"Implement robust extraction for medium-availability sections: {', '.join(medium_availability_sections)} (50-80% availability)",
                'impact': 'medium',
                'implementation_complexity': 'medium'
            })

        if low_availability_sections:
            recommendations.append({
                'category': 'low_priority_extraction',
                'priority': 'medium',
                'recommendation': f"Consider alternative approaches for low-availability sections: {', '.join(low_availability_sections)} (<50% availability)",
                'impact': 'low',
                'implementation_complexity': 'high'
            })

        # Property type specific recommendations
        type_analysis = self.research_results.get('type_analysis', {})

        best_performing_type = max(type_analysis.items(), key=lambda x: x[1]['avg_sections_found']) if type_analysis else None
        worst_performing_type = min(type_analysis.items(), key=lambda x: x[1]['avg_sections_found']) if type_analysis else None

        if best_performing_type and worst_performing_type:
            recommendations.append({
                'category': 'property_type_optimization',
                'priority': 'high',
                'recommendation': f"Optimize extraction for {worst_performing_type[0]} properties (avg {worst_performing_type[1]['avg_sections_found']:.1f} sections) using patterns from {best_performing_type[0]} properties (avg {best_performing_type[1]['avg_sections_found']:.1f} sections)",
                'impact': 'high',
                'implementation_complexity': 'medium'
            })

        # Performance recommendations
        successful_count = self.research_results['metadata']['successful_analyses']
        total_count = self.research_results['metadata']['total_properties_analyzed']

        if total_count > 0:
            success_rate = (successful_count / total_count) * 100

            if success_rate >= 90:
                recommendations.append({
                    'category': 'performance_validation',
                    'priority': 'high',
                    'recommendation': f"Excellent success rate ({success_rate:.1f}%) validates production readiness for parallel processing implementation",
                    'impact': 'high',
                    'implementation_complexity': 'low'
                })
            elif success_rate >= 75:
                recommendations.append({
                    'category': 'performance_improvement',
                    'priority': 'medium',
                    'recommendation': f"Good success rate ({success_rate:.1f}%) but implement additional error handling for edge cases",
                    'impact': 'medium',
                    'implementation_complexity': 'medium'
                })
            else:
                recommendations.append({
                    'category': 'performance_critical',
                    'priority': 'critical',
                    'recommendation': f"Low success rate ({success_rate:.1f}%) requires investigation and optimization before production deployment",
                    'impact': 'critical',
                    'implementation_complexity': 'high'
                })

        # Consistency recommendations
        consistency_scores = self.research_results.get('cross_category_validation', {}).get('consistency_scores', {})

        inconsistent_sections = [
            section for section, scores in consistency_scores.items()
            if scores.get('overall_consistency', 100) < 70
        ]

        if inconsistent_sections:
            recommendations.append({
                'category': 'consistency_improvement',
                'priority': 'high',
                'recommendation': f"Improve extraction consistency for sections with high variance: {', '.join(inconsistent_sections)}",
                'impact': 'medium',
                'implementation_complexity': 'medium'
            })

        self.research_results['comprehensive_recommendations'] = recommendations

    def _save_comprehensive_results(self):
        """Save comprehensive research results"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON results
        json_filename = f"comprehensive_property_research_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.research_results, f, indent=2, ensure_ascii=False, default=str)

        # Save summary CSV
        csv_filename = f"comprehensive_research_summary_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)

            # Write summary data
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Properties Analyzed', self.research_results['metadata']['total_properties_analyzed']])
            writer.writerow(['Successful Analyses', self.research_results['metadata']['successful_analyses']])
            writer.writerow(['Failed Analyses', self.research_results['metadata']['failed_analyses']])

            # Write overall section availability
            writer.writerow([])
            writer.writerow(['Data Section', 'Overall Availability %'])
            overall_availability = self.research_results.get('cross_category_validation', {}).get('overall_section_availability', {})
            for section, rate in overall_availability.items():
                writer.writerow([section, f"{rate:.1f}%"])

            # Write type analysis
            writer.writerow([])
            writer.writerow(['Property Type', 'Count', 'Avg Sections Found', 'Success Rate %'])
            type_analysis = self.research_results.get('type_analysis', {})
            for prop_type, data in type_analysis.items():
                writer.writerow([prop_type, data['count'], f"{data['avg_sections_found']:.1f}", f"{data['success_rate']:.1f}%"])

        print(f"📁 Comprehensive research results saved:")
        print(f"   📄 Detailed results: {json_filename}")
        print(f"   📊 Summary: {csv_filename}")

    def _print_comprehensive_summary(self):
        """Print comprehensive research summary"""

        print("\n" + "="*70)
        print("📊 COMPREHENSIVE PROPERTY RESEARCH SUMMARY")
        print("="*70)

        metadata = self.research_results['metadata']
        print(f"🔍 Properties Analyzed: {metadata['total_properties_analyzed']}")
        print(f"✅ Successful: {metadata['successful_analyses']}")
        print(f"❌ Failed: {metadata['failed_analyses']}")

        if metadata['total_properties_analyzed'] > 0:
            success_rate = (metadata['successful_analyses'] / metadata['total_properties_analyzed']) * 100
            print(f"📈 Overall Success Rate: {success_rate:.1f}%")

        # Overall section availability
        overall_availability = self.research_results.get('cross_category_validation', {}).get('overall_section_availability', {})
        if overall_availability:
            print(f"\n📊 OVERALL DATA AVAILABILITY:")
            for section, rate in overall_availability.items():
                status = "🟢" if rate > 80 else "🟡" if rate > 50 else "🔴"
                print(f"   {status} {section}: {rate:.1f}%")

        # Property type analysis
        type_analysis = self.research_results.get('type_analysis', {})
        if type_analysis:
            print(f"\n🏠 PROPERTY TYPE ANALYSIS:")
            for prop_type, data in type_analysis.items():
                print(f"   📋 {prop_type}: {data['count']} properties, {data['avg_sections_found']:.1f} avg sections")

        # Price range analysis
        price_analysis = self.research_results.get('price_range_analysis', {})
        if price_analysis:
            print(f"\n💰 PRICE RANGE ANALYSIS:")
            for price_range, data in price_analysis.items():
                print(f"   💵 {price_range}: {data['count']} properties, {data['avg_sections_found']:.1f} avg sections")

        # Top recommendations
        recommendations = self.research_results.get('comprehensive_recommendations', [])
        if recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                priority_icon = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
                print(f"   {i}. {priority_icon} {rec['recommendation']}")


def main():
    """Main comprehensive research execution function"""

    print("🔬 Comprehensive MagicBricks Property Research Tool")
    print("Conducting expanded analysis across 50+ properties of all types...")
    print()

    try:
        # Initialize researcher
        researcher = ComprehensivePropertyResearcher()

        # Conduct comprehensive research
        results = researcher.conduct_comprehensive_research()

        if results['metadata']['successful_analyses'] > 0:
            print("\n✅ COMPREHENSIVE PROPERTY RESEARCH COMPLETED SUCCESSFULLY!")
            print("🎯 Comprehensive findings will inform production-ready implementation")
        else:
            print("\n⚠️ COMPREHENSIVE PROPERTY RESEARCH COMPLETED WITH ISSUES")
            print("📊 Review results for troubleshooting guidance")

        return results

    except Exception as e:
        print(f"❌ Comprehensive property research failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
