#!/usr/bin/env python3
"""
Direct Property Page Research Tool
Uses existing CSV data to get real property URLs and conduct comprehensive analysis.
"""

import time
import json
import re
import os
import csv
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options

# BeautifulSoup for parsing
from bs4 import BeautifulSoup


class DirectPropertyResearcher:
    """
    Direct property page research using existing CSV data
    """
    
    def __init__(self):
        """Initialize direct property researcher"""
        
        self.research_results = {
            'metadata': {
                'start_time': None,
                'end_time': None,
                'total_properties_analyzed': 0,
                'successful_analyses': 0,
                'failed_analyses': 0
            },
            'property_analyses': [],
            'data_availability_summary': {},
            'selector_effectiveness': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        print("🔬 Direct Property Page Research Tool Initialized")
    
    def conduct_research(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Conduct direct property page research using existing CSV data
        """
        
        print("\n🚀 Starting Direct Property Page Research")
        print("="*60)
        
        self.research_results['metadata']['start_time'] = datetime.now().isoformat()
        
        try:
            # Step 1: Get property URLs from existing CSV
            print("📄 Step 1: Loading Property URLs from CSV...")
            property_urls = self._load_property_urls_from_csv(sample_size)
            
            if not property_urls:
                print("❌ No property URLs found in CSV data")
                return self.research_results
            
            # Step 2: Analyze property pages
            print(f"\n🔍 Step 2: Analyzing {len(property_urls)} Property Pages...")
            self._analyze_property_pages_direct(property_urls)
            
            # Step 3: Analyze results
            print("\n📊 Step 3: Analyzing Research Results...")
            self._analyze_research_results()
            
            # Step 4: Generate recommendations
            print("\n💡 Step 4: Generating Recommendations...")
            self._generate_research_recommendations()
            
            # Finalize and save
            self.research_results['metadata']['end_time'] = datetime.now().isoformat()
            self._save_research_results()
            
            print("\n✅ Direct Property Page Research Complete!")
            self._print_research_summary()
            
            return self.research_results
            
        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            self.research_results['metadata']['error'] = str(e)
            return self.research_results
    
    def _load_property_urls_from_csv(self, sample_size: int) -> List[Dict[str, Any]]:
        """Load property URLs from existing CSV files"""
        
        property_urls = []
        
        # Look for CSV files in output directory
        csv_files = []
        if os.path.exists('output'):
            csv_files = [f for f in os.listdir('output') if f.endswith('.csv')]
        
        # Also check current directory
        csv_files.extend([f for f in os.listdir('.') if f.endswith('.csv') and 'properties' in f.lower()])
        
        print(f"📁 Found {len(csv_files)} CSV files to check")
        
        for csv_file in csv_files:
            try:
                print(f"📄 Reading {csv_file}...")
                
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        if 'property_url' in row and row['property_url']:
                            url = row['property_url'].strip()
                            
                            # Validate URL
                            if url.startswith('http') and 'magicbricks.com' in url:
                                property_urls.append({
                                    'url': url,
                                    'title': row.get('title', ''),
                                    'price': row.get('price', ''),
                                    'property_type': row.get('property_type', ''),
                                    'locality': row.get('locality', ''),
                                    'source_file': csv_file
                                })
                        
                        # Stop if we have enough URLs
                        if len(property_urls) >= sample_size * 2:
                            break
                
                print(f"✅ Loaded {len(property_urls)} URLs from {csv_file}")
                
            except Exception as e:
                print(f"⚠️ Error reading {csv_file}: {str(e)}")
        
        # Shuffle and limit to sample size
        if property_urls:
            random.shuffle(property_urls)
            property_urls = property_urls[:sample_size]
        
        print(f"🎯 Selected {len(property_urls)} URLs for analysis")
        return property_urls
    
    def _analyze_property_pages_direct(self, property_urls: List[Dict[str, Any]]):
        """Analyze property pages directly"""
        
        # Setup browser
        driver = self._setup_research_browser()
        
        try:
            for i, url_data in enumerate(property_urls, 1):
                url = url_data['url']
                
                print(f"\n🔍 Analyzing property {i}/{len(property_urls)}")
                print(f"🌐 URL: {url}")
                print(f"🏠 Title: {url_data.get('title', 'N/A')}")
                
                try:
                    # Analyze single property page
                    analysis_result = self._analyze_single_property_direct(driver, url_data)
                    
                    # Store result
                    self.research_results['property_analyses'].append(analysis_result)
                    self.research_results['metadata']['successful_analyses'] += 1
                    
                    print(f"✅ Analysis complete - Sections found: {analysis_result.get('sections_found', 0)}")
                    
                except Exception as e:
                    print(f"❌ Analysis failed: {str(e)}")
                    
                    # Store failed analysis
                    failed_analysis = {
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'url_data': url_data
                    }
                    self.research_results['property_analyses'].append(failed_analysis)
                    self.research_results['metadata']['failed_analyses'] += 1
                
                # Delay between requests
                if i < len(property_urls):
                    delay = random.uniform(3, 6)
                    print(f"⏱️ Waiting {delay:.1f}s before next request...")
                    time.sleep(delay)
                
                self.research_results['metadata']['total_properties_analyzed'] += 1
        
        finally:
            driver.quit()
    
    def _analyze_single_property_direct(self, driver: webdriver.Chrome, url_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single property page"""
        
        url = url_data['url']
        analysis_start = time.time()
        
        # Navigate to property page
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page load
        page_load_start = time.time()
        self._wait_for_page_load(driver)
        page_load_time = time.time() - page_load_start
        
        # Get page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Comprehensive analysis
        analysis_result = {
            'url': url,
            'url_data': url_data,
            'timestamp': datetime.now().isoformat(),
            'page_load_time': page_load_time,
            'page_accessible': True,
            'page_size_kb': len(driver.page_source) / 1024,
            'data_sections_analysis': self._analyze_data_sections_direct(soup),
            'structure_analysis': self._analyze_page_structure_direct(soup),
            'content_quality': self._assess_content_quality(soup),
            'extraction_opportunities': self._identify_extraction_opportunities(soup),
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
    
    def _setup_research_browser(self) -> webdriver.Chrome:
        """Setup browser for research"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _wait_for_page_load(self, driver: webdriver.Chrome, timeout: int = 15):
        """Wait for page to load"""
        
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Additional wait for dynamic content
        except TimeoutException:
            print(f"⚠️ Page load timeout")
    
    def _analyze_data_sections_direct(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze data sections availability"""
        
        sections = {
            'amenities': {'found': False, 'indicators': [], 'content_sample': ''},
            'floor_plan': {'found': False, 'indicators': [], 'content_sample': ''},
            'neighborhood': {'found': False, 'indicators': [], 'content_sample': ''},
            'pricing_details': {'found': False, 'indicators': [], 'content_sample': ''},
            'project_info': {'found': False, 'indicators': [], 'content_sample': ''},
            'specifications': {'found': False, 'indicators': [], 'content_sample': ''},
            'location_details': {'found': False, 'indicators': [], 'content_sample': ''},
            'images': {'found': False, 'indicators': [], 'content_sample': ''}
        }
        
        # Search patterns
        search_patterns = {
            'amenities': ['amenity', 'amenities', 'feature', 'facilities', 'club', 'gym', 'pool'],
            'floor_plan': ['floor', 'plan', 'layout', 'blueprint', 'room', 'bhk'],
            'neighborhood': ['nearby', 'locality', 'neighborhood', 'surrounding', 'schools', 'hospital'],
            'pricing_details': ['price', 'cost', 'payment', 'emi', 'charges', 'booking', 'registration'],
            'project_info': ['project', 'builder', 'developer', 'rera', 'possession', 'ready'],
            'specifications': ['specification', 'specs', 'details', 'construction', 'material', 'flooring'],
            'location_details': ['location', 'address', 'map', 'coordinates', 'direction'],
            'images': ['image', 'photo', 'gallery', 'picture']
        }
        
        page_text = soup.get_text().lower()
        
        for section_name, patterns in search_patterns.items():
            indicators = []
            content_samples = []
            
            for pattern in patterns:
                # Search in text content
                if pattern in page_text:
                    indicators.append(f"text:{pattern}")
                
                # Search in class names
                elements = soup.find_all(class_=re.compile(pattern, re.I))
                if elements:
                    indicators.append(f"class:{pattern}")
                    
                    # Get content sample
                    for elem in elements[:2]:
                        content = elem.get_text(strip=True)[:100]
                        if content:
                            content_samples.append(content)
            
            if indicators:
                sections[section_name]['found'] = True
                sections[section_name]['indicators'] = indicators
                sections[section_name]['content_sample'] = ' | '.join(content_samples[:2])
        
        return sections
    
    def _analyze_page_structure_direct(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page structure"""
        
        return {
            'total_elements': len(soup.find_all()),
            'div_count': len(soup.find_all('div')),
            'section_count': len(soup.find_all('section')),
            'image_count': len(soup.find_all('img')),
            'link_count': len(soup.find_all('a')),
            'form_count': len(soup.find_all('form')),
            'script_count': len(soup.find_all('script')),
            'has_main_content': bool(soup.find(['main', 'article']) or soup.find(class_=re.compile('main|content', re.I)))
        }
    
    def _assess_content_quality(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Assess content quality and completeness"""
        
        text_content = soup.get_text()
        
        return {
            'total_text_length': len(text_content),
            'word_count': len(text_content.split()),
            'has_substantial_content': len(text_content.split()) > 100,
            'has_property_details': any(keyword in text_content.lower() for keyword in ['bhk', 'sqft', 'apartment', 'house', 'villa']),
            'has_contact_info': any(keyword in text_content.lower() for keyword in ['contact', 'phone', 'email', 'agent']),
            'has_price_info': any(keyword in text_content.lower() for keyword in ['₹', 'crore', 'lakh', 'price', 'cost'])
        }
    
    def _identify_extraction_opportunities(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Identify specific extraction opportunities"""
        
        opportunities = {
            'structured_data': False,
            'json_ld': False,
            'meta_properties': [],
            'data_attributes': [],
            'api_endpoints': []
        }
        
        # Check for structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        opportunities['json_ld'] = len(json_ld_scripts) > 0
        
        # Check for meta properties
        meta_tags = soup.find_all('meta', property=True)
        opportunities['meta_properties'] = [tag.get('property') for tag in meta_tags[:5]]
        
        # Check for data attributes
        data_elements = soup.find_all(attrs={'data-price': True}) or soup.find_all(attrs={'data-id': True})
        opportunities['data_attributes'] = [elem.name for elem in data_elements[:5]]
        
        return opportunities
    
    def _analyze_research_results(self):
        """Analyze overall research results"""
        
        successful_analyses = [
            analysis for analysis in self.research_results['property_analyses']
            if 'data_sections_analysis' in analysis
        ]
        
        if not successful_analyses:
            return
        
        # Data availability summary
        section_availability = {}
        total_properties = len(successful_analyses)
        
        for section_name in ['amenities', 'floor_plan', 'neighborhood', 'pricing_details', 
                           'project_info', 'specifications', 'location_details', 'images']:
            
            found_count = sum(1 for analysis in successful_analyses 
                            if analysis['data_sections_analysis'].get(section_name, {}).get('found', False))
            
            availability_percentage = (found_count / total_properties) * 100
            
            section_availability[section_name] = {
                'availability_percentage': availability_percentage,
                'found_in_properties': found_count,
                'total_properties': total_properties,
                'priority': 'high' if availability_percentage > 70 else 'medium' if availability_percentage > 30 else 'low'
            }
        
        self.research_results['data_availability_summary'] = section_availability
        
        # Performance metrics
        load_times = [analysis['page_load_time'] for analysis in successful_analyses if 'page_load_time' in analysis]
        
        if load_times:
            self.research_results['performance_metrics'] = {
                'avg_page_load_time': statistics.mean(load_times),
                'max_page_load_time': max(load_times),
                'min_page_load_time': min(load_times),
                'recommended_delay': max(3, statistics.mean(load_times) * 1.5),
                'parallel_processing_feasible': statistics.mean(load_times) < 10
            }
    
    def _generate_research_recommendations(self):
        """Generate recommendations based on research"""
        
        recommendations = []
        
        # Data availability recommendations
        if self.research_results['data_availability_summary']:
            high_availability = [
                name for name, data in self.research_results['data_availability_summary'].items()
                if data['priority'] == 'high'
            ]
            
            if high_availability:
                recommendations.append({
                    'category': 'data_extraction',
                    'priority': 'high',
                    'recommendation': f"Focus on extracting: {', '.join(high_availability)} (>70% availability)",
                    'impact': 'high'
                })
            
            low_availability = [
                name for name, data in self.research_results['data_availability_summary'].items()
                if data['priority'] == 'low'
            ]
            
            if low_availability:
                recommendations.append({
                    'category': 'data_extraction',
                    'priority': 'medium',
                    'recommendation': f"Consider alternative approaches for: {', '.join(low_availability)} (<30% availability)",
                    'impact': 'medium'
                })
        
        # Performance recommendations
        if self.research_results['performance_metrics']:
            if self.research_results['performance_metrics']['parallel_processing_feasible']:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'recommendation': f"Parallel processing feasible with {self.research_results['performance_metrics']['recommended_delay']:.1f}s delays",
                    'impact': 'high'
                })
        
        self.research_results['recommendations'] = recommendations
    
    def _save_research_results(self):
        """Save research results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"direct_property_research_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.research_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Research results saved: {filename}")
    
    def _print_research_summary(self):
        """Print research summary"""
        
        print("\n" + "="*60)
        print("📊 DIRECT PROPERTY PAGE RESEARCH SUMMARY")
        print("="*60)
        
        metadata = self.research_results['metadata']
        print(f"🔍 Properties Analyzed: {metadata['total_properties_analyzed']}")
        print(f"✅ Successful: {metadata['successful_analyses']}")
        print(f"❌ Failed: {metadata['failed_analyses']}")
        
        if metadata['total_properties_analyzed'] > 0:
            success_rate = (metadata['successful_analyses'] / metadata['total_properties_analyzed']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.research_results['data_availability_summary']:
            print(f"\n📊 DATA AVAILABILITY:")
            for section, data in self.research_results['data_availability_summary'].items():
                status = "🟢" if data['priority'] == 'high' else "🟡" if data['priority'] == 'medium' else "🔴"
                print(f"   {status} {section}: {data['availability_percentage']:.1f}%")
        
        if self.research_results['performance_metrics']:
            print(f"\n⚡ PERFORMANCE:")
            perf = self.research_results['performance_metrics']
            print(f"   📊 Avg Load Time: {perf['avg_page_load_time']:.2f}s")
            print(f"   🚀 Parallel Processing: {'✅ Feasible' if perf['parallel_processing_feasible'] else '❌ Not Recommended'}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.research_results['recommendations'][:3], 1):
            print(f"   {i}. {rec['recommendation']}")


def main():
    """Main research function"""
    
    print("🔬 Direct Property Page Research Tool")
    print("Analyzing real property pages from existing data...")
    print()
    
    try:
        researcher = DirectPropertyResearcher()
        results = researcher.conduct_research(sample_size=10)
        
        if results['metadata']['successful_analyses'] > 0:
            print("\n✅ DIRECT PROPERTY PAGE RESEARCH COMPLETED!")
            print("🎯 Research findings available for Phase II planning")
        else:
            print("\n⚠️ RESEARCH COMPLETED WITH LIMITED SUCCESS")
            print("📊 Check results for troubleshooting")
        
        return results
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
