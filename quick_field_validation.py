#!/usr/bin/env python3
"""
Quick Field Validation
Quick validation of improved selectors to confirm extraction improvements.
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class QuickFieldValidator:
    """
    Quick validator for field extraction improvements
    """
    
    def __init__(self):
        """Initialize quick field validator"""
        
        # Key fields to validate
        self.key_fields = [
            'title', 'price', 'area', 'super_area', 'bedrooms', 'bathrooms',
            'society', 'locality', 'status', 'property_url'
        ]
        
        # Priority fields (previously low completeness)
        self.priority_fields = ['super_area', 'society', 'status']
        
        # Improved selectors based on analysis
        self.improved_selectors = {
            'property_card': '.mb-srp__card',
            'title': '.mb-srp__card--title a',
            'price': '.mb-srp__card__price--amount',
            'area': '.mb-srp__card__price--size',
            'super_area': '.mb-srp__card__summary--value',
            'bedrooms': '.mb-srp__card__summary--value',
            'bathrooms': '.mb-srp__card__summary--value',
            'society': '.mb-srp__card__society',
            'locality': '.mb-srp__card__ads--locality',
            'status': '.mb-srp__card__summary__list--item',
            'property_url': '.mb-srp__card--title a'
        }
        
        # Original selectors for comparison
        self.original_selectors = {
            'property_card': '.mb-srp__card',
            'title': '.mb-srp__card__title--link',
            'price': '.mb-srp__card__price--amount',
            'area': '.mb-srp__card__summary--value',
            'super_area': '.mb-srp__card__summary--value',
            'bedrooms': '.mb-srp__card__summary--value',
            'bathrooms': '.mb-srp__card__summary--value',
            'society': '.mb-srp__card__society',
            'locality': '.mb-srp__card__ads--locality',
            'status': '.mb-srp__card__summary--value',
            'property_url': '.mb-srp__card__title--link'
        }
        
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'properties_tested': 0,
            'original_performance': {},
            'improved_performance': {},
            'improvements': {}
        }
        
        print("⚡ Quick Field Validator Initialized")
        print(f"🎯 Testing {len(self.key_fields)} key fields")
    
    def validate_field_improvements(self) -> Dict[str, Any]:
        """
        Quick validation of field extraction improvements
        """
        
        print("\n🚀 Starting Quick Field Validation")
        print("="*50)
        
        try:
            # Load test page
            print("📄 Loading test page...")
            test_cards = self._load_test_page()
            
            if not test_cards:
                print("❌ No test cards could be loaded")
                return self.validation_results
            
            print(f"✅ Loaded {len(test_cards)} property cards for testing")
            self.validation_results['properties_tested'] = len(test_cards)
            
            # Test original selectors
            print("\n🔍 Testing original selectors...")
            self._test_selectors(test_cards, self.original_selectors, 'original')
            
            # Test improved selectors
            print("\n⚡ Testing improved selectors...")
            self._test_selectors(test_cards, self.improved_selectors, 'improved')
            
            # Calculate improvements
            print("\n📊 Calculating improvements...")
            self._calculate_improvements()
            
            # Print results
            self._print_validation_results()
            
            # Save results
            self._save_validation_results()
            
            return self.validation_results
            
        except Exception as e:
            print(f"❌ Validation failed: {str(e)}")
            self.validation_results['error'] = str(e)
            return self.validation_results
    
    def _load_test_page(self) -> List[Tag]:
        """Load test page and extract property cards"""
        
        driver = self._setup_browser()
        
        try:
            # Navigate to test page
            url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
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
            
            return property_cards[:20]  # Test first 20 cards
            
        finally:
            driver.quit()
    
    def _test_selectors(self, cards: List[Tag], selectors: Dict[str, str], test_type: str):
        """Test selectors against property cards"""
        
        results = {}
        
        for field in self.key_fields:
            print(f"   🎯 Testing {field}...")
            
            selector = selectors.get(field)
            if not selector:
                results[field] = {'success_rate': 0, 'successful': 0, 'total': len(cards)}
                continue
            
            successful = 0
            sample_values = []
            
            for card in cards:
                try:
                    extracted_value = self._extract_field_value(card, field, selector)
                    
                    if extracted_value and extracted_value.strip():
                        successful += 1
                        
                        if len(sample_values) < 3:
                            sample_values.append(extracted_value.strip()[:50])  # First 50 chars
                
                except Exception:
                    pass
            
            success_rate = (successful / len(cards)) * 100 if cards else 0
            
            results[field] = {
                'success_rate': success_rate,
                'successful': successful,
                'total': len(cards),
                'sample_values': sample_values
            }
            
            print(f"      ✅ {field}: {success_rate:.1f}% ({successful}/{len(cards)})")
        
        if test_type == 'original':
            self.validation_results['original_performance'] = results
        else:
            self.validation_results['improved_performance'] = results
    
    def _extract_field_value(self, card: Tag, field: str, selector: str) -> Optional[str]:
        """Extract field value using selector"""
        
        try:
            elements = card.select(selector)
            
            if not elements:
                return None
            
            element = elements[0]
            
            if field == 'property_url':
                return element.get('href')
            elif field in ['super_area', 'bedrooms', 'bathrooms']:
                # For summary fields, try to find specific content
                text = element.get_text(strip=True)
                
                if field == 'super_area' and ('sqft' in text.lower() or 'sq' in text.lower()):
                    return text
                elif field == 'bedrooms' and ('bhk' in text.lower() or 'bed' in text.lower()):
                    return text
                elif field == 'bathrooms' and ('bath' in text.lower() or 'toilet' in text.lower()):
                    return text
                else:
                    return text if text else None
            else:
                return element.get_text(strip=True)
        
        except Exception:
            return None
    
    def _calculate_improvements(self):
        """Calculate improvements between original and improved selectors"""
        
        improvements = {}
        
        for field in self.key_fields:
            original = self.validation_results['original_performance'].get(field, {})
            improved = self.validation_results['improved_performance'].get(field, {})
            
            original_rate = original.get('success_rate', 0)
            improved_rate = improved.get('success_rate', 0)
            
            improvement = improved_rate - original_rate
            
            improvements[field] = {
                'original_rate': original_rate,
                'improved_rate': improved_rate,
                'absolute_improvement': improvement,
                'percentage_improvement': (improvement / original_rate * 100) if original_rate > 0 else 0,
                'status': 'improved' if improvement > 0 else 'declined' if improvement < 0 else 'unchanged'
            }
        
        self.validation_results['improvements'] = improvements
    
    def _print_validation_results(self):
        """Print validation results"""
        
        print("\n📊 QUICK FIELD VALIDATION RESULTS")
        print("="*50)
        
        print(f"🏠 Properties Tested: {self.validation_results['properties_tested']}")
        
        # Overall performance
        original_avg = sum(perf['success_rate'] for perf in self.validation_results['original_performance'].values()) / len(self.key_fields)
        improved_avg = sum(perf['success_rate'] for perf in self.validation_results['improved_performance'].values()) / len(self.key_fields)
        overall_improvement = improved_avg - original_avg
        
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"   📊 Original Average: {original_avg:.1f}%")
        print(f"   ⚡ Improved Average: {improved_avg:.1f}%")
        print(f"   📈 Overall Improvement: {overall_improvement:+.1f}%")
        
        # Priority fields
        print(f"\n🎯 PRIORITY FIELDS:")
        for field in self.priority_fields:
            improvement = self.validation_results['improvements'].get(field, {})
            original = improvement.get('original_rate', 0)
            improved = improvement.get('improved_rate', 0)
            change = improvement.get('absolute_improvement', 0)
            
            status = "✅" if change > 0 else "❌" if change < 0 else "➖"
            print(f"   {status} {field}: {original:.1f}% → {improved:.1f}% ({change:+.1f}%)")
        
        # Top improvements
        improvements_list = [(field, data['absolute_improvement']) for field, data in self.validation_results['improvements'].items()]
        improvements_list.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🚀 TOP IMPROVEMENTS:")
        for field, improvement in improvements_list[:5]:
            if improvement > 0:
                print(f"   ✅ {field}: +{improvement:.1f}%")
        
        # Summary
        improved_fields = sum(1 for data in self.validation_results['improvements'].values() if data['absolute_improvement'] > 0)
        declined_fields = sum(1 for data in self.validation_results['improvements'].values() if data['absolute_improvement'] < 0)
        
        print(f"\n📋 SUMMARY:")
        print(f"   ✅ Fields Improved: {improved_fields}/{len(self.key_fields)}")
        print(f"   ❌ Fields Declined: {declined_fields}/{len(self.key_fields)}")
        print(f"   🎯 Priority Fields Improved: {sum(1 for field in self.priority_fields if self.validation_results['improvements'].get(field, {}).get('absolute_improvement', 0) > 0)}/{len(self.priority_fields)}")
    
    def _save_validation_results(self):
        """Save validation results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_field_validation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Validation results saved: {filename}")
    
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


def main():
    """Main function for quick field validation"""
    
    print("⚡ Quick Field Validation Tool")
    print("Quick validation of improved selectors...")
    print()
    
    try:
        # Initialize validator
        validator = QuickFieldValidator()
        
        # Run validation
        results = validator.validate_field_improvements()
        
        if 'error' not in results:
            print("\n✅ QUICK FIELD VALIDATION COMPLETED SUCCESSFULLY!")
            
            # Calculate summary metrics
            improvements = results['improvements']
            improved_count = sum(1 for data in improvements.values() if data['absolute_improvement'] > 0)
            priority_improved = sum(1 for field in validator.priority_fields 
                                  if improvements.get(field, {}).get('absolute_improvement', 0) > 0)
            
            print(f"🎯 Fields Improved: {improved_count}/{len(validator.key_fields)}")
            print(f"🎯 Priority Fields Improved: {priority_improved}/{len(validator.priority_fields)}")
            
        else:
            print(f"\n❌ QUICK FIELD VALIDATION FAILED: {results['error']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
