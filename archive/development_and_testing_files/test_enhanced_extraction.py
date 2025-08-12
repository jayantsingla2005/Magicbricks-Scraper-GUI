#!/usr/bin/env python3
"""
Test Enhanced Premium Scraper
Compares original scraper vs enhanced scraper extraction rates
Focuses on the problematic properties identified in previous analysis
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Any, Optional

# Import both scrapers for comparison
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from enhanced_premium_scraper import EnhancedPremiumScraper


class ExtractionComparisonTest:
    """
    Test class to compare original vs enhanced scraper performance
    """
    
    def __init__(self):
        self.test_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
        self.results = {
            'original_scraper': {},
            'enhanced_scraper': {},
            'comparison': {}
        }
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver for testing"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Anti-detection measures
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def get_page_html(self) -> str:
        """Get HTML content from the test page"""
        driver = self.setup_driver()
        
        try:
            print(f"Loading test page: {self.test_url}")
            driver.get(self.test_url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mb-srp__list")))
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Get page source
            html_content = driver.page_source
            print("Page loaded successfully")
            
            return html_content
            
        except Exception as e:
            print(f"Error loading page: {e}")
            return None
        finally:
            driver.quit()
    
    def extract_property_cards(self, html_content: str) -> List:
        """Extract property cards from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find property cards using multiple selectors
        card_selectors = [
            '.mb-srp__card',
            '.mb-srp__card--item',
            '[class*="mb-srp__card"]'
        ]
        
        cards = []
        for selector in card_selectors:
            found_cards = soup.select(selector)
            if found_cards:
                cards = found_cards
                break
        
        print(f"Found {len(cards)} property cards")
        return cards
    
    def test_original_scraper(self, cards: List) -> Dict[str, Any]:
        """Test original scraper extraction"""
        print("\n=== Testing Original Scraper ===")
        
        # Create original scraper instance
        original_scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
        original_scraper.setup_logging()
        
        results = {
            'total_cards': len(cards),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'properties': [],
            'failed_indices': [],
            'extraction_details': []
        }
        
        for i, card in enumerate(cards):
            try:
                property_data = original_scraper.extract_property_data(card, 1, i)
                
                extraction_detail = {
                    'index': i,
                    'success': property_data is not None,
                    'title': property_data.get('title', 'N/A') if property_data else 'N/A',
                    'price': property_data.get('price', 'N/A') if property_data else 'N/A',
                    'area': property_data.get('area', 'N/A') if property_data else 'N/A',
                    'url': property_data.get('property_url', 'N/A') if property_data else 'N/A'
                }
                
                if property_data:
                    results['successful_extractions'] += 1
                    results['properties'].append(property_data)
                else:
                    results['failed_extractions'] += 1
                    results['failed_indices'].append(i)
                
                results['extraction_details'].append(extraction_detail)
                
            except Exception as e:
                print(f"Error extracting property {i}: {e}")
                results['failed_extractions'] += 1
                results['failed_indices'].append(i)
                results['extraction_details'].append({
                    'index': i,
                    'success': False,
                    'error': str(e)
                })
        
        success_rate = (results['successful_extractions'] / results['total_cards'] * 100) if results['total_cards'] > 0 else 0
        results['success_rate'] = success_rate
        
        print(f"Original Scraper Results:")
        print(f"  Total Cards: {results['total_cards']}")
        print(f"  Successful: {results['successful_extractions']}")
        print(f"  Failed: {results['failed_extractions']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Failed Indices: {results['failed_indices']}")
        
        return results
    
    def test_enhanced_scraper(self, cards: List) -> Dict[str, Any]:
        """Test enhanced scraper extraction"""
        print("\n=== Testing Enhanced Scraper ===")
        
        # Create enhanced scraper instance
        enhanced_scraper = EnhancedPremiumScraper(headless=True, incremental_enabled=False)
        enhanced_scraper.setup_logging()
        
        results = {
            'total_cards': len(cards),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'premium_properties': 0,
            'properties': [],
            'failed_indices': [],
            'extraction_details': [],
            'premium_stats': enhanced_scraper.premium_stats.copy()
        }
        
        for i, card in enumerate(cards):
            try:
                property_data = enhanced_scraper.extract_enhanced_property_data(card, 1, i)
                
                extraction_detail = {
                    'index': i,
                    'success': property_data is not None,
                    'title': property_data.get('title', 'N/A') if property_data else 'N/A',
                    'price': property_data.get('price', 'N/A') if property_data else 'N/A',
                    'area': property_data.get('area', 'N/A') if property_data else 'N/A',
                    'url': property_data.get('property_url', 'N/A') if property_data else 'N/A',
                    'is_premium': property_data.get('is_premium', False) if property_data else False,
                    'premium_type': property_data.get('premium_type', 'N/A') if property_data else 'N/A'
                }
                
                if property_data:
                    results['successful_extractions'] += 1
                    results['properties'].append(property_data)
                    
                    if property_data.get('is_premium', False):
                        results['premium_properties'] += 1
                else:
                    results['failed_extractions'] += 1
                    results['failed_indices'].append(i)
                
                results['extraction_details'].append(extraction_detail)
                
            except Exception as e:
                print(f"Error extracting property {i}: {e}")
                results['failed_extractions'] += 1
                results['failed_indices'].append(i)
                results['extraction_details'].append({
                    'index': i,
                    'success': False,
                    'error': str(e)
                })
        
        success_rate = (results['successful_extractions'] / results['total_cards'] * 100) if results['total_cards'] > 0 else 0
        results['success_rate'] = success_rate
        results['premium_stats'] = enhanced_scraper.premium_stats
        
        print(f"Enhanced Scraper Results:")
        print(f"  Total Cards: {results['total_cards']}")
        print(f"  Successful: {results['successful_extractions']}")
        print(f"  Failed: {results['failed_extractions']}")
        print(f"  Premium Properties: {results['premium_properties']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Failed Indices: {results['failed_indices']}")
        print(f"  Premium Stats: {results['premium_stats']}")
        
        return results
    
    def compare_results(self, original_results: Dict, enhanced_results: Dict) -> Dict[str, Any]:
        """Compare results between original and enhanced scrapers"""
        print("\n=== Comparison Analysis ===")
        
        comparison = {
            'improvement': {
                'successful_extractions': enhanced_results['successful_extractions'] - original_results['successful_extractions'],
                'success_rate_improvement': enhanced_results['success_rate'] - original_results['success_rate'],
                'failed_extractions_reduced': original_results['failed_extractions'] - enhanced_results['failed_extractions']
            },
            'originally_failed_now_successful': [],
            'still_failing': [],
            'premium_analysis': {
                'total_premium_detected': enhanced_results['premium_properties'],
                'premium_stats': enhanced_results['premium_stats']
            }
        }
        
        # Analyze which originally failed properties are now successful
        original_failed = set(original_results['failed_indices'])
        enhanced_failed = set(enhanced_results['failed_indices'])
        
        comparison['originally_failed_now_successful'] = list(original_failed - enhanced_failed)
        comparison['still_failing'] = list(original_failed & enhanced_failed)
        comparison['newly_failing'] = list(enhanced_failed - original_failed)
        
        print(f"Improvement Analysis:")
        print(f"  Success Rate Improvement: +{comparison['improvement']['success_rate_improvement']:.1f}%")
        print(f"  Additional Successful Extractions: +{comparison['improvement']['successful_extractions']}")
        print(f"  Failed Extractions Reduced: -{comparison['improvement']['failed_extractions_reduced']}")
        print(f"  Originally Failed, Now Successful: {len(comparison['originally_failed_now_successful'])} properties")
        print(f"  Still Failing: {len(comparison['still_failing'])} properties")
        print(f"  Premium Properties Detected: {comparison['premium_analysis']['total_premium_detected']}")
        
        if comparison['originally_failed_now_successful']:
            print(f"  Recovered Property Indices: {comparison['originally_failed_now_successful']}")
        
        return comparison
    
    def analyze_specific_failures(self, original_results: Dict, enhanced_results: Dict):
        """Analyze specific failure cases"""
        print("\n=== Detailed Failure Analysis ===")
        
        # Focus on the known problematic indices from previous analysis
        known_failed_indices = [4, 9, 11, 14, 17, 19, 22, 24]  # From previous analysis
        
        print("Analysis of Previously Known Failed Properties:")
        for idx in known_failed_indices:
            if idx < len(original_results['extraction_details']) and idx < len(enhanced_results['extraction_details']):
                orig_detail = original_results['extraction_details'][idx]
                enh_detail = enhanced_results['extraction_details'][idx]
                
                print(f"\nProperty {idx}:")
                print(f"  Original: Success={orig_detail['success']}, Title='{orig_detail['title'][:50]}...', Area='{orig_detail['area']}'")
                print(f"  Enhanced: Success={enh_detail['success']}, Title='{enh_detail['title'][:50]}...', Area='{enh_detail['area']}'")
                
                if enh_detail.get('is_premium'):
                    print(f"  Premium Type: {enh_detail.get('premium_type', 'N/A')}")
                
                if orig_detail['success'] != enh_detail['success']:
                    status = "RECOVERED" if enh_detail['success'] else "STILL FAILING"
                    print(f"  Status: {status}")
    
    def save_detailed_results(self, original_results: Dict, enhanced_results: Dict, comparison: Dict):
        """Save detailed results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comprehensive results
        results_data = {
            'test_info': {
                'timestamp': timestamp,
                'test_url': self.test_url,
                'total_cards_tested': len(original_results['extraction_details'])
            },
            'original_scraper': original_results,
            'enhanced_scraper': enhanced_results,
            'comparison': comparison
        }
        
        # Save JSON results
        json_filename = f"extraction_comparison_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {json_filename}")
        
        # Save CSV comparison
        csv_data = []
        for i, (orig, enh) in enumerate(zip(original_results['extraction_details'], enhanced_results['extraction_details'])):
            csv_data.append({
                'property_index': i,
                'original_success': orig['success'],
                'enhanced_success': enh['success'],
                'original_title': orig.get('title', 'N/A'),
                'enhanced_title': enh.get('title', 'N/A'),
                'original_area': orig.get('area', 'N/A'),
                'enhanced_area': enh.get('area', 'N/A'),
                'is_premium': enh.get('is_premium', False),
                'premium_type': enh.get('premium_type', 'N/A'),
                'improvement': 'RECOVERED' if not orig['success'] and enh['success'] else 
                              'MAINTAINED' if orig['success'] and enh['success'] else
                              'DEGRADED' if orig['success'] and not enh['success'] else 'STILL_FAILED'
            })
        
        csv_filename = f"extraction_comparison_{timestamp}.csv"
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_filename, index=False)
        
        print(f"CSV comparison saved to: {csv_filename}")
        
        return json_filename, csv_filename
    
    def run_comprehensive_test(self):
        """Run comprehensive comparison test"""
        print("=== ENHANCED SCRAPER COMPARISON TEST ===")
        print(f"Test URL: {self.test_url}")
        print(f"Test Time: {datetime.now()}")
        
        # Get page HTML
        html_content = self.get_page_html()
        if not html_content:
            print("Failed to load page content")
            return
        
        # Extract property cards
        cards = self.extract_property_cards(html_content)
        if not cards:
            print("No property cards found")
            return
        
        # Test original scraper
        original_results = self.test_original_scraper(cards)
        
        # Test enhanced scraper
        enhanced_results = self.test_enhanced_scraper(cards)
        
        # Compare results
        comparison = self.compare_results(original_results, enhanced_results)
        
        # Analyze specific failures
        self.analyze_specific_failures(original_results, enhanced_results)
        
        # Save results
        json_file, csv_file = self.save_detailed_results(original_results, enhanced_results, comparison)
        
        print("\n=== TEST COMPLETED ===")
        print(f"Results saved to: {json_file} and {csv_file}")
        
        return {
            'original_results': original_results,
            'enhanced_results': enhanced_results,
            'comparison': comparison,
            'files_saved': [json_file, csv_file]
        }


if __name__ == "__main__":
    # Run the comprehensive test
    test = ExtractionComparisonTest()
    results = test.run_comprehensive_test()
    
    if results:
        print("\n=== FINAL SUMMARY ===")
        print(f"Original Success Rate: {results['original_results']['success_rate']:.1f}%")
        print(f"Enhanced Success Rate: {results['enhanced_results']['success_rate']:.1f}%")
        print(f"Improvement: +{results['comparison']['improvement']['success_rate_improvement']:.1f}%")
        print(f"Premium Properties Detected: {results['enhanced_results']['premium_properties']}")