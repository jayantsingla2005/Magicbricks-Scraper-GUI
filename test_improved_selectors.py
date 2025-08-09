#!/usr/bin/env python3
"""
Test Improved Selectors
Comprehensive testing of improved selectors against real MagicBricks data
to validate extraction accuracy and completeness.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class ImprovedSelectorTester:
    """
    Comprehensive tester for improved selectors
    """
    
    def __init__(self):
        """Initialize improved selector tester"""
        
        # Load improved selector configuration
        self.config = self._load_improved_config()
        
        # Test results
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_tested': 0,
            'properties_tested': 0,
            'field_performance': {},
            'overall_performance': {},
            'comparison_with_old': {},
            'recommendations': []
        }
        
        # Target fields for testing
        self.target_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'society', 'locality', 'status', 'property_type', 'property_url'
        ]
        
        print("🧪 Improved Selector Tester Initialized")
        print(f"🎯 Testing {len(self.target_fields)} fields")
        print(f"⚡ Using improved selectors from analysis")
    
    def _load_improved_config(self) -> Dict[str, Any]:
        """Load improved selector configuration"""
        
        try:
            with open('config/improved_scraper_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Improved config not found, using default")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file not found"""
        
        return {
            'selectors': {
                'property_card': '.mb-srp__card',
                'title': '.mb-srp__card--title a',
                'price': '.mb-srp__card__price--amount',
                'area': '.mb-srp__card__price--size',
                'locality': '.mb-srp__card__ads--locality',
                'society': '.mb-srp__card__society',
                'status': '.mb-srp__card__summary__list--item',
                'property_url': '.mb-srp__card--title a'
            },
            'extraction_methods': {
                'title': 'text_content',
                'price': 'text_with_regex',
                'area': 'text_with_regex',
                'property_url': 'href_attribute'
            }
        }
    
    def test_improved_selectors(self, num_pages: int = 3) -> Dict[str, Any]:
        """
        Test improved selectors against real data
        """
        
        print("\n🚀 Starting Improved Selector Testing")
        print("="*60)
        
        try:
            # Step 1: Load test pages
            print("📄 Step 1: Loading Test Pages...")
            test_data = self._load_test_pages(num_pages)
            
            if not test_data:
                print("❌ No test data could be loaded")
                return self.test_results
            
            # Step 2: Test each field
            print("\n🧪 Step 2: Testing Field Extraction...")
            self._test_field_extraction(test_data)
            
            # Step 3: Analyze performance
            print("\n📊 Step 3: Analyzing Performance...")
            self._analyze_performance()
            
            # Step 4: Generate recommendations
            print("\n💡 Step 4: Generating Recommendations...")
            self._generate_recommendations()
            
            # Step 5: Save results
            print("\n💾 Step 5: Saving Test Results...")
            self._save_test_results()
            
            print("\n✅ Improved Selector Testing Complete!")
            self._print_test_summary()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Selector testing failed: {str(e)}")
            self.test_results['error'] = str(e)
            return self.test_results
    
    def _load_test_pages(self, num_pages: int) -> List[Dict[str, Any]]:
        """Load test pages for selector validation"""
        
        driver = self._setup_browser()
        test_data = []
        
        try:
            base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
            
            for page_num in range(1, num_pages + 1):
                try:
                    print(f"📄 Loading test page {page_num}/{num_pages}...")
                    
                    # Navigate to page
                    url = f"{base_url}?page={page_num}" if page_num > 1 else base_url
                    driver.get(url)
                    
                    # Wait for page load
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Wait for dynamic content
                    time.sleep(3)
                    
                    # Get page source and parse
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Find property cards using improved selector
                    card_selector = self.config['selectors'].get('property_card', '.mb-srp__card')
                    property_cards = soup.select(card_selector)
                    
                    if property_cards:
                        test_data.append({
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
        
        self.test_results['pages_tested'] = len(test_data)
        self.test_results['properties_tested'] = sum(data['card_count'] for data in test_data)
        
        return test_data
    
    def _test_field_extraction(self, test_data: List[Dict[str, Any]]):
        """Test extraction for each field"""
        
        print("🧪 Testing field extraction with improved selectors...")
        
        for field in self.target_fields:
            print(f"   🎯 Testing {field}...")
            
            field_results = {
                'field_name': field,
                'total_cards_tested': 0,
                'successful_extractions': 0,
                'failed_extractions': 0,
                'success_rate': 0,
                'sample_values': [],
                'extraction_issues': []
            }
            
            # Test field across all pages and cards
            for page_data in test_data:
                for card in page_data['property_cards']:
                    field_results['total_cards_tested'] += 1
                    
                    try:
                        # Extract using improved selector
                        extracted_value = self._extract_field_value(card, field)
                        
                        if extracted_value and extracted_value.strip():
                            field_results['successful_extractions'] += 1
                            
                            # Store sample values (limit to 10)
                            if len(field_results['sample_values']) < 10:
                                field_results['sample_values'].append(extracted_value.strip())
                        else:
                            field_results['failed_extractions'] += 1
                    
                    except Exception as e:
                        field_results['failed_extractions'] += 1
                        field_results['extraction_issues'].append(str(e))
            
            # Calculate success rate
            if field_results['total_cards_tested'] > 0:
                field_results['success_rate'] = (
                    field_results['successful_extractions'] / field_results['total_cards_tested'] * 100
                )
            
            self.test_results['field_performance'][field] = field_results
            
            print(f"      ✅ {field}: {field_results['success_rate']:.1f}% success rate "
                  f"({field_results['successful_extractions']}/{field_results['total_cards_tested']})")
    
    def _extract_field_value(self, card: Tag, field: str) -> Optional[str]:
        """Extract field value using improved selectors"""
        
        try:
            # Get selector and extraction method
            selector = self.config['selectors'].get(field)
            extraction_method = self.config['extraction_methods'].get(field, 'text_content')
            
            if not selector:
                return None
            
            # Handle different field types
            if field in ['bedrooms', 'bathrooms', 'super_area', 'furnishing', 'floor', 'age', 'parking']:
                # Use label-value matching for summary fields
                return self._extract_summary_field(card, field)
            else:
                # Use direct selector
                return self._extract_direct_field(card, selector, extraction_method)
        
        except Exception:
            return None
    
    def _extract_direct_field(self, card: Tag, selector: str, method: str) -> Optional[str]:
        """Extract field using direct selector"""
        
        try:
            elements = card.select(selector)
            
            if not elements:
                return None
            
            element = elements[0]
            
            if method == 'href_attribute':
                return element.get('href')
            elif method == 'text_with_regex':
                text = element.get_text(strip=True)
                # Apply basic cleaning for numeric fields
                return text
            else:  # text_content
                return element.get_text(strip=True)
        
        except Exception:
            return None
    
    def _extract_summary_field(self, card: Tag, field: str) -> Optional[str]:
        """Extract field using label-value matching in summary section"""
        
        try:
            # Find summary items
            summary_items = card.select('.mb-srp__card__summary__list--item')
            
            # Get label keywords for this field
            label_keywords = self._get_field_keywords(field)
            
            for item in summary_items:
                # Check if this item contains our field
                item_text = item.get_text(strip=True).lower()
                
                if any(keyword in item_text for keyword in label_keywords):
                    # Try to extract value
                    value_elements = item.select('.mb-srp__card__summary--value')
                    if value_elements:
                        return value_elements[0].get_text(strip=True)
                    else:
                        # Fallback to item text
                        return item.get_text(strip=True)
            
            return None
        
        except Exception:
            return None
    
    def _get_field_keywords(self, field: str) -> List[str]:
        """Get keywords for field identification"""
        
        keywords = {
            'bedrooms': ['bhk', 'bedroom', 'bed'],
            'bathrooms': ['bathroom', 'bath', 'toilet'],
            'super_area': ['super', 'built', 'carpet', 'sqft'],
            'furnishing': ['furnish', 'furnished', 'semi'],
            'floor': ['floor', 'flr'],
            'age': ['age', 'year', 'old'],
            'parking': ['parking', 'car']
        }
        
        return keywords.get(field, [])
    
    def _analyze_performance(self):
        """Analyze overall performance of improved selectors"""
        
        print("📊 Analyzing overall performance...")
        
        # Calculate overall statistics
        total_fields = len(self.test_results['field_performance'])
        successful_fields = sum(1 for perf in self.test_results['field_performance'].values() 
                               if perf['success_rate'] >= 70)
        
        success_rates = [perf['success_rate'] for perf in self.test_results['field_performance'].values()]
        
        self.test_results['overall_performance'] = {
            'total_fields_tested': total_fields,
            'fields_above_70_percent': successful_fields,
            'overall_success_percentage': (successful_fields / total_fields * 100) if total_fields > 0 else 0,
            'average_success_rate': statistics.mean(success_rates) if success_rates else 0,
            'median_success_rate': statistics.median(success_rates) if success_rates else 0,
            'min_success_rate': min(success_rates) if success_rates else 0,
            'max_success_rate': max(success_rates) if success_rates else 0
        }
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Analyze field performance
        for field, performance in self.test_results['field_performance'].items():
            success_rate = performance['success_rate']
            
            if success_rate >= 90:
                recommendations.append({
                    'field': field,
                    'priority': 'low',
                    'action': 'maintain_current_selector',
                    'description': f"{field} has excellent performance ({success_rate:.1f}%)"
                })
            elif success_rate >= 70:
                recommendations.append({
                    'field': field,
                    'priority': 'medium',
                    'action': 'minor_optimization',
                    'description': f"{field} has good performance ({success_rate:.1f}%) but could be optimized"
                })
            else:
                recommendations.append({
                    'field': field,
                    'priority': 'high',
                    'action': 'requires_improvement',
                    'description': f"{field} has low performance ({success_rate:.1f}%) and needs improvement"
                })
        
        # Overall recommendations
        overall_perf = self.test_results['overall_performance']
        avg_success = overall_perf['average_success_rate']
        
        if avg_success >= 80:
            recommendations.append({
                'field': 'overall',
                'priority': 'low',
                'action': 'deploy_to_production',
                'description': f"Overall performance is excellent ({avg_success:.1f}%). Ready for production."
            })
        elif avg_success >= 60:
            recommendations.append({
                'field': 'overall',
                'priority': 'medium',
                'action': 'optimize_low_performers',
                'description': f"Overall performance is good ({avg_success:.1f}%). Focus on optimizing low-performing fields."
            })
        else:
            recommendations.append({
                'field': 'overall',
                'priority': 'high',
                'action': 'comprehensive_review',
                'description': f"Overall performance needs improvement ({avg_success:.1f}%). Comprehensive selector review required."
            })
        
        self.test_results['recommendations'] = recommendations
    
    def _save_test_results(self):
        """Save test results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"improved_selector_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Test results saved: {filename}")
    
    def _print_test_summary(self):
        """Print comprehensive test summary"""
        
        print("\n📊 IMPROVED SELECTOR TEST SUMMARY")
        print("="*50)
        
        print(f"📄 Pages Tested: {self.test_results['pages_tested']}")
        print(f"🏠 Properties Tested: {self.test_results['properties_tested']}")
        
        # Field performance
        print(f"\n🎯 FIELD PERFORMANCE:")
        for field in self.target_fields:
            if field in self.test_results['field_performance']:
                perf = self.test_results['field_performance'][field]
                success_rate = perf['success_rate']
                status = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 60 else "🔴"
                print(f"   {status} {field}: {success_rate:.1f}% "
                      f"({perf['successful_extractions']}/{perf['total_cards_tested']})")
        
        # Overall performance
        overall = self.test_results['overall_performance']
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"   📊 Average Success Rate: {overall['average_success_rate']:.1f}%")
        print(f"   📊 Fields Above 70%: {overall['fields_above_70_percent']}/{overall['total_fields_tested']}")
        print(f"   📊 Range: {overall['min_success_rate']:.1f}% - {overall['max_success_rate']:.1f}%")
        
        # Top recommendations
        print(f"\n💡 TOP RECOMMENDATIONS:")
        high_priority_recs = [r for r in self.test_results['recommendations'] if r.get('priority') == 'high']
        for i, rec in enumerate(high_priority_recs[:5], 1):
            print(f"   {i}. {rec['description']}")
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for testing"""
        
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


def main():
    """Main function for testing improved selectors"""
    
    print("🧪 Improved Selector Testing Tool")
    print("Testing improved selectors against real MagicBricks data...")
    print()
    
    try:
        # Initialize tester
        tester = ImprovedSelectorTester()
        
        # Run comprehensive testing
        results = tester.test_improved_selectors(num_pages=3)
        
        if 'error' not in results:
            print("\n✅ IMPROVED SELECTOR TESTING COMPLETED SUCCESSFULLY!")
            
            overall_perf = results['overall_performance']
            print(f"📊 Average Success Rate: {overall_perf['average_success_rate']:.1f}%")
            print(f"🎯 Fields Above 70%: {overall_perf['fields_above_70_percent']}/{overall_perf['total_fields_tested']}")
            
        else:
            print(f"\n❌ IMPROVED SELECTOR TESTING FAILED: {results['error']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
