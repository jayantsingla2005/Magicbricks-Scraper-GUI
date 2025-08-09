#!/usr/bin/env python3
"""
Comprehensive Field Extraction Tester
Tests improved selectors and validates extraction improvements across all fields.
Provides before/after comparison and comprehensive validation.
"""

import time
import json
import csv
import re
from typing import Dict, List, Any, Optional, Tuple
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


class ComprehensiveFieldExtractionTester:
    """
    Comprehensive tester for field extraction improvements
    """
    
    def __init__(self):
        """Initialize comprehensive field extraction tester"""
        
        # Load improved configuration
        self.improved_config = self._load_improved_config()
        self.original_config = self._load_original_config()
        
        # All fields to test
        self.all_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'balconies', 'furnishing', 'floor', 'total_floors', 'age',
            'facing', 'parking', 'status', 'society', 'locality', 'city',
            'property_type', 'transaction_type', 'possession', 'property_url'
        ]
        
        # Priority fields (previously low completeness)
        self.priority_fields = ['super_area', 'society', 'status']
        
        # Test results
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_tested': 0,
            'properties_tested': 0,
            'original_performance': {},
            'improved_performance': {},
            'comparison_analysis': {},
            'field_improvements': {},
            'overall_metrics': {},
            'validation_results': {}
        }
        
        print("🧪 Comprehensive Field Extraction Tester Initialized")
        print(f"🎯 Testing {len(self.all_fields)} fields")
        print(f"🔍 Priority fields: {', '.join(self.priority_fields)}")
    
    def _load_improved_config(self) -> Dict[str, Any]:
        """Load improved selector configuration"""
        
        try:
            with open('config/improved_scraper_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Improved config not found, using default")
            return self._get_default_improved_config()
    
    def _load_original_config(self) -> Dict[str, Any]:
        """Load original selector configuration for comparison"""
        
        try:
            with open('config/scraper_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Original config not found, using default")
            return self._get_default_original_config()
    
    def _get_default_improved_config(self) -> Dict[str, Any]:
        """Get default improved configuration"""
        
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
    
    def _get_default_original_config(self) -> Dict[str, Any]:
        """Get default original configuration"""
        
        return {
            'selectors': {
                'property_card': '.mb-srp__card',
                'title': '.mb-srp__card__title--link',
                'price': '.mb-srp__card__price--amount',
                'area': '.mb-srp__card__summary--value',
                'locality': '.mb-srp__card__ads--locality',
                'society': '.mb-srp__card__society',
                'status': '.mb-srp__card__summary--value',
                'property_url': '.mb-srp__card__title--link'
            }
        }
    
    def test_field_extraction_comprehensive(self, num_pages: int = 3) -> Dict[str, Any]:
        """
        Perform comprehensive field extraction testing
        """
        
        print("\n🚀 Starting Comprehensive Field Extraction Testing")
        print("="*60)
        
        try:
            # Step 1: Load test data
            print("📄 Step 1: Loading Test Data...")
            test_data = self._load_test_data(num_pages)
            
            if not test_data:
                print("❌ No test data could be loaded")
                return self.test_results
            
            # Step 2: Test original selectors
            print("\n🔍 Step 2: Testing Original Selectors...")
            self._test_original_selectors(test_data)
            
            # Step 3: Test improved selectors
            print("\n⚡ Step 3: Testing Improved Selectors...")
            self._test_improved_selectors(test_data)
            
            # Step 4: Compare performance
            print("\n📊 Step 4: Comparing Performance...")
            self._compare_performance()
            
            # Step 5: Validate improvements
            print("\n✅ Step 5: Validating Improvements...")
            self._validate_improvements()
            
            # Step 6: Generate comprehensive report
            print("\n📋 Step 6: Generating Comprehensive Report...")
            self._generate_comprehensive_report()
            
            # Step 7: Save results
            print("\n💾 Step 7: Saving Test Results...")
            self._save_test_results()
            
            print("\n✅ Comprehensive Field Extraction Testing Complete!")
            self._print_test_summary()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Field extraction testing failed: {str(e)}")
            self.test_results['error'] = str(e)
            return self.test_results
    
    def _load_test_data(self, num_pages: int) -> List[Dict[str, Any]]:
        """Load test data from listing pages"""
        
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
                    
                    # Find property cards
                    property_cards = soup.select('.mb-srp__card')
                    
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
    
    def _test_original_selectors(self, test_data: List[Dict[str, Any]]):
        """Test original selectors for baseline comparison"""
        
        print("🔍 Testing original selectors for baseline...")
        
        for field in self.all_fields:
            print(f"   📊 Testing original {field}...")
            
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
                        # Extract using original selector
                        extracted_value = self._extract_field_original(card, field)
                        
                        if extracted_value and extracted_value.strip():
                            field_results['successful_extractions'] += 1
                            
                            # Store sample values (limit to 5)
                            if len(field_results['sample_values']) < 5:
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
            
            self.test_results['original_performance'][field] = field_results
    
    def _test_improved_selectors(self, test_data: List[Dict[str, Any]]):
        """Test improved selectors"""
        
        print("⚡ Testing improved selectors...")
        
        for field in self.all_fields:
            print(f"   🎯 Testing improved {field}...")
            
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
                        extracted_value = self._extract_field_improved(card, field)
                        
                        if extracted_value and extracted_value.strip():
                            field_results['successful_extractions'] += 1
                            
                            # Store sample values (limit to 5)
                            if len(field_results['sample_values']) < 5:
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
            
            self.test_results['improved_performance'][field] = field_results
    
    def _extract_field_original(self, card: Tag, field: str) -> Optional[str]:
        """Extract field using original selectors"""
        
        try:
            selector = self.original_config['selectors'].get(field)
            if not selector:
                return None
            
            elements = card.select(selector)
            if not elements:
                return None
            
            element = elements[0]
            
            if field == 'property_url':
                return element.get('href')
            else:
                return element.get_text(strip=True)
        
        except Exception:
            return None
    
    def _extract_field_improved(self, card: Tag, field: str) -> Optional[str]:
        """Extract field using improved selectors"""
        
        try:
            selector = self.improved_config['selectors'].get(field)
            extraction_method = self.improved_config.get('extraction_methods', {}).get(field, 'text_content')
            
            if not selector:
                return None
            
            elements = card.select(selector)
            if not elements:
                return None
            
            element = elements[0]
            
            if extraction_method == 'href_attribute':
                return element.get('href')
            elif extraction_method == 'text_with_regex':
                text = element.get_text(strip=True)
                # Apply basic cleaning for numeric fields
                return text
            else:  # text_content
                return element.get_text(strip=True)
        
        except Exception:
            return None
    
    def _compare_performance(self):
        """Compare original vs improved performance"""
        
        print("📊 Comparing original vs improved performance...")
        
        comparison = {}
        
        for field in self.all_fields:
            original = self.test_results['original_performance'].get(field, {})
            improved = self.test_results['improved_performance'].get(field, {})
            
            original_rate = original.get('success_rate', 0)
            improved_rate = improved.get('success_rate', 0)
            
            improvement = improved_rate - original_rate
            improvement_percentage = (improvement / original_rate * 100) if original_rate > 0 else 0
            
            comparison[field] = {
                'original_success_rate': original_rate,
                'improved_success_rate': improved_rate,
                'absolute_improvement': improvement,
                'percentage_improvement': improvement_percentage,
                'status': 'improved' if improvement > 0 else 'declined' if improvement < 0 else 'unchanged'
            }
        
        self.test_results['comparison_analysis'] = comparison
    
    def _validate_improvements(self):
        """Validate that improvements meet expectations"""
        
        print("✅ Validating improvements...")
        
        validation = {
            'priority_fields_improved': 0,
            'total_fields_improved': 0,
            'total_fields_declined': 0,
            'average_improvement': 0,
            'meets_expectations': False,
            'validation_details': {}
        }
        
        improvements = []
        
        for field in self.all_fields:
            comparison = self.test_results['comparison_analysis'].get(field, {})
            improvement = comparison.get('absolute_improvement', 0)
            
            improvements.append(improvement)
            
            if improvement > 0:
                validation['total_fields_improved'] += 1
                
                if field in self.priority_fields:
                    validation['priority_fields_improved'] += 1
            elif improvement < 0:
                validation['total_fields_declined'] += 1
            
            # Field-specific validation
            validation['validation_details'][field] = {
                'improvement': improvement,
                'meets_target': improvement >= 5.0 if field in self.priority_fields else improvement >= 0,
                'priority_field': field in self.priority_fields
            }
        
        # Calculate average improvement
        validation['average_improvement'] = statistics.mean(improvements) if improvements else 0
        
        # Check if meets expectations
        priority_improved = validation['priority_fields_improved'] >= len(self.priority_fields) * 0.7  # 70% of priority fields
        overall_positive = validation['average_improvement'] > 0
        no_major_regressions = validation['total_fields_declined'] <= len(self.all_fields) * 0.2  # Max 20% decline
        
        validation['meets_expectations'] = priority_improved and overall_positive and no_major_regressions
        
        self.test_results['validation_results'] = validation
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        
        print("📋 Generating comprehensive report...")
        
        # Calculate overall metrics
        original_rates = [perf['success_rate'] for perf in self.test_results['original_performance'].values()]
        improved_rates = [perf['success_rate'] for perf in self.test_results['improved_performance'].values()]
        
        overall_metrics = {
            'original_average': statistics.mean(original_rates) if original_rates else 0,
            'improved_average': statistics.mean(improved_rates) if improved_rates else 0,
            'overall_improvement': statistics.mean(improved_rates) - statistics.mean(original_rates) if original_rates and improved_rates else 0,
            'fields_tested': len(self.all_fields),
            'properties_tested': self.test_results['properties_tested'],
            'pages_tested': self.test_results['pages_tested']
        }
        
        self.test_results['overall_metrics'] = overall_metrics
        
        # Identify top improvements and regressions
        improvements = []
        regressions = []
        
        for field, comparison in self.test_results['comparison_analysis'].items():
            improvement = comparison['absolute_improvement']
            
            if improvement > 5:
                improvements.append((field, improvement))
            elif improvement < -5:
                regressions.append((field, improvement))
        
        # Sort by magnitude
        improvements.sort(key=lambda x: x[1], reverse=True)
        regressions.sort(key=lambda x: x[1])
        
        self.test_results['field_improvements'] = {
            'top_improvements': improvements[:5],
            'significant_regressions': regressions[:3]
        }
    
    def _save_test_results(self):
        """Save comprehensive test results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON results
        json_filename = f"comprehensive_field_extraction_test_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Save CSV comparison
        csv_filename = f"field_extraction_comparison_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Field', 'Original_Success_Rate', 'Improved_Success_Rate', 
                           'Absolute_Improvement', 'Percentage_Improvement', 'Status'])
            
            # Write comparison data
            for field, comparison in self.test_results['comparison_analysis'].items():
                writer.writerow([
                    field,
                    f"{comparison['original_success_rate']:.1f}%",
                    f"{comparison['improved_success_rate']:.1f}%",
                    f"{comparison['absolute_improvement']:.1f}%",
                    f"{comparison['percentage_improvement']:.1f}%",
                    comparison['status']
                ])
        
        print(f"📁 Test results saved:")
        print(f"   📄 Detailed results: {json_filename}")
        print(f"   📊 Comparison: {csv_filename}")
    
    def _print_test_summary(self):
        """Print comprehensive test summary"""
        
        print("\n📊 COMPREHENSIVE FIELD EXTRACTION TEST SUMMARY")
        print("="*60)
        
        overall = self.test_results['overall_metrics']
        print(f"📄 Pages Tested: {overall['pages_tested']}")
        print(f"🏠 Properties Tested: {overall['properties_tested']}")
        print(f"🎯 Fields Tested: {overall['fields_tested']}")
        
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"   📊 Original Average: {overall['original_average']:.1f}%")
        print(f"   ⚡ Improved Average: {overall['improved_average']:.1f}%")
        print(f"   📈 Overall Improvement: {overall['overall_improvement']:.1f}%")
        
        # Priority fields performance
        print(f"\n🎯 PRIORITY FIELDS PERFORMANCE:")
        for field in self.priority_fields:
            comparison = self.test_results['comparison_analysis'].get(field, {})
            improvement = comparison.get('absolute_improvement', 0)
            status = "✅" if improvement > 0 else "❌" if improvement < 0 else "➖"
            print(f"   {status} {field}: {comparison.get('original_success_rate', 0):.1f}% → "
                  f"{comparison.get('improved_success_rate', 0):.1f}% ({improvement:+.1f}%)")
        
        # Top improvements
        improvements = self.test_results['field_improvements']['top_improvements']
        if improvements:
            print(f"\n🚀 TOP IMPROVEMENTS:")
            for field, improvement in improvements[:3]:
                print(f"   ✅ {field}: +{improvement:.1f}%")
        
        # Validation results
        validation = self.test_results['validation_results']
        print(f"\n✅ VALIDATION RESULTS:")
        print(f"   🎯 Priority Fields Improved: {validation['priority_fields_improved']}/{len(self.priority_fields)}")
        print(f"   📈 Total Fields Improved: {validation['total_fields_improved']}")
        print(f"   📉 Fields Declined: {validation['total_fields_declined']}")
        print(f"   🎯 Meets Expectations: {'YES' if validation['meets_expectations'] else 'NO'}")
    
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
    """Main function for comprehensive field extraction testing"""
    
    print("🧪 Comprehensive Field Extraction Tester")
    print("Testing improved selectors and validating extraction improvements...")
    print()
    
    try:
        # Initialize tester
        tester = ComprehensiveFieldExtractionTester()
        
        # Run comprehensive testing
        results = tester.test_field_extraction_comprehensive(num_pages=3)
        
        if 'error' not in results:
            print("\n✅ COMPREHENSIVE FIELD EXTRACTION TESTING COMPLETED SUCCESSFULLY!")
            
            overall = results['overall_metrics']
            validation = results['validation_results']
            
            print(f"📊 Overall Improvement: {overall['overall_improvement']:.1f}%")
            print(f"🎯 Priority Fields Improved: {validation['priority_fields_improved']}/{len(tester.priority_fields)}")
            print(f"✅ Meets Expectations: {'YES' if validation['meets_expectations'] else 'NO'}")
            
        else:
            print(f"\n❌ COMPREHENSIVE FIELD EXTRACTION TESTING FAILED: {results['error']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
