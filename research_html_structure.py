#!/usr/bin/env python3
"""
Deep HTML Structure Analysis for MagicBricks Scraper
Systematic research to identify root causes of field extraction issues
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from src.core.modern_scraper import ModernMagicBricksScraper


class HTMLStructureResearcher:
    """
    Comprehensive HTML structure analysis for field extraction optimization
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.driver = None
        self.research_data = {
            'timestamp': datetime.now().isoformat(),
            'property_cards_analyzed': 0,
            'html_samples': [],
            'selector_analysis': {},
            'data_patterns': {},
            'property_type_patterns': defaultdict(list),
            'field_locations': defaultdict(list),
            'missing_data_analysis': defaultdict(int)
        }
    
    def _load_config(self):
        """Load scraper configuration"""
        with open('config/scraper_config.json', 'r') as f:
            return json.load(f)
    
    def _setup_browser(self):
        """Setup browser for research"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        print("🌐 Browser initialized for HTML structure research")
    
    def capture_property_card_html(self, max_cards=20):
        """Capture raw HTML of property cards for analysis"""
        print(f"\n📋 CAPTURING HTML STRUCTURE OF {max_cards} PROPERTY CARDS")
        print("=" * 60)
        
        try:
            # Navigate to first page
            url = self.config['website']['base_url']
            print(f"🔗 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for React to render
            time.sleep(5)
            
            # Find property cards
            property_cards = self.driver.find_elements(By.CSS_SELECTOR, self.config['selectors']['property_cards'])
            print(f"🏠 Found {len(property_cards)} property cards")
            
            cards_analyzed = 0
            for i, card in enumerate(property_cards[:max_cards], 1):
                try:
                    print(f"   📄 Analyzing card {i}/{min(max_cards, len(property_cards))}")
                    
                    # Get raw HTML
                    html_content = card.get_attribute('outerHTML')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract basic info for identification
                    title_elem = soup.select_one(self.config['selectors']['title'])
                    title = title_elem.get_text(strip=True) if title_elem else f"Property {i}"
                    
                    # Store HTML sample
                    html_sample = {
                        'card_index': i,
                        'title': title[:50] + "..." if len(title) > 50 else title,
                        'html_content': html_content,
                        'html_length': len(html_content),
                        'soup_structure': str(soup.prettify())[:1000] + "..." if len(str(soup.prettify())) > 1000 else str(soup.prettify())
                    }
                    
                    self.research_data['html_samples'].append(html_sample)
                    
                    # Analyze this card's structure
                    self._analyze_card_structure(soup, i, title)
                    
                    cards_analyzed += 1
                    
                except Exception as e:
                    print(f"   ❌ Error analyzing card {i}: {str(e)}")
                    continue
            
            self.research_data['property_cards_analyzed'] = cards_analyzed
            print(f"\n✅ Successfully analyzed {cards_analyzed} property cards")
            
        except Exception as e:
            print(f"❌ Error in HTML capture: {str(e)}")
            raise
    
    def _analyze_card_structure(self, soup, card_index, title):
        """Analyze individual card structure for patterns"""
        
        # Analyze area data patterns
        self._analyze_area_patterns(soup, card_index, title)
        
        # Analyze society/project patterns
        self._analyze_society_patterns(soup, card_index, title)
        
        # Analyze property type patterns
        self._analyze_property_type_patterns(soup, card_index, title)
        
        # Analyze all data attributes and classes
        self._analyze_data_attributes(soup, card_index)
    
    def _analyze_area_patterns(self, soup, card_index, title):
        """Deep analysis of area data patterns"""
        area_data = {
            'card_index': card_index,
            'title': title,
            'super_area_found': False,
            'carpet_area_found': False,
            'area_locations': [],
            'area_values': [],
            'sqft_mentions': []
        }
        
        # Check current selectors
        super_area_elem = soup.select_one(self.config['selectors']['area']['super_area'])
        if super_area_elem:
            area_data['super_area_found'] = True
            area_data['area_locations'].append(f"super_area_selector: {super_area_elem.get_text(strip=True)}")
        
        carpet_area_elem = soup.select_one(self.config['selectors']['area']['carpet_area'])
        if carpet_area_elem:
            area_data['carpet_area_found'] = True
            area_data['area_locations'].append(f"carpet_area_selector: {carpet_area_elem.get_text(strip=True)}")
        
        # Find ALL elements containing 'sqft'
        all_text = soup.get_text()
        sqft_matches = re.findall(r'(\d+(?:,\d+)*)\s*sqft', all_text, re.IGNORECASE)
        area_data['sqft_mentions'] = sqft_matches
        
        # Find all elements with area-related classes or data attributes
        area_elements = soup.find_all(attrs={'class': re.compile(r'area|sqft|size', re.I)})
        for elem in area_elements:
            if elem.get_text(strip=True):
                area_data['area_locations'].append(f"area_class: {elem.get('class')} = {elem.get_text(strip=True)}")
        
        # Find data-summary attributes
        summary_elements = soup.find_all(attrs={'data-summary': True})
        for elem in summary_elements:
            summary_type = elem.get('data-summary')
            if 'area' in summary_type.lower():
                area_data['area_locations'].append(f"data-summary-{summary_type}: {elem.get_text(strip=True)}")
        
        self.research_data['field_locations']['area'].append(area_data)
    
    def _analyze_society_patterns(self, soup, card_index, title):
        """Deep analysis of society/project name patterns"""
        society_data = {
            'card_index': card_index,
            'title': title,
            'society_found': False,
            'society_locations': [],
            'builder_mentions': [],
            'project_mentions': []
        }
        
        # Check current selector
        society_elem = soup.select_one(self.config['selectors']['society']['primary'])
        if society_elem:
            society_data['society_found'] = True
            society_data['society_locations'].append(f"primary_selector: {society_elem.get_text(strip=True)}")
        
        # Check fallback selectors
        for fallback in self.config['selectors']['society']['fallback']:
            elem = soup.select_one(fallback)
            if elem and elem.get_text(strip=True):
                society_data['society_locations'].append(f"fallback_{fallback}: {elem.get_text(strip=True)}")
        
        # Find all elements with society/project/builder related classes
        society_elements = soup.find_all(attrs={'class': re.compile(r'society|project|builder|name', re.I)})
        for elem in society_elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:  # Avoid empty or very short text
                society_data['society_locations'].append(f"society_class: {elem.get('class')} = {text}")
        
        self.research_data['field_locations']['society'].append(society_data)
    
    def _analyze_property_type_patterns(self, soup, card_index, title):
        """Analyze patterns by property type"""
        # Determine property type from title
        property_type = "Unknown"
        title_lower = title.lower()
        
        if 'apartment' in title_lower or 'flat' in title_lower:
            property_type = 'Apartment'
        elif 'builder floor' in title_lower or 'independent floor' in title_lower:
            property_type = 'Independent Floor'
        elif 'villa' in title_lower:
            property_type = 'Villa'
        elif 'plot' in title_lower or 'land' in title_lower:
            property_type = 'Plot'
        elif 'house' in title_lower:
            property_type = 'House'
        
        # Store structure pattern for this property type
        structure_info = {
            'card_index': card_index,
            'title': title,
            'classes': [elem.get('class', []) for elem in soup.find_all(class_=True)],
            'data_attributes': [elem.attrs for elem in soup.find_all(attrs={'data-summary': True})],
            'text_patterns': re.findall(r'\b\d+\s*(?:BHK|sqft|Cr|Lac|Floor|out of)\b', soup.get_text(), re.IGNORECASE)
        }
        
        self.research_data['property_type_patterns'][property_type].append(structure_info)
    
    def _analyze_data_attributes(self, soup, card_index):
        """Analyze all data attributes and CSS classes for patterns"""
        
        # Collect all unique classes
        all_classes = []
        for elem in soup.find_all(class_=True):
            all_classes.extend(elem.get('class', []))
        
        # Collect all data attributes
        data_attrs = {}
        for elem in soup.find_all(attrs=lambda x: any(k.startswith('data-') for k in x.keys()) if x else False):
            for attr, value in elem.attrs.items():
                if attr.startswith('data-'):
                    if attr not in data_attrs:
                        data_attrs[attr] = []
                    data_attrs[attr].append(value)
        
        # Store in research data
        if 'css_classes' not in self.research_data['selector_analysis']:
            self.research_data['selector_analysis']['css_classes'] = Counter()
        if 'data_attributes' not in self.research_data['selector_analysis']:
            self.research_data['selector_analysis']['data_attributes'] = defaultdict(Counter)
        
        self.research_data['selector_analysis']['css_classes'].update(all_classes)
        
        for attr, values in data_attrs.items():
            self.research_data['selector_analysis']['data_attributes'][attr].update(values)
    
    def analyze_selector_effectiveness(self):
        """Analyze how effective current selectors are"""
        print(f"\n🔍 ANALYZING SELECTOR EFFECTIVENESS")
        print("=" * 50)
        
        # Analyze area field patterns
        area_analysis = self._analyze_area_effectiveness()
        society_analysis = self._analyze_society_effectiveness()
        
        self.research_data['selector_analysis']['area_effectiveness'] = area_analysis
        self.research_data['selector_analysis']['society_effectiveness'] = society_analysis
        
        return area_analysis, society_analysis
    
    def _analyze_area_effectiveness(self):
        """Analyze area field extraction effectiveness"""
        area_data = self.research_data['field_locations']['area']
        total_cards = len(area_data)
        
        super_area_found = sum(1 for card in area_data if card['super_area_found'])
        carpet_area_found = sum(1 for card in area_data if card['carpet_area_found'])
        sqft_mentions = sum(1 for card in area_data if card['sqft_mentions'])
        
        analysis = {
            'total_cards': total_cards,
            'super_area_selector_success': super_area_found,
            'carpet_area_selector_success': carpet_area_found,
            'cards_with_sqft_data': sqft_mentions,
            'super_area_success_rate': (super_area_found / total_cards * 100) if total_cards > 0 else 0,
            'carpet_area_success_rate': (carpet_area_found / total_cards * 100) if total_cards > 0 else 0,
            'sqft_data_availability': (sqft_mentions / total_cards * 100) if total_cards > 0 else 0
        }
        
        print(f"📐 AREA FIELD ANALYSIS:")
        print(f"   Super Area Selector Success: {super_area_found}/{total_cards} ({analysis['super_area_success_rate']:.1f}%)")
        print(f"   Carpet Area Selector Success: {carpet_area_found}/{total_cards} ({analysis['carpet_area_success_rate']:.1f}%)")
        print(f"   Cards with SQFT Data: {sqft_mentions}/{total_cards} ({analysis['sqft_data_availability']:.1f}%)")
        
        return analysis
    
    def _analyze_society_effectiveness(self):
        """Analyze society field extraction effectiveness"""
        society_data = self.research_data['field_locations']['society']
        total_cards = len(society_data)
        
        primary_found = sum(1 for card in society_data if card['society_found'])
        fallback_found = sum(1 for card in society_data if len(card['society_locations']) > 1)
        any_society_data = sum(1 for card in society_data if card['society_locations'])
        
        analysis = {
            'total_cards': total_cards,
            'primary_selector_success': primary_found,
            'fallback_selector_success': fallback_found,
            'any_society_data_found': any_society_data,
            'primary_success_rate': (primary_found / total_cards * 100) if total_cards > 0 else 0,
            'overall_success_rate': (any_society_data / total_cards * 100) if total_cards > 0 else 0
        }
        
        print(f"🏢 SOCIETY FIELD ANALYSIS:")
        print(f"   Primary Selector Success: {primary_found}/{total_cards} ({analysis['primary_success_rate']:.1f}%)")
        print(f"   Any Society Data Found: {any_society_data}/{total_cards} ({analysis['overall_success_rate']:.1f}%)")
        
        return analysis
    
    def generate_research_report(self):
        """Generate comprehensive research report"""
        print(f"\n📊 GENERATING RESEARCH REPORT")
        print("=" * 50)
        
        # Save detailed research data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_file = f"output/html_structure_research_{timestamp}.json"
        
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(self.research_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Detailed research data saved to: {research_file}")
        
        # Generate summary report
        self._generate_summary_report()
        
        return research_file
    
    def _generate_summary_report(self):
        """Generate human-readable summary report"""
        print(f"\n📋 RESEARCH SUMMARY REPORT")
        print("=" * 60)
        
        print(f"🔬 Analysis Scope:")
        print(f"   Property Cards Analyzed: {self.research_data['property_cards_analyzed']}")
        print(f"   HTML Samples Captured: {len(self.research_data['html_samples'])}")
        
        # Property type distribution
        print(f"\n🏠 Property Type Distribution:")
        for prop_type, data in self.research_data['property_type_patterns'].items():
            print(f"   {prop_type}: {len(data)} cards")
        
        # Most common CSS classes
        if 'css_classes' in self.research_data['selector_analysis']:
            print(f"\n🎨 Most Common CSS Classes:")
            for class_name, count in self.research_data['selector_analysis']['css_classes'].most_common(10):
                print(f"   {class_name}: {count} occurrences")
        
        # Data attributes found
        if 'data_attributes' in self.research_data['selector_analysis']:
            print(f"\n📊 Data Attributes Found:")
            for attr in self.research_data['selector_analysis']['data_attributes'].keys():
                print(f"   {attr}")
    
    def run_comprehensive_research(self):
        """Run complete HTML structure research"""
        print("🔬 STARTING COMPREHENSIVE HTML STRUCTURE RESEARCH")
        print("=" * 80)
        
        try:
            # Setup browser
            self._setup_browser()
            
            # Capture HTML structure
            self.capture_property_card_html(max_cards=15)
            
            # Analyze selector effectiveness
            self.analyze_selector_effectiveness()
            
            # Generate research report
            research_file = self.generate_research_report()
            
            print(f"\n🎉 RESEARCH COMPLETED SUCCESSFULLY")
            print(f"📁 Research file: {research_file}")
            
            return research_file
            
        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            raise
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔧 Browser closed")


def main():
    """Main research function"""
    researcher = HTMLStructureResearcher()
    research_file = researcher.run_comprehensive_research()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Review research file: {research_file}")
    print(f"2. Analyze patterns and root causes")
    print(f"3. Implement targeted fixes based on findings")
    print(f"4. Test fixes and validate improvements")


if __name__ == "__main__":
    main()
