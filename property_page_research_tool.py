#!/usr/bin/env python3
"""
Comprehensive Property Page Research Tool
Conducts deep analysis of individual MagicBricks property pages to understand structure,
data availability, performance characteristics, and anti-scraping patterns.
"""

import time
import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import statistics
import csv

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options

# BeautifulSoup for parsing
from bs4 import BeautifulSoup

# Add src directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.core.modern_scraper import ModernMagicBricksScraper
    from src.core.url_discovery_manager import URLDiscoveryManager
except ImportError:
    print("❌ Import error - ensure src modules are available")
    sys.exit(1)


class PropertyPageResearcher:
    """
    Comprehensive property page research and analysis tool
    """
    
    def __init__(self, config_path: str = "config/scraper_config.json"):
        """Initialize property page researcher"""
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Research settings
        self.research_config = {
            'sample_size': 15,  # Number of properties to analyze
            'property_types': ['apartment', 'house', 'plot', 'villa', 'floor'],
            'price_ranges': ['budget', 'mid', 'premium'],  # <1Cr, 1-3Cr, >3Cr
            'max_pages_to_discover': 5,  # Pages to scan for URLs
            'analysis_timeout': 30,  # Seconds per property page
            'delay_between_requests': (3, 7)  # Min, max delay in seconds
        }
        
        # Research results storage
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
            'structure_patterns': {},
            'data_availability': {},
            'performance_metrics': {},
            'anti_scraping_findings': {},
            'selector_validation': {},
            'recommendations': []
        }
        
        # Initialize URL discovery manager
        self.url_manager = URLDiscoveryManager()
        
        print("🔬 Property Page Research Tool Initialized")
        print(f"📊 Target sample size: {self.research_config['sample_size']} properties")
        print(f"🏠 Property types: {', '.join(self.research_config['property_types'])}")
    
    def conduct_comprehensive_research(self) -> Dict[str, Any]:
        """
        Conduct comprehensive property page research
        """
        
        print("\n🚀 Starting Comprehensive Property Page Research")
        print("="*60)
        
        self.research_results['metadata']['start_time'] = datetime.now().isoformat()
        
        try:
            # Step 1: Discover property URLs
            print("📡 Step 1: Discovering Property URLs...")
            property_urls = self._discover_sample_property_urls()
            
            if len(property_urls) < 5:
                print(f"⚠️ Warning: Only found {len(property_urls)} URLs, continuing with available sample")
            
            # Step 2: Analyze each property page
            print(f"\n🔍 Step 2: Analyzing {len(property_urls)} Property Pages...")
            self._analyze_property_pages(property_urls)
            
            # Step 3: Pattern analysis
            print("\n📊 Step 3: Analyzing Patterns and Structure...")
            self._analyze_structure_patterns()
            
            # Step 4: Data availability assessment
            print("\n📈 Step 4: Assessing Data Availability...")
            self._assess_data_availability()
            
            # Step 5: Performance analysis
            print("\n⚡ Step 5: Performance Analysis...")
            self._analyze_performance_metrics()
            
            # Step 6: Anti-scraping analysis
            print("\n🛡️ Step 6: Anti-Scraping Pattern Analysis...")
            self._analyze_anti_scraping_patterns()
            
            # Step 7: Selector validation
            print("\n🎯 Step 7: Selector Validation...")
            self._validate_selectors()
            
            # Step 8: Generate recommendations
            print("\n💡 Step 8: Generating Recommendations...")
            self._generate_recommendations()
            
            # Finalize results
            self.research_results['metadata']['end_time'] = datetime.now().isoformat()
            
            # Save results
            self._save_research_results()
            
            print("\n✅ Comprehensive Property Page Research Complete!")
            self._print_research_summary()
            
            return self.research_results
            
        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            self.research_results['metadata']['error'] = str(e)
            return self.research_results
    
    def _discover_sample_property_urls(self) -> List[str]:
        """Discover sample property URLs for analysis"""

        print("🔍 Discovering property URLs from listing pages...")

        # First try URL discovery manager
        try:
            discovery_result = self.url_manager.discover_urls_from_listings(
                start_page=1,
                max_pages=self.research_config['max_pages_to_discover'],
                session_id=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Get discovered URLs
            pending_urls = self.url_manager.get_pending_urls(
                limit=self.research_config['sample_size'] * 2
            )

            if pending_urls:
                property_urls = []
                for url_data in pending_urls:
                    url = url_data['url']
                    metadata = url_data.get('metadata', {})

                    property_urls.append({
                        'url': url,
                        'metadata': metadata,
                        'discovery_priority': url_data.get('priority', 2)
                    })

                property_urls = property_urls[:self.research_config['sample_size']]
                print(f"✅ Discovered {len(property_urls)} property URLs for analysis")
                return property_urls

        except Exception as e:
            print(f"⚠️ URL discovery failed: {str(e)}")

        # Fallback: Use manual sample URLs for research
        print("🔄 Using fallback sample URLs for research...")

        sample_urls = [
            {
                'url': 'https://www.magicbricks.com/propertydetail/3-bhk-apartment-dlf-phase-2-gurgaon/sample1',
                'metadata': {'listing_title': '3 BHK Apartment', 'listing_price': '₹2.5 Cr'},
                'discovery_priority': 1
            },
            {
                'url': 'https://www.magicbricks.com/property-detail/2-bhk-apartment-sector-45/sample2',
                'metadata': {'listing_title': '2 BHK Apartment', 'listing_price': '₹1.8 Cr'},
                'discovery_priority': 2
            }
        ]

        print(f"✅ Using {len(sample_urls)} fallback URLs for analysis")
        return sample_urls
    
    def _analyze_property_pages(self, property_urls: List[Dict[str, Any]]):
        """Analyze individual property pages"""
        
        # Setup browser for analysis
        driver = self._setup_research_browser()
        
        try:
            for i, url_data in enumerate(property_urls, 1):
                url = url_data['url']
                metadata = url_data.get('metadata', {})
                
                print(f"\n🔍 Analyzing property {i}/{len(property_urls)}: {url}")
                
                try:
                    # Analyze single property page
                    analysis_result = self._analyze_single_property_page(driver, url, metadata)
                    
                    # Store result
                    self.research_results['property_analyses'].append(analysis_result)
                    self.research_results['metadata']['successful_analyses'] += 1
                    
                    print(f"✅ Analysis complete - Data sections found: {analysis_result['data_sections_found']}")
                    
                except Exception as e:
                    print(f"❌ Analysis failed: {str(e)}")
                    
                    # Store failed analysis
                    failed_analysis = {
                        'url': url,
                        'metadata': metadata,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.research_results['property_analyses'].append(failed_analysis)
                    self.research_results['metadata']['failed_analyses'] += 1
                
                # Delay between requests
                if i < len(property_urls):  # Don't delay after last request
                    delay = time.uniform(*self.research_config['delay_between_requests'])
                    print(f"⏱️ Waiting {delay:.1f}s before next request...")
                    time.sleep(delay)
                
                self.research_results['metadata']['total_properties_analyzed'] += 1
        
        finally:
            driver.quit()
    
    def _analyze_single_property_page(self, driver: webdriver.Chrome, url: str, 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single property page comprehensively"""
        
        analysis_start = time.time()
        
        # Navigate to property page
        driver.get(url)
        
        # Wait for page load and measure timing
        page_load_start = time.time()
        self._wait_for_property_page_load(driver)
        page_load_time = time.time() - page_load_start
        
        # Get page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Comprehensive analysis
        analysis_result = {
            'url': url,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            'performance': {
                'page_load_time': page_load_time,
                'total_analysis_time': 0,  # Will be set at end
                'page_size_kb': len(driver.page_source) / 1024
            },
            'structure_analysis': self._analyze_page_structure(soup),
            'data_sections': self._analyze_data_sections(soup),
            'selector_tests': self._test_selectors_on_page(soup),
            'dynamic_content': self._analyze_dynamic_content(driver),
            'anti_scraping_indicators': self._detect_anti_scraping_measures(driver, soup),
            'data_sections_found': 0,  # Will be calculated
            'extraction_success_rate': 0.0  # Will be calculated
        }
        
        # Calculate summary metrics
        analysis_result['data_sections_found'] = len([
            section for section, data in analysis_result['data_sections'].items() 
            if data.get('found', False)
        ])
        
        successful_selectors = len([
            test for test in analysis_result['selector_tests'].values() 
            if test.get('found', False)
        ])
        total_selectors = len(analysis_result['selector_tests'])
        analysis_result['extraction_success_rate'] = (successful_selectors / total_selectors * 100) if total_selectors > 0 else 0
        
        # Set total analysis time
        analysis_result['performance']['total_analysis_time'] = time.time() - analysis_start
        
        return analysis_result
    
    def _setup_research_browser(self) -> webdriver.Chrome:
        """Setup optimized browser for research"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run headless for research
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
        chrome_options.add_argument(f'--user-agent={user_agents[0]}')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _wait_for_property_page_load(self, driver: webdriver.Chrome, timeout: int = 15):
        """Wait for property page to fully load"""
        
        try:
            # Wait for basic page structure
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Try to wait for specific property page elements
            try:
                WebDriverWait(driver, 5).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "amenities")),
                        EC.presence_of_element_located((By.CLASS_NAME, "features")),
                        EC.presence_of_element_located((By.CLASS_NAME, "property-details")),
                        EC.presence_of_element_located((By.CLASS_NAME, "specifications"))
                    )
                )
            except TimeoutException:
                # Continue if specific sections not found
                pass
                
        except TimeoutException:
            print(f"⚠️ Page load timeout for {driver.current_url}")
    
    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze overall page structure"""
        
        structure = {
            'total_elements': len(soup.find_all()),
            'div_count': len(soup.find_all('div')),
            'section_count': len(soup.find_all('section')),
            'class_diversity': len(set([
                cls for elem in soup.find_all(class_=True) 
                for cls in elem.get('class', [])
            ])),
            'main_containers': [],
            'potential_data_sections': []
        }
        
        # Find main containers
        main_containers = soup.find_all(['div', 'section'], class_=re.compile(r'(main|content|property|detail)', re.I))
        structure['main_containers'] = [
            {
                'tag': elem.name,
                'classes': elem.get('class', []),
                'id': elem.get('id', ''),
                'child_count': len(elem.find_all())
            }
            for elem in main_containers[:5]  # Limit to top 5
        ]
        
        # Find potential data sections
        data_keywords = ['amenity', 'feature', 'specification', 'detail', 'info', 'nearby', 'location', 'price', 'floor', 'plan']
        for keyword in data_keywords:
            elements = soup.find_all(class_=re.compile(keyword, re.I))
            if elements:
                structure['potential_data_sections'].append({
                    'keyword': keyword,
                    'count': len(elements),
                    'sample_classes': [elem.get('class', []) for elem in elements[:3]]
                })
        
        return structure
    
    def _analyze_data_sections(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze availability of different data sections"""
        
        sections = {
            'amenities': {'found': False, 'elements': [], 'content_sample': []},
            'floor_plan': {'found': False, 'elements': [], 'content_sample': []},
            'neighborhood': {'found': False, 'elements': [], 'content_sample': []},
            'pricing_details': {'found': False, 'elements': [], 'content_sample': []},
            'project_info': {'found': False, 'elements': [], 'content_sample': []},
            'specifications': {'found': False, 'elements': [], 'content_sample': []},
            'location_details': {'found': False, 'elements': [], 'content_sample': []},
            'additional_info': {'found': False, 'elements': [], 'content_sample': []}
        }
        
        # Search patterns for each section
        search_patterns = {
            'amenities': ['amenity', 'amenities', 'feature', 'facilities'],
            'floor_plan': ['floor', 'plan', 'layout', 'blueprint'],
            'neighborhood': ['nearby', 'locality', 'neighborhood', 'surrounding'],
            'pricing_details': ['price', 'cost', 'payment', 'emi', 'charges'],
            'project_info': ['project', 'builder', 'developer', 'rera'],
            'specifications': ['specification', 'specs', 'details', 'construction'],
            'location_details': ['location', 'address', 'map', 'coordinates'],
            'additional_info': ['overview', 'description', 'about', 'summary']
        }
        
        for section_name, patterns in search_patterns.items():
            section_elements = []
            
            for pattern in patterns:
                # Search by class names
                elements = soup.find_all(class_=re.compile(pattern, re.I))
                section_elements.extend(elements)
                
                # Search by text content
                text_elements = soup.find_all(text=re.compile(pattern, re.I))
                for text_elem in text_elements:
                    if text_elem.parent:
                        section_elements.append(text_elem.parent)
            
            if section_elements:
                sections[section_name]['found'] = True
                sections[section_name]['elements'] = len(section_elements)
                
                # Get content samples
                content_samples = []
                for elem in section_elements[:3]:  # Sample first 3
                    content = elem.get_text(strip=True)[:100]  # First 100 chars
                    if content:
                        content_samples.append(content)
                
                sections[section_name]['content_sample'] = content_samples
        
        return sections
    
    def _test_selectors_on_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Test current selectors against the page"""
        
        # Get selectors from detailed property extractor
        phase2_selectors = self.config.get('phase2', {}).get('selectors', {})
        
        selector_tests = {}
        
        for section_name, section_selectors in phase2_selectors.items():
            if isinstance(section_selectors, dict) and 'container' in section_selectors:
                container_selector = section_selectors['container']
                
                # Test container selector
                container_elements = soup.select(container_selector)
                
                selector_tests[f"{section_name}_container"] = {
                    'selector': container_selector,
                    'found': len(container_elements) > 0,
                    'count': len(container_elements),
                    'sample_content': [elem.get_text(strip=True)[:50] for elem in container_elements[:2]]
                }
                
                # Test sub-selectors if container found
                if container_elements and isinstance(section_selectors, dict):
                    for sub_key, sub_selector in section_selectors.items():
                        if sub_key != 'container' and isinstance(sub_selector, str):
                            sub_elements = container_elements[0].select(sub_selector)
                            
                            selector_tests[f"{section_name}_{sub_key}"] = {
                                'selector': sub_selector,
                                'found': len(sub_elements) > 0,
                                'count': len(sub_elements),
                                'sample_content': [elem.get_text(strip=True)[:30] for elem in sub_elements[:2]]
                            }
        
        return selector_tests
    
    def _analyze_dynamic_content(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Analyze dynamic content loading patterns"""
        
        dynamic_analysis = {
            'initial_load_complete': True,
            'lazy_loaded_images': 0,
            'ajax_requests_detected': False,
            'scroll_triggered_content': False,
            'javascript_required': False
        }
        
        try:
            # Check for lazy loading images
            images = driver.find_elements(By.TAG_NAME, 'img')
            lazy_images = [img for img in images if 'lazy' in img.get_attribute('class') or '']
            dynamic_analysis['lazy_loaded_images'] = len(lazy_images)
            
            # Test scroll-triggered content
            initial_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            final_height = driver.execute_script("return document.body.scrollHeight")
            
            dynamic_analysis['scroll_triggered_content'] = final_height > initial_height
            
            # Check for JavaScript dependency
            noscript_elements = driver.find_elements(By.TAG_NAME, 'noscript')
            dynamic_analysis['javascript_required'] = len(noscript_elements) > 0
            
        except Exception as e:
            dynamic_analysis['analysis_error'] = str(e)
        
        return dynamic_analysis
    
    def _detect_anti_scraping_measures(self, driver: webdriver.Chrome, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detect anti-scraping measures on the page"""
        
        anti_scraping = {
            'captcha_detected': False,
            'rate_limit_indicators': [],
            'bot_detection_scripts': False,
            'content_obfuscation': False,
            'unusual_redirects': False
        }
        
        try:
            # Check for CAPTCHA
            captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'bot-detection']
            page_text = soup.get_text().lower()
            
            for indicator in captcha_indicators:
                if indicator in page_text:
                    anti_scraping['captcha_detected'] = True
                    break
            
            # Check for rate limiting messages
            rate_limit_phrases = ['too many requests', 'rate limit', 'slow down', 'try again later']
            for phrase in rate_limit_phrases:
                if phrase in page_text:
                    anti_scraping['rate_limit_indicators'].append(phrase)
            
            # Check for bot detection scripts
            scripts = soup.find_all('script')
            bot_detection_keywords = ['bot', 'automation', 'webdriver', 'selenium']
            
            for script in scripts:
                script_content = script.get_text().lower()
                if any(keyword in script_content for keyword in bot_detection_keywords):
                    anti_scraping['bot_detection_scripts'] = True
                    break
            
            # Check for content obfuscation
            obfuscated_elements = soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden', re.I))
            anti_scraping['content_obfuscation'] = len(obfuscated_elements) > 10
            
            # Check for unusual redirects
            current_url = driver.current_url
            anti_scraping['unusual_redirects'] = 'error' in current_url or 'blocked' in current_url
            
        except Exception as e:
            anti_scraping['detection_error'] = str(e)
        
        return anti_scraping
    
    def _analyze_structure_patterns(self):
        """Analyze common structure patterns across properties"""
        
        print("📊 Analyzing structure patterns across all properties...")
        
        # Collect structure data from all analyses
        all_structures = [
            analysis['structure_analysis'] 
            for analysis in self.research_results['property_analyses']
            if 'structure_analysis' in analysis
        ]
        
        if not all_structures:
            return
        
        # Calculate averages and patterns
        self.research_results['structure_patterns'] = {
            'avg_total_elements': statistics.mean([s['total_elements'] for s in all_structures]),
            'avg_div_count': statistics.mean([s['div_count'] for s in all_structures]),
            'avg_class_diversity': statistics.mean([s['class_diversity'] for s in all_structures]),
            'common_container_classes': self._find_common_patterns([
                container['classes'] for s in all_structures 
                for container in s['main_containers']
            ]),
            'common_data_section_keywords': self._find_common_patterns([
                section['keyword'] for s in all_structures 
                for section in s['potential_data_sections']
            ])
        }
    
    def _assess_data_availability(self):
        """Assess data availability across all analyzed properties"""
        
        print("📈 Assessing data availability across all properties...")
        
        # Collect data section results
        all_data_sections = [
            analysis['data_sections'] 
            for analysis in self.research_results['property_analyses']
            if 'data_sections' in analysis
        ]
        
        if not all_data_sections:
            return
        
        # Calculate availability percentages
        section_availability = {}
        total_properties = len(all_data_sections)
        
        for section_name in ['amenities', 'floor_plan', 'neighborhood', 'pricing_details', 
                           'project_info', 'specifications', 'location_details', 'additional_info']:
            
            found_count = sum(1 for sections in all_data_sections if sections.get(section_name, {}).get('found', False))
            availability_percentage = (found_count / total_properties) * 100
            
            section_availability[section_name] = {
                'availability_percentage': availability_percentage,
                'found_in_properties': found_count,
                'total_properties': total_properties,
                'priority': 'high' if availability_percentage > 70 else 'medium' if availability_percentage > 30 else 'low'
            }
        
        self.research_results['data_availability'] = section_availability
    
    def _analyze_performance_metrics(self):
        """Analyze performance metrics across all properties"""
        
        print("⚡ Analyzing performance metrics...")
        
        # Collect performance data
        performance_data = [
            analysis['performance'] 
            for analysis in self.research_results['property_analyses']
            if 'performance' in analysis
        ]
        
        if not performance_data:
            return
        
        # Calculate performance statistics
        if performance_data:
            avg_load_time = statistics.mean([p['page_load_time'] for p in performance_data])
            self.research_results['performance_metrics'] = {
                'avg_page_load_time': avg_load_time,
                'max_page_load_time': max([p['page_load_time'] for p in performance_data]),
                'min_page_load_time': min([p['page_load_time'] for p in performance_data]),
                'avg_analysis_time': statistics.mean([p['total_analysis_time'] for p in performance_data]),
                'avg_page_size_kb': statistics.mean([p['page_size_kb'] for p in performance_data]),
                'recommended_delay': max(3, avg_load_time * 1.5),
                'parallel_processing_feasible': avg_load_time < 10
            }
        else:
            # Default values when no performance data available
            self.research_results['performance_metrics'] = {
                'avg_page_load_time': 0,
                'max_page_load_time': 0,
                'min_page_load_time': 0,
                'avg_analysis_time': 0,
                'avg_page_size_kb': 0,
                'recommended_delay': 5,
                'parallel_processing_feasible': True
            }
    
    def _analyze_anti_scraping_patterns(self):
        """Analyze anti-scraping patterns across properties"""
        
        print("🛡️ Analyzing anti-scraping patterns...")
        
        # Collect anti-scraping data
        anti_scraping_data = [
            analysis['anti_scraping_indicators'] 
            for analysis in self.research_results['property_analyses']
            if 'anti_scraping_indicators' in analysis
        ]
        
        if not anti_scraping_data:
            return
        
        total_properties = len(anti_scraping_data)
        
        self.research_results['anti_scraping_findings'] = {
            'captcha_frequency': sum(1 for data in anti_scraping_data if data.get('captcha_detected', False)) / total_properties,
            'rate_limit_indicators_found': sum(1 for data in anti_scraping_data if data.get('rate_limit_indicators', [])) / total_properties,
            'bot_detection_frequency': sum(1 for data in anti_scraping_data if data.get('bot_detection_scripts', False)) / total_properties,
            'content_obfuscation_frequency': sum(1 for data in anti_scraping_data if data.get('content_obfuscation', False)) / total_properties,
            'risk_level': 'low',  # Will be calculated
            'recommended_measures': []
        }
        
        # Calculate risk level
        risk_indicators = [
            self.research_results['anti_scraping_findings']['captcha_frequency'],
            self.research_results['anti_scraping_findings']['bot_detection_frequency'],
            self.research_results['anti_scraping_findings']['content_obfuscation_frequency']
        ]
        
        avg_risk = statistics.mean(risk_indicators)
        if avg_risk > 0.3:
            self.research_results['anti_scraping_findings']['risk_level'] = 'high'
        elif avg_risk > 0.1:
            self.research_results['anti_scraping_findings']['risk_level'] = 'medium'
        else:
            self.research_results['anti_scraping_findings']['risk_level'] = 'low'
    
    def _validate_selectors(self):
        """Validate current selectors against research findings"""
        
        print("🎯 Validating selectors...")
        
        # Collect selector test results
        all_selector_tests = [
            analysis['selector_tests'] 
            for analysis in self.research_results['property_analyses']
            if 'selector_tests' in analysis
        ]
        
        if not all_selector_tests:
            return
        
        # Calculate selector success rates
        selector_validation = {}
        total_properties = len(all_selector_tests)
        
        # Get all unique selectors tested
        all_selectors = set()
        for tests in all_selector_tests:
            all_selectors.update(tests.keys())
        
        for selector_name in all_selectors:
            success_count = sum(1 for tests in all_selector_tests if tests.get(selector_name, {}).get('found', False))
            success_rate = (success_count / total_properties) * 100
            
            selector_validation[selector_name] = {
                'success_rate': success_rate,
                'successful_properties': success_count,
                'total_properties': total_properties,
                'status': 'good' if success_rate > 70 else 'needs_improvement' if success_rate > 30 else 'poor'
            }
        
        self.research_results['selector_validation'] = selector_validation
    
    def _generate_recommendations(self):
        """Generate recommendations based on research findings"""
        
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Data availability recommendations
        high_availability_sections = [
            name for name, data in self.research_results['data_availability'].items()
            if data['priority'] == 'high'
        ]
        
        if high_availability_sections:
            recommendations.append({
                'category': 'data_prioritization',
                'priority': 'high',
                'recommendation': f"Focus on extracting {', '.join(high_availability_sections)} as they have >70% availability",
                'impact': 'high'
            })
        
        # Performance recommendations
        if self.research_results['performance_metrics']['parallel_processing_feasible']:
            recommendations.append({
                'category': 'parallel_processing',
                'priority': 'medium',
                'recommendation': f"Parallel processing feasible with {self.research_results['performance_metrics']['recommended_delay']:.1f}s delays",
                'impact': 'high'
            })
        
        # Selector recommendations
        poor_selectors = [
            name for name, data in self.research_results['selector_validation'].items()
            if data['status'] == 'poor'
        ]
        
        if poor_selectors:
            recommendations.append({
                'category': 'selector_improvement',
                'priority': 'high',
                'recommendation': f"Improve selectors for: {', '.join(poor_selectors[:3])}",
                'impact': 'high'
            })
        
        # Anti-scraping recommendations
        risk_level = self.research_results['anti_scraping_findings']['risk_level']
        if risk_level == 'high':
            recommendations.append({
                'category': 'anti_scraping',
                'priority': 'critical',
                'recommendation': "Implement advanced anti-detection measures due to high risk level",
                'impact': 'critical'
            })
        
        self.research_results['recommendations'] = recommendations
    
    def _find_common_patterns(self, pattern_lists: List[List[str]]) -> List[Tuple[str, int]]:
        """Find common patterns across multiple lists"""
        
        pattern_counts = {}
        for pattern_list in pattern_lists:
            for pattern in pattern_list:
                if isinstance(pattern, str):
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Return top 10 most common patterns
        return sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _save_research_results(self):
        """Save research results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comprehensive JSON results
        json_filename = f"property_page_research_results_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.research_results, f, indent=2, ensure_ascii=False)
        
        # Save summary CSV
        csv_filename = f"property_page_research_summary_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write summary data
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Properties Analyzed', self.research_results['metadata']['total_properties_analyzed']])
            writer.writerow(['Successful Analyses', self.research_results['metadata']['successful_analyses']])
            writer.writerow(['Failed Analyses', self.research_results['metadata']['failed_analyses']])
            
            # Write data availability
            writer.writerow([])
            writer.writerow(['Data Section', 'Availability %', 'Priority'])
            for section, data in self.research_results['data_availability'].items():
                writer.writerow([section, f"{data['availability_percentage']:.1f}%", data['priority']])
        
        print(f"📁 Research results saved:")
        print(f"   📄 Comprehensive results: {json_filename}")
        print(f"   📊 Summary: {csv_filename}")
    
    def _print_research_summary(self):
        """Print comprehensive research summary"""
        
        print("\n" + "="*60)
        print("📊 PROPERTY PAGE RESEARCH SUMMARY")
        print("="*60)
        
        metadata = self.research_results['metadata']
        print(f"🔍 Properties Analyzed: {metadata['total_properties_analyzed']}")
        print(f"✅ Successful: {metadata['successful_analyses']}")
        print(f"❌ Failed: {metadata['failed_analyses']}")
        print(f"📈 Success Rate: {(metadata['successful_analyses']/metadata['total_properties_analyzed']*100):.1f}%")
        
        print(f"\n📊 DATA AVAILABILITY:")
        for section, data in self.research_results['data_availability'].items():
            status = "🟢" if data['priority'] == 'high' else "🟡" if data['priority'] == 'medium' else "🔴"
            print(f"   {status} {section}: {data['availability_percentage']:.1f}%")
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        perf = self.research_results['performance_metrics']
        print(f"   📊 Avg Page Load: {perf['avg_page_load_time']:.2f}s")
        print(f"   📊 Recommended Delay: {perf['recommended_delay']:.1f}s")
        print(f"   🚀 Parallel Processing: {'✅ Feasible' if perf['parallel_processing_feasible'] else '❌ Not Recommended'}")
        
        print(f"\n🛡️ ANTI-SCRAPING ANALYSIS:")
        anti = self.research_results['anti_scraping_findings']
        print(f"   🎯 Risk Level: {anti['risk_level'].upper()}")
        print(f"   🤖 Bot Detection: {anti['bot_detection_frequency']*100:.1f}%")
        print(f"   🔒 CAPTCHA Frequency: {anti['captcha_frequency']*100:.1f}%")
        
        print(f"\n💡 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(self.research_results['recommendations'][:3], 1):
            priority_icon = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            print(f"   {i}. {priority_icon} {rec['recommendation']}")


def main():
    """Main research execution function"""
    
    print("🔬 MagicBricks Property Page Research Tool")
    print("Conducting comprehensive analysis of individual property pages...")
    print()
    
    try:
        # Initialize researcher
        researcher = PropertyPageResearcher()
        
        # Conduct comprehensive research
        results = researcher.conduct_comprehensive_research()
        
        if results['metadata']['successful_analyses'] > 0:
            print("\n✅ PROPERTY PAGE RESEARCH COMPLETED SUCCESSFULLY!")
            print("🎯 Research findings will inform parallel processing and data schema design")
        else:
            print("\n⚠️ PROPERTY PAGE RESEARCH COMPLETED WITH ISSUES")
            print("📊 Review results for troubleshooting guidance")
        
        return results
        
    except Exception as e:
        print(f"❌ Property page research failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
