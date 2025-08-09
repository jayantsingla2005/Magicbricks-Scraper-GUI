#!/usr/bin/env python3
"""
Comprehensive Selector Validation & Mapping Tool
Validates current selectors against actual website structure and maps where data actually appears.
Focuses on improving low-completeness fields identified in previous testing.
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
from selenium.common.exceptions import TimeoutException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class SelectorValidationMapper:
    """
    Comprehensive tool for validating and mapping selectors against actual website structure
    """
    
    def __init__(self):
        """Initialize selector validation mapper"""
        
        # Load current selectors from scraper configuration
        self.current_selectors = self._load_current_selectors()
        
        # Fields with known low completeness that need improvement
        self.priority_fields = {
            'super_area': {'current_completeness': 49.6, 'target': 85.0},
            'society': {'current_completeness': 59.8, 'target': 85.0},
            'status': {'current_completeness': 79.3, 'target': 90.0}
        }
        
        # All fields to validate
        self.all_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'balconies', 'furnishing', 'floor', 'total_floors', 'age',
            'facing', 'parking', 'status', 'society', 'locality', 'city',
            'property_type', 'transaction_type', 'possession', 'property_url'
        ]
        
        # Validation results
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_analyzed': 0,
            'current_selector_performance': {},
            'field_analysis': {},
            'improved_selectors': {},
            'html_structure_analysis': {},
            'recommendations': []
        }
        
        print("🔍 Selector Validation & Mapping Tool Initialized")
        print(f"🎯 Priority Fields: {list(self.priority_fields.keys())}")
        print(f"📊 Total Fields to Validate: {len(self.all_fields)}")
    
    def _load_current_selectors(self) -> Dict[str, Any]:
        """Load current selectors from scraper configuration"""
        
        try:
            with open('config/scraper_config.json', 'r') as f:
                config = json.load(f)
                return config.get('selectors', {})
        except FileNotFoundError:
            print("⚠️ Config file not found, using default selectors")
            return self._get_default_selectors()
    
    def _get_default_selectors(self) -> Dict[str, Any]:
        """Get default selectors from main scraper"""
        
        return {
            'property_card': '.mb-srp__card',
            'title': '.mb-srp__card__title--link',
            'price': '.mb-srp__card__price--amount',
            'area': '.mb-srp__card__summary--value',
            'super_area': '.mb-srp__card__summary--value',
            'bedrooms': '.mb-srp__card__summary--value',
            'bathrooms': '.mb-srp__card__summary--value',
            'balconies': '.mb-srp__card__summary--value',
            'furnishing': '.mb-srp__card__summary--value',
            'floor': '.mb-srp__card__summary--value',
            'total_floors': '.mb-srp__card__summary--value',
            'age': '.mb-srp__card__summary--value',
            'facing': '.mb-srp__card__summary--value',
            'parking': '.mb-srp__card__summary--value',
            'status': '.mb-srp__card__summary--value',
            'society': '.mb-srp__card__society',
            'locality': '.mb-srp__card__ads--locality',
            'city': '.mb-srp__card__ads--locality',
            'property_type': '.mb-srp__card__summary--value',
            'transaction_type': '.mb-srp__card__summary--value',
            'possession': '.mb-srp__card__summary--value',
            'property_url': '.mb-srp__card__title--link'
        }
    
    def validate_selectors_comprehensive(self, num_pages: int = 5) -> Dict[str, Any]:
        """
        Perform comprehensive selector validation across multiple listing pages
        """
        
        print("\n🚀 Starting Comprehensive Selector Validation")
        print("="*60)
        
        try:
            # Step 1: Load and analyze listing pages
            print("📄 Step 1: Loading and Analyzing Listing Pages...")
            page_data = self._load_listing_pages(num_pages)
            
            if not page_data:
                print("❌ No listing pages could be loaded")
                return self.validation_results
            
            # Step 2: Test current selectors
            print("\n🧪 Step 2: Testing Current Selectors...")
            self._test_current_selectors(page_data)
            
            # Step 3: Analyze HTML structure for priority fields
            print("\n🔍 Step 3: Analyzing HTML Structure for Priority Fields...")
            self._analyze_html_structure(page_data)
            
            # Step 4: Develop improved selectors
            print("\n⚡ Step 4: Developing Improved Selectors...")
            self._develop_improved_selectors(page_data)
            
            # Step 5: Validate improved selectors
            print("\n✅ Step 5: Validating Improved Selectors...")
            self._validate_improved_selectors(page_data)
            
            # Step 6: Generate recommendations
            print("\n💡 Step 6: Generating Recommendations...")
            self._generate_recommendations()
            
            # Step 7: Save results
            print("\n💾 Step 7: Saving Validation Results...")
            self._save_validation_results()
            
            print("\n✅ Comprehensive Selector Validation Complete!")
            self._print_validation_summary()
            
            return self.validation_results
            
        except Exception as e:
            print(f"❌ Selector validation failed: {str(e)}")
            self.validation_results['error'] = str(e)
            return self.validation_results
    
    def _load_listing_pages(self, num_pages: int) -> List[Dict[str, Any]]:
        """Load multiple listing pages for analysis"""
        
        # Setup browser
        driver = self._setup_browser()
        page_data = []
        
        try:
            base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
            
            for page_num in range(1, num_pages + 1):
                try:
                    print(f"📄 Loading page {page_num}/{num_pages}...")
                    
                    # Navigate to page
                    url = f"{base_url}?page={page_num}" if page_num > 1 else base_url
                    driver.get(url)
                    
                    # Wait for page load
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Additional wait for dynamic content
                    time.sleep(3)
                    
                    # Get page source and parse
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Find property cards
                    property_cards = soup.find_all('div', class_=lambda x: x and 'mb-srp__card' in x)
                    
                    if property_cards:
                        page_data.append({
                            'page_number': page_num,
                            'url': url,
                            'soup': soup,
                            'property_cards': property_cards,
                            'card_count': len(property_cards)
                        })
                        
                        print(f"✅ Page {page_num}: Found {len(property_cards)} property cards")
                    else:
                        print(f"⚠️ Page {page_num}: No property cards found")
                    
                    # Delay between pages
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Error loading page {page_num}: {str(e)}")
        
        finally:
            driver.quit()
        
        self.validation_results['pages_analyzed'] = len(page_data)
        return page_data
    
    def _test_current_selectors(self, page_data: List[Dict[str, Any]]):
        """Test current selectors against real page data"""
        
        print("🧪 Testing current selectors against real data...")
        
        for field in self.all_fields:
            field_results = {
                'field_name': field,
                'selector': self.current_selectors.get(field, 'NOT_DEFINED'),
                'total_cards_tested': 0,
                'successful_extractions': 0,
                'failed_extractions': 0,
                'success_rate': 0,
                'sample_values': [],
                'common_issues': []
            }
            
            # Test selector across all pages and cards
            for page in page_data:
                for card in page['property_cards']:
                    field_results['total_cards_tested'] += 1
                    
                    try:
                        # Test current selector
                        selector = self.current_selectors.get(field)
                        if selector:
                            extracted_value = self._extract_with_selector(card, selector, field)
                            
                            if extracted_value and extracted_value.strip():
                                field_results['successful_extractions'] += 1
                                
                                # Store sample values (limit to 10)
                                if len(field_results['sample_values']) < 10:
                                    field_results['sample_values'].append(extracted_value.strip())
                            else:
                                field_results['failed_extractions'] += 1
                        else:
                            field_results['failed_extractions'] += 1
                            field_results['common_issues'].append('NO_SELECTOR_DEFINED')
                    
                    except Exception as e:
                        field_results['failed_extractions'] += 1
                        field_results['common_issues'].append(f'EXTRACTION_ERROR: {str(e)}')
            
            # Calculate success rate
            if field_results['total_cards_tested'] > 0:
                field_results['success_rate'] = (
                    field_results['successful_extractions'] / field_results['total_cards_tested'] * 100
                )
            
            self.validation_results['current_selector_performance'][field] = field_results
            
            # Print progress for priority fields
            if field in self.priority_fields:
                print(f"   🎯 {field}: {field_results['success_rate']:.1f}% success rate "
                      f"({field_results['successful_extractions']}/{field_results['total_cards_tested']})")
    
    def _extract_with_selector(self, card: Tag, selector: str, field: str) -> Optional[str]:
        """Extract value using selector with field-specific logic"""
        
        try:
            # Handle different selector types
            if selector.startswith('.'):
                # CSS class selector
                elements = card.find_all(class_=selector[1:])
            elif selector.startswith('#'):
                # ID selector
                elements = card.find_all(id=selector[1:])
            else:
                # Tag selector
                elements = card.find_all(selector)
            
            if not elements:
                return None
            
            # Field-specific extraction logic
            if field == 'property_url':
                # Extract href attribute
                for elem in elements:
                    href = elem.get('href')
                    if href:
                        return href
            elif field == 'title':
                # Extract text content
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            elif field == 'price':
                # Extract price text
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and ('₹' in text or 'lac' in text.lower() or 'cr' in text.lower()):
                        return text
            else:
                # Generic text extraction
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            
            return None
            
        except Exception:
            return None
    
    def _analyze_html_structure(self, page_data: List[Dict[str, Any]]):
        """Analyze HTML structure for priority fields to find where data actually appears"""
        
        print("🔍 Analyzing HTML structure for priority fields...")
        
        for field in self.priority_fields:
            print(f"   🎯 Analyzing {field}...")
            
            structure_analysis = {
                'field_name': field,
                'potential_locations': [],
                'common_patterns': [],
                'alternative_selectors': [],
                'data_samples': []
            }
            
            # Analyze first few cards from first page for detailed structure
            sample_cards = page_data[0]['property_cards'][:5] if page_data else []
            
            for i, card in enumerate(sample_cards):
                # Search for field-specific patterns in the card
                if field == 'super_area':
                    patterns = self._find_area_patterns(card)
                elif field == 'society':
                    patterns = self._find_society_patterns(card)
                elif field == 'status':
                    patterns = self._find_status_patterns(card)
                else:
                    patterns = []
                
                structure_analysis['potential_locations'].extend(patterns)
            
            # Identify common patterns
            location_counts = defaultdict(int)
            for location in structure_analysis['potential_locations']:
                location_counts[location['selector']] += 1
            
            # Sort by frequency
            common_patterns = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
            structure_analysis['common_patterns'] = [
                {'selector': selector, 'frequency': count}
                for selector, count in common_patterns[:5]
            ]
            
            self.validation_results['html_structure_analysis'][field] = structure_analysis
    
    def _find_area_patterns(self, card: Tag) -> List[Dict[str, Any]]:
        """Find patterns for area/super_area data"""
        
        patterns = []
        
        # Look for area-related text patterns
        area_keywords = ['sqft', 'sq ft', 'sq.ft', 'square feet', 'sq yards', 'sq.yards']
        
        # Search all text elements
        for elem in card.find_all(text=True):
            text = elem.strip().lower()
            if any(keyword in text for keyword in area_keywords):
                parent = elem.parent
                if parent:
                    patterns.append({
                        'selector': self._generate_selector(parent),
                        'text': elem.strip(),
                        'parent_tag': parent.name,
                        'parent_classes': parent.get('class', [])
                    })
        
        return patterns
    
    def _find_society_patterns(self, card: Tag) -> List[Dict[str, Any]]:
        """Find patterns for society/project name data"""
        
        patterns = []
        
        # Look for society/project indicators
        society_indicators = ['society', 'project', 'complex', 'residency', 'apartments', 'homes']
        
        # Search elements with society-related classes or text
        for elem in card.find_all():
            classes = ' '.join(elem.get('class', [])).lower()
            text = elem.get_text(strip=True).lower()
            
            if any(indicator in classes for indicator in society_indicators):
                patterns.append({
                    'selector': self._generate_selector(elem),
                    'text': elem.get_text(strip=True),
                    'classes': elem.get('class', []),
                    'tag': elem.name
                })
            elif any(indicator in text for indicator in society_indicators):
                patterns.append({
                    'selector': self._generate_selector(elem),
                    'text': elem.get_text(strip=True),
                    'classes': elem.get('class', []),
                    'tag': elem.name
                })
        
        return patterns
    
    def _find_status_patterns(self, card: Tag) -> List[Dict[str, Any]]:
        """Find patterns for status data"""
        
        patterns = []
        
        # Look for status indicators
        status_keywords = ['ready', 'under construction', 'new launch', 'resale', 'possession']
        
        # Search all elements for status-related content
        for elem in card.find_all():
            text = elem.get_text(strip=True).lower()
            classes = ' '.join(elem.get('class', [])).lower()
            
            if any(keyword in text for keyword in status_keywords):
                patterns.append({
                    'selector': self._generate_selector(elem),
                    'text': elem.get_text(strip=True),
                    'classes': elem.get('class', []),
                    'tag': elem.name
                })
            elif 'status' in classes or 'possession' in classes:
                patterns.append({
                    'selector': self._generate_selector(elem),
                    'text': elem.get_text(strip=True),
                    'classes': elem.get('class', []),
                    'tag': elem.name
                })
        
        return patterns
    
    def _generate_selector(self, element: Tag) -> str:
        """Generate CSS selector for an element"""
        
        try:
            # Try to generate a specific selector
            classes = element.get('class', [])
            if classes:
                return f".{'.'.join(classes)}"
            
            # Fallback to tag name
            return element.name
            
        except Exception:
            return 'unknown'
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for validation"""
        
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

    def _develop_improved_selectors(self, page_data: List[Dict[str, Any]]):
        """Develop improved selectors based on HTML structure analysis"""

        print("⚡ Developing improved selectors...")

        for field in self.priority_fields:
            print(f"   🎯 Developing improved selectors for {field}...")

            structure_analysis = self.validation_results['html_structure_analysis'].get(field, {})
            common_patterns = structure_analysis.get('common_patterns', [])

            improved_selectors = []

            if common_patterns:
                # Test top patterns as potential improved selectors
                for pattern in common_patterns[:3]:  # Test top 3 patterns
                    selector = pattern['selector']

                    # Test this selector across sample data
                    test_results = self._test_selector_candidate(page_data, selector, field)

                    if test_results['success_rate'] > self.priority_fields[field]['current_completeness']:
                        improved_selectors.append({
                            'selector': selector,
                            'success_rate': test_results['success_rate'],
                            'sample_values': test_results['sample_values'],
                            'improvement': test_results['success_rate'] - self.priority_fields[field]['current_completeness']
                        })

            # Sort by success rate
            improved_selectors.sort(key=lambda x: x['success_rate'], reverse=True)

            self.validation_results['improved_selectors'][field] = improved_selectors

            if improved_selectors:
                best = improved_selectors[0]
                print(f"   ✅ Best improved selector for {field}: {best['success_rate']:.1f}% "
                      f"(+{best['improvement']:.1f}% improvement)")
            else:
                print(f"   ⚠️ No improved selectors found for {field}")

    def _test_selector_candidate(self, page_data: List[Dict[str, Any]], selector: str, field: str) -> Dict[str, Any]:
        """Test a candidate selector against sample data"""

        results = {
            'selector': selector,
            'total_tested': 0,
            'successful_extractions': 0,
            'success_rate': 0,
            'sample_values': []
        }

        # Test across first 20 cards for efficiency
        cards_tested = 0
        for page in page_data:
            for card in page['property_cards']:
                if cards_tested >= 20:
                    break

                cards_tested += 1
                results['total_tested'] += 1

                try:
                    extracted_value = self._extract_with_selector(card, selector, field)

                    if extracted_value and extracted_value.strip():
                        results['successful_extractions'] += 1

                        if len(results['sample_values']) < 5:
                            results['sample_values'].append(extracted_value.strip())

                except Exception:
                    pass

            if cards_tested >= 20:
                break

        if results['total_tested'] > 0:
            results['success_rate'] = (results['successful_extractions'] / results['total_tested']) * 100

        return results

    def _validate_improved_selectors(self, page_data: List[Dict[str, Any]]):
        """Validate improved selectors against larger sample"""

        print("✅ Validating improved selectors...")

        for field in self.priority_fields:
            improved_selectors = self.validation_results['improved_selectors'].get(field, [])

            if improved_selectors:
                best_selector = improved_selectors[0]

                # Test against all available data
                validation_results = self._comprehensive_selector_test(page_data, best_selector['selector'], field)

                # Update with comprehensive results
                best_selector.update(validation_results)

                print(f"   ✅ {field}: {validation_results['success_rate']:.1f}% success rate "
                      f"({validation_results['successful_extractions']}/{validation_results['total_tested']})")

    def _comprehensive_selector_test(self, page_data: List[Dict[str, Any]], selector: str, field: str) -> Dict[str, Any]:
        """Comprehensive test of a selector against all available data"""

        results = {
            'selector': selector,
            'total_tested': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'success_rate': 0,
            'sample_values': [],
            'error_patterns': []
        }

        for page in page_data:
            for card in page['property_cards']:
                results['total_tested'] += 1

                try:
                    extracted_value = self._extract_with_selector(card, selector, field)

                    if extracted_value and extracted_value.strip():
                        results['successful_extractions'] += 1

                        if len(results['sample_values']) < 10:
                            results['sample_values'].append(extracted_value.strip())
                    else:
                        results['failed_extractions'] += 1

                except Exception as e:
                    results['failed_extractions'] += 1
                    results['error_patterns'].append(str(e))

        if results['total_tested'] > 0:
            results['success_rate'] = (results['successful_extractions'] / results['total_tested']) * 100

        return results

    def _generate_recommendations(self):
        """Generate recommendations based on validation results"""

        print("💡 Generating recommendations...")

        recommendations = []

        # Analyze current selector performance
        for field, performance in self.validation_results['current_selector_performance'].items():
            success_rate = performance['success_rate']

            if field in self.priority_fields:
                target_rate = self.priority_fields[field]['target']

                if success_rate < target_rate:
                    # Check if we have improved selectors
                    improved = self.validation_results['improved_selectors'].get(field, [])

                    if improved:
                        best_improved = improved[0]
                        recommendations.append({
                            'field': field,
                            'priority': 'high',
                            'current_rate': success_rate,
                            'target_rate': target_rate,
                            'recommended_action': 'replace_selector',
                            'current_selector': performance['selector'],
                            'improved_selector': best_improved['selector'],
                            'expected_improvement': best_improved['success_rate'] - success_rate,
                            'description': f"Replace selector for {field} to improve from {success_rate:.1f}% to {best_improved['success_rate']:.1f}%"
                        })
                    else:
                        recommendations.append({
                            'field': field,
                            'priority': 'high',
                            'current_rate': success_rate,
                            'target_rate': target_rate,
                            'recommended_action': 'investigate_further',
                            'description': f"Field {field} has low success rate ({success_rate:.1f}%) and needs further investigation"
                        })

            elif success_rate < 70:  # General threshold for non-priority fields
                recommendations.append({
                    'field': field,
                    'priority': 'medium',
                    'current_rate': success_rate,
                    'recommended_action': 'review_selector',
                    'description': f"Field {field} has moderate success rate ({success_rate:.1f}%) and could benefit from review"
                })

        # Overall recommendations
        total_fields = len(self.validation_results['current_selector_performance'])
        high_performing_fields = sum(1 for perf in self.validation_results['current_selector_performance'].values()
                                   if perf['success_rate'] >= 80)

        if high_performing_fields / total_fields >= 0.8:
            recommendations.append({
                'field': 'overall',
                'priority': 'low',
                'recommended_action': 'minor_optimizations',
                'description': f"Overall selector performance is good ({high_performing_fields}/{total_fields} fields >80%). Focus on priority field improvements."
            })
        else:
            recommendations.append({
                'field': 'overall',
                'priority': 'high',
                'recommended_action': 'comprehensive_review',
                'description': f"Overall selector performance needs improvement ({high_performing_fields}/{total_fields} fields >80%). Consider comprehensive selector review."
            })

        self.validation_results['recommendations'] = recommendations

    def _save_validation_results(self):
        """Save validation results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"selector_validation_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Validation results saved: {filename}")

    def _print_validation_summary(self):
        """Print comprehensive validation summary"""

        print("\n📊 SELECTOR VALIDATION SUMMARY")
        print("="*50)

        print(f"📄 Pages Analyzed: {self.validation_results['pages_analyzed']}")

        # Current selector performance
        print(f"\n🧪 CURRENT SELECTOR PERFORMANCE:")
        for field in self.priority_fields:
            if field in self.validation_results['current_selector_performance']:
                perf = self.validation_results['current_selector_performance'][field]
                target = self.priority_fields[field]['target']
                status = "✅" if perf['success_rate'] >= target else "❌"
                print(f"   {status} {field}: {perf['success_rate']:.1f}% (target: {target}%)")

        # Improved selectors
        print(f"\n⚡ IMPROVED SELECTORS:")
        for field in self.priority_fields:
            improved = self.validation_results['improved_selectors'].get(field, [])
            if improved:
                best = improved[0]
                improvement = best['success_rate'] - self.validation_results['current_selector_performance'][field]['success_rate']
                print(f"   ✅ {field}: {best['success_rate']:.1f}% (+{improvement:.1f}% improvement)")
            else:
                print(f"   ⚠️ {field}: No improvements found")

        # Top recommendations
        print(f"\n💡 TOP RECOMMENDATIONS:")
        high_priority_recs = [r for r in self.validation_results['recommendations'] if r.get('priority') == 'high']
        for i, rec in enumerate(high_priority_recs[:5], 1):
            print(f"   {i}. {rec['description']}")


def main():
    """Main function for selector validation"""

    print("🔍 Comprehensive Selector Validation & Mapping Tool")
    print("Validating current selectors and mapping data locations...")
    print()

    try:
        # Initialize validator
        validator = SelectorValidationMapper()

        # Run comprehensive validation
        results = validator.validate_selectors_comprehensive(num_pages=3)

        if 'error' not in results:
            print("\n✅ SELECTOR VALIDATION COMPLETED SUCCESSFULLY!")

            # Print key findings
            priority_improvements = 0
            for field in validator.priority_fields:
                improved = results['improved_selectors'].get(field, [])
                if improved:
                    priority_improvements += 1

            print(f"🎯 Priority field improvements found: {priority_improvements}/{len(validator.priority_fields)}")
            print(f"📊 Total recommendations generated: {len(results['recommendations'])}")

        else:
            print(f"\n❌ SELECTOR VALIDATION FAILED: {results['error']}")

        return results

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
