#!/usr/bin/env python3
"""
Advanced HTML Structure Analyzer
Deep analysis of current MagicBricks website structure to understand
how property data is organized and develop effective selectors.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict, Counter

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class HTMLStructureAnalyzer:
    """
    Advanced analyzer for understanding current MagicBricks HTML structure
    """
    
    def __init__(self):
        """Initialize HTML structure analyzer"""
        
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_analyzed': 0,
            'total_cards_analyzed': 0,
            'card_structure_patterns': {},
            'class_name_analysis': {},
            'data_location_mapping': {},
            'field_extraction_strategies': {},
            'recommended_selectors': {}
        }
        
        # Target fields for analysis
        self.target_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'society', 'locality', 'status', 'property_type'
        ]
        
        print("🔬 Advanced HTML Structure Analyzer Initialized")
        print(f"🎯 Target Fields: {', '.join(self.target_fields)}")
    
    def analyze_website_structure(self, num_pages: int = 2) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of current website structure
        """
        
        print("\n🚀 Starting Advanced HTML Structure Analysis")
        print("="*60)
        
        try:
            # Step 1: Load and capture raw HTML structure
            print("📄 Step 1: Loading and Capturing Raw HTML Structure...")
            raw_data = self._capture_raw_html_structure(num_pages)
            
            if not raw_data:
                print("❌ No data could be captured")
                return self.analysis_results
            
            # Step 2: Analyze card structure patterns
            print("\n🏗️ Step 2: Analyzing Card Structure Patterns...")
            self._analyze_card_structure_patterns(raw_data)
            
            # Step 3: Analyze class naming patterns
            print("\n🏷️ Step 3: Analyzing Class Naming Patterns...")
            self._analyze_class_naming_patterns(raw_data)
            
            # Step 4: Map data locations
            print("\n📍 Step 4: Mapping Data Locations...")
            self._map_data_locations(raw_data)
            
            # Step 5: Develop extraction strategies
            print("\n⚡ Step 5: Developing Extraction Strategies...")
            self._develop_extraction_strategies(raw_data)
            
            # Step 6: Generate recommended selectors
            print("\n🎯 Step 6: Generating Recommended Selectors...")
            self._generate_recommended_selectors()
            
            # Step 7: Save analysis results
            print("\n💾 Step 7: Saving Analysis Results...")
            self._save_analysis_results()
            
            print("\n✅ Advanced HTML Structure Analysis Complete!")
            self._print_analysis_summary()
            
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ HTML structure analysis failed: {str(e)}")
            self.analysis_results['error'] = str(e)
            return self.analysis_results
    
    def _capture_raw_html_structure(self, num_pages: int) -> List[Dict[str, Any]]:
        """Capture raw HTML structure from listing pages"""
        
        driver = self._setup_browser()
        raw_data = []
        
        try:
            base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
            
            for page_num in range(1, num_pages + 1):
                try:
                    print(f"📄 Capturing page {page_num}/{num_pages}...")
                    
                    # Navigate to page
                    url = f"{base_url}?page={page_num}" if page_num > 1 else base_url
                    driver.get(url)
                    
                    # Wait for page load
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Wait for dynamic content
                    time.sleep(5)
                    
                    # Get page source and parse
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Find potential property containers
                    potential_containers = self._find_potential_property_containers(soup)
                    
                    if potential_containers:
                        raw_data.append({
                            'page_number': page_num,
                            'url': url,
                            'soup': soup,
                            'containers': potential_containers,
                            'container_count': len(potential_containers)
                        })
                        
                        print(f"✅ Page {page_num}: Found {len(potential_containers)} potential property containers")
                    else:
                        print(f"⚠️ Page {page_num}: No property containers found")
                    
                    # Delay between pages
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"❌ Error capturing page {page_num}: {str(e)}")
        
        finally:
            driver.quit()
        
        self.analysis_results['pages_analyzed'] = len(raw_data)
        self.analysis_results['total_cards_analyzed'] = sum(data['container_count'] for data in raw_data)
        
        return raw_data
    
    def _find_potential_property_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """Find potential property containers using various strategies"""
        
        containers = []
        
        # Strategy 1: Look for common property-related class patterns
        property_patterns = [
            'card', 'property', 'listing', 'item', 'result', 'srp',
            'mb-srp', 'property-card', 'listing-card'
        ]
        
        for pattern in property_patterns:
            # Find elements with classes containing the pattern
            elements = soup.find_all(class_=lambda x: x and any(pattern in cls.lower() for cls in x))
            
            # Filter for elements that look like property containers
            for elem in elements:
                if self._looks_like_property_container(elem):
                    containers.append(elem)
        
        # Strategy 2: Look for repeated structures
        # Find divs that appear multiple times with similar structure
        all_divs = soup.find_all('div')
        class_counts = Counter()
        
        for div in all_divs:
            classes = div.get('class', [])
            if classes:
                class_signature = ' '.join(sorted(classes))
                class_counts[class_signature] += 1
        
        # Find classes that appear multiple times (likely property cards)
        for class_signature, count in class_counts.items():
            if count >= 10:  # Appears at least 10 times
                elements = soup.find_all('div', class_=class_signature.split())
                for elem in elements[:5]:  # Sample first 5
                    if self._looks_like_property_container(elem):
                        containers.append(elem)
        
        # Remove duplicates
        unique_containers = []
        seen_elements = set()
        
        for container in containers:
            element_id = id(container)
            if element_id not in seen_elements:
                seen_elements.add(element_id)
                unique_containers.append(container)
        
        return unique_containers[:50]  # Limit to first 50 for analysis
    
    def _looks_like_property_container(self, element: Tag) -> bool:
        """Check if an element looks like a property container"""
        
        # Check if element has reasonable size (contains multiple child elements)
        if len(element.find_all()) < 5:
            return False
        
        # Check for property-related text content
        text_content = element.get_text().lower()
        property_indicators = [
            '₹', 'bhk', 'sqft', 'sq ft', 'bedroom', 'bathroom',
            'apartment', 'house', 'villa', 'floor', 'plot',
            'gurgaon', 'sector', 'ready', 'under construction'
        ]
        
        indicator_count = sum(1 for indicator in property_indicators if indicator in text_content)
        
        # Should have at least 3 property indicators
        return indicator_count >= 3
    
    def _analyze_card_structure_patterns(self, raw_data: List[Dict[str, Any]]):
        """Analyze common structure patterns in property cards"""
        
        print("🏗️ Analyzing card structure patterns...")
        
        structure_patterns = defaultdict(int)
        tag_hierarchies = defaultdict(int)
        
        for page_data in raw_data:
            for container in page_data['containers'][:10]:  # Analyze first 10 per page
                # Analyze tag hierarchy
                hierarchy = self._get_tag_hierarchy(container)
                tag_hierarchies[hierarchy] += 1
                
                # Analyze class structure
                class_structure = self._get_class_structure(container)
                structure_patterns[class_structure] += 1
        
        # Find most common patterns
        common_hierarchies = sorted(tag_hierarchies.items(), key=lambda x: x[1], reverse=True)[:5]
        common_structures = sorted(structure_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        self.analysis_results['card_structure_patterns'] = {
            'common_tag_hierarchies': [{'pattern': pattern, 'count': count} for pattern, count in common_hierarchies],
            'common_class_structures': [{'pattern': pattern, 'count': count} for pattern, count in common_structures]
        }
    
    def _get_tag_hierarchy(self, element: Tag) -> str:
        """Get simplified tag hierarchy of an element"""
        
        tags = []
        for child in element.find_all():
            if child.name:
                tags.append(child.name)
        
        # Get unique tags in order
        unique_tags = []
        for tag in tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
        
        return ' > '.join(unique_tags[:10])  # Limit to first 10 levels
    
    def _get_class_structure(self, element: Tag) -> str:
        """Get simplified class structure of an element"""
        
        classes = []
        for child in element.find_all():
            child_classes = child.get('class', [])
            if child_classes:
                classes.extend(child_classes)
        
        # Get unique classes
        unique_classes = list(set(classes))
        
        # Sort and limit
        unique_classes.sort()
        return ' | '.join(unique_classes[:15])  # Limit to first 15 classes
    
    def _analyze_class_naming_patterns(self, raw_data: List[Dict[str, Any]]):
        """Analyze class naming patterns to understand naming conventions"""
        
        print("🏷️ Analyzing class naming patterns...")
        
        all_classes = []
        class_frequency = defaultdict(int)
        
        for page_data in raw_data:
            for container in page_data['containers']:
                for element in container.find_all():
                    classes = element.get('class', [])
                    for cls in classes:
                        all_classes.append(cls)
                        class_frequency[cls] += 1
        
        # Analyze naming patterns
        naming_patterns = {
            'prefixes': defaultdict(int),
            'suffixes': defaultdict(int),
            'separators': defaultdict(int),
            'common_words': defaultdict(int)
        }
        
        for cls in all_classes:
            # Analyze prefixes (first part before separator)
            if '__' in cls:
                prefix = cls.split('__')[0]
                naming_patterns['prefixes'][prefix] += 1
                naming_patterns['separators']['__'] += 1
            elif '--' in cls:
                prefix = cls.split('--')[0]
                naming_patterns['prefixes'][prefix] += 1
                naming_patterns['separators']['--'] += 1
            elif '-' in cls:
                prefix = cls.split('-')[0]
                naming_patterns['prefixes'][prefix] += 1
                naming_patterns['separators']['-'] += 1
            
            # Analyze common words
            words = re.findall(r'[a-zA-Z]+', cls)
            for word in words:
                if len(word) > 2:
                    naming_patterns['common_words'][word.lower()] += 1
        
        # Get top patterns
        top_patterns = {}
        for pattern_type, patterns in naming_patterns.items():
            top_patterns[pattern_type] = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        self.analysis_results['class_name_analysis'] = {
            'total_unique_classes': len(set(all_classes)),
            'most_frequent_classes': sorted(class_frequency.items(), key=lambda x: x[1], reverse=True)[:20],
            'naming_patterns': top_patterns
        }
    
    def _map_data_locations(self, raw_data: List[Dict[str, Any]]):
        """Map where different types of data actually appear in the HTML"""
        
        print("📍 Mapping data locations...")
        
        data_locations = {}
        
        for field in self.target_fields:
            print(f"   🎯 Mapping {field}...")
            
            locations = self._find_field_locations(raw_data, field)
            data_locations[field] = locations
        
        self.analysis_results['data_location_mapping'] = data_locations
    
    def _find_field_locations(self, raw_data: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        """Find where a specific field's data appears in the HTML"""
        
        locations = {
            'potential_selectors': [],
            'text_patterns': [],
            'common_locations': [],
            'confidence_scores': {}
        }
        
        # Define field-specific search patterns
        search_patterns = self._get_field_search_patterns(field)
        
        # Search through containers
        for page_data in raw_data:
            for container in page_data['containers'][:5]:  # Analyze first 5 per page
                # Search for field data in this container
                field_elements = self._search_field_in_container(container, search_patterns)
                
                for element_info in field_elements:
                    locations['potential_selectors'].append(element_info)
        
        # Analyze patterns
        if locations['potential_selectors']:
            # Group by selector patterns
            selector_counts = defaultdict(int)
            for selector_info in locations['potential_selectors']:
                selector = selector_info['selector']
                selector_counts[selector] += 1
            
            # Get most common selectors
            common_selectors = sorted(selector_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            locations['common_locations'] = [
                {'selector': selector, 'frequency': count}
                for selector, count in common_selectors
            ]
        
        return locations
    
    def _get_field_search_patterns(self, field: str) -> Dict[str, List[str]]:
        """Get search patterns for a specific field"""
        
        patterns = {
            'title': {
                'text_patterns': ['bhk', 'apartment', 'house', 'villa', 'floor', 'plot'],
                'class_patterns': ['title', 'heading', 'name'],
                'tag_patterns': ['h1', 'h2', 'h3', 'a']
            },
            'price': {
                'text_patterns': ['₹', 'lac', 'lakh', 'cr', 'crore'],
                'class_patterns': ['price', 'amount', 'cost'],
                'tag_patterns': ['span', 'div']
            },
            'area': {
                'text_patterns': ['sqft', 'sq ft', 'sq.ft', 'square feet'],
                'class_patterns': ['area', 'size', 'sqft'],
                'tag_patterns': ['span', 'div']
            },
            'super_area': {
                'text_patterns': ['super', 'built', 'carpet', 'sqft'],
                'class_patterns': ['super', 'built', 'area'],
                'tag_patterns': ['span', 'div']
            },
            'bedrooms': {
                'text_patterns': ['bhk', 'bedroom', 'bed'],
                'class_patterns': ['bhk', 'bedroom', 'bed'],
                'tag_patterns': ['span', 'div']
            },
            'society': {
                'text_patterns': ['society', 'project', 'complex', 'residency'],
                'class_patterns': ['society', 'project', 'complex'],
                'tag_patterns': ['span', 'div', 'p']
            },
            'locality': {
                'text_patterns': ['sector', 'gurgaon', 'delhi', 'noida'],
                'class_patterns': ['locality', 'location', 'address'],
                'tag_patterns': ['span', 'div', 'p']
            },
            'status': {
                'text_patterns': ['ready', 'under construction', 'new launch', 'resale'],
                'class_patterns': ['status', 'possession', 'ready'],
                'tag_patterns': ['span', 'div']
            }
        }
        
        return patterns.get(field, {
            'text_patterns': [],
            'class_patterns': [],
            'tag_patterns': []
        })
    
    def _search_field_in_container(self, container: Tag, search_patterns: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Search for field data within a container"""
        
        found_elements = []
        
        # Search all elements in container
        for element in container.find_all():
            element_text = element.get_text(strip=True).lower()
            element_classes = ' '.join(element.get('class', [])).lower()
            element_tag = element.name.lower()
            
            # Check if element matches any patterns
            text_matches = sum(1 for pattern in search_patterns.get('text_patterns', []) 
                             if pattern.lower() in element_text)
            class_matches = sum(1 for pattern in search_patterns.get('class_patterns', []) 
                              if pattern.lower() in element_classes)
            tag_matches = sum(1 for pattern in search_patterns.get('tag_patterns', []) 
                            if pattern.lower() == element_tag)
            
            total_matches = text_matches + class_matches + tag_matches
            
            if total_matches > 0:
                # Generate selector for this element
                selector = self._generate_element_selector(element)
                
                found_elements.append({
                    'element': element,
                    'selector': selector,
                    'text': element_text[:100],  # First 100 chars
                    'classes': element.get('class', []),
                    'tag': element.name,
                    'match_score': total_matches,
                    'text_matches': text_matches,
                    'class_matches': class_matches,
                    'tag_matches': tag_matches
                })
        
        # Sort by match score
        found_elements.sort(key=lambda x: x['match_score'], reverse=True)
        
        return found_elements[:10]  # Return top 10 matches
    
    def _generate_element_selector(self, element: Tag) -> str:
        """Generate CSS selector for an element"""
        
        try:
            classes = element.get('class', [])
            if classes:
                # Use most specific class
                return f".{classes[0]}"
            
            # Fallback to tag name
            return element.name
            
        except Exception:
            return 'unknown'
    
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

    def _develop_extraction_strategies(self, raw_data: List[Dict[str, Any]]):
        """Develop extraction strategies based on data location analysis"""

        print("⚡ Developing extraction strategies...")

        strategies = {}

        for field in self.target_fields:
            field_locations = self.analysis_results['data_location_mapping'].get(field, {})
            common_locations = field_locations.get('common_locations', [])

            if common_locations:
                # Develop strategy based on most common location
                best_location = common_locations[0]

                strategy = {
                    'primary_selector': best_location['selector'],
                    'confidence': best_location['frequency'],
                    'fallback_selectors': [loc['selector'] for loc in common_locations[1:3]],
                    'extraction_method': self._determine_extraction_method(field),
                    'validation_patterns': self._get_validation_patterns(field)
                }
            else:
                strategy = {
                    'primary_selector': None,
                    'confidence': 0,
                    'fallback_selectors': [],
                    'extraction_method': 'text',
                    'validation_patterns': [],
                    'status': 'needs_investigation'
                }

            strategies[field] = strategy

        self.analysis_results['field_extraction_strategies'] = strategies

    def _determine_extraction_method(self, field: str) -> str:
        """Determine the best extraction method for a field"""

        if field == 'property_url':
            return 'href_attribute'
        elif field in ['title', 'society', 'locality']:
            return 'text_content'
        elif field in ['price', 'area', 'super_area']:
            return 'text_with_regex'
        else:
            return 'text_content'

    def _get_validation_patterns(self, field: str) -> List[str]:
        """Get validation patterns for a field"""

        patterns = {
            'price': [r'₹[\d,.]+(lac|lakh|cr|crore)', r'₹[\d,.]+'],
            'area': [r'\d+\s*(sqft|sq\.?ft|square feet)', r'\d+\s*sqft'],
            'super_area': [r'\d+\s*(sqft|sq\.?ft)', r'super.*\d+'],
            'bedrooms': [r'\d+\s*bhk', r'\d+\s*(bed|bedroom)'],
            'bathrooms': [r'\d+\s*(bath|bathroom)', r'\d+\s*bath'],
            'status': [r'(ready|under construction|new launch|resale)'],
            'property_url': [r'/[a-zA-Z0-9\-]+\-pdpid\-[a-zA-Z0-9]+']
        }

        return patterns.get(field, [])

    def _generate_recommended_selectors(self):
        """Generate recommended selectors based on analysis"""

        print("🎯 Generating recommended selectors...")

        recommended = {}

        for field in self.target_fields:
            strategy = self.analysis_results['field_extraction_strategies'].get(field, {})

            if strategy.get('primary_selector') and strategy.get('confidence', 0) > 0:
                recommended[field] = {
                    'selector': strategy['primary_selector'],
                    'method': strategy['extraction_method'],
                    'confidence': strategy['confidence'],
                    'fallbacks': strategy.get('fallback_selectors', []),
                    'validation': strategy.get('validation_patterns', [])
                }
            else:
                recommended[field] = {
                    'selector': None,
                    'method': 'manual_investigation_needed',
                    'confidence': 0,
                    'status': 'requires_manual_analysis'
                }

        self.analysis_results['recommended_selectors'] = recommended

    def _save_analysis_results(self):
        """Save analysis results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"html_structure_analysis_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Analysis results saved: {filename}")

        # Also save a simplified summary
        summary_filename = f"structure_analysis_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("HTML STRUCTURE ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")

            f.write(f"Pages Analyzed: {self.analysis_results['pages_analyzed']}\n")
            f.write(f"Total Cards Analyzed: {self.analysis_results['total_cards_analyzed']}\n\n")

            f.write("RECOMMENDED SELECTORS:\n")
            f.write("-" * 30 + "\n")
            for field, rec in self.analysis_results['recommended_selectors'].items():
                if rec['selector']:
                    f.write(f"{field}: {rec['selector']} (confidence: {rec['confidence']})\n")
                else:
                    f.write(f"{field}: NEEDS INVESTIGATION\n")

            f.write("\nCLASS NAME PATTERNS:\n")
            f.write("-" * 30 + "\n")
            class_analysis = self.analysis_results.get('class_name_analysis', {})
            frequent_classes = class_analysis.get('most_frequent_classes', [])[:10]
            for cls, count in frequent_classes:
                f.write(f"{cls}: {count} occurrences\n")

        print(f"📄 Summary saved: {summary_filename}")

    def _print_analysis_summary(self):
        """Print comprehensive analysis summary"""

        print("\n📊 HTML STRUCTURE ANALYSIS SUMMARY")
        print("="*50)

        print(f"📄 Pages Analyzed: {self.analysis_results['pages_analyzed']}")
        print(f"🏗️ Total Cards Analyzed: {self.analysis_results['total_cards_analyzed']}")

        # Class analysis summary
        class_analysis = self.analysis_results.get('class_name_analysis', {})
        print(f"🏷️ Unique Classes Found: {class_analysis.get('total_unique_classes', 0)}")

        # Recommended selectors summary
        recommended = self.analysis_results.get('recommended_selectors', {})
        successful_fields = sum(1 for rec in recommended.values() if rec.get('selector'))

        print(f"\n🎯 RECOMMENDED SELECTORS:")
        print(f"   ✅ Fields with selectors: {successful_fields}/{len(self.target_fields)}")

        for field in self.target_fields:
            rec = recommended.get(field, {})
            if rec.get('selector'):
                confidence = rec.get('confidence', 0)
                status = "🟢" if confidence >= 5 else "🟡" if confidence >= 2 else "🔴"
                print(f"   {status} {field}: {rec['selector']} (confidence: {confidence})")
            else:
                print(f"   ❌ {field}: NEEDS INVESTIGATION")

        # Top class patterns
        print(f"\n🏷️ TOP CLASS PATTERNS:")
        frequent_classes = class_analysis.get('most_frequent_classes', [])[:5]
        for cls, count in frequent_classes:
            print(f"   📊 {cls}: {count} occurrences")

        # Naming patterns
        naming_patterns = class_analysis.get('naming_patterns', {})
        top_prefixes = naming_patterns.get('prefixes', [])[:3]
        if top_prefixes:
            print(f"\n🔤 TOP CLASS PREFIXES:")
            for prefix, count in top_prefixes:
                print(f"   📝 {prefix}: {count} occurrences")


def main():
    """Main function for HTML structure analysis"""

    print("🔬 Advanced HTML Structure Analyzer")
    print("Deep analysis of current MagicBricks website structure...")
    print()

    try:
        # Initialize analyzer
        analyzer = HTMLStructureAnalyzer()

        # Run comprehensive analysis
        results = analyzer.analyze_website_structure(num_pages=2)

        if 'error' not in results:
            print("\n✅ HTML STRUCTURE ANALYSIS COMPLETED SUCCESSFULLY!")

            # Print key findings
            recommended = results.get('recommended_selectors', {})
            successful_fields = sum(1 for rec in recommended.values() if rec.get('selector'))

            print(f"🎯 Fields with recommended selectors: {successful_fields}/{len(analyzer.target_fields)}")
            print(f"🏗️ Total property containers analyzed: {results['total_cards_analyzed']}")

        else:
            print(f"\n❌ HTML STRUCTURE ANALYSIS FAILED: {results['error']}")

        return results

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
