#!/usr/bin/env python3
"""
Delhi Selector Investigation
Investigate why Delhi uses fallback selectors and fix the issue
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class DelhiSelectorInvestigator:
    """Investigate Delhi page structure and fix selectors"""
    
    def __init__(self):
        """Initialize investigator"""
        self.driver = None
        print("🔍 DELHI SELECTOR INVESTIGATION")
        print("="*40)
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome WebDriver initialized")
    
    def investigate_delhi_page_structure(self):
        """Investigate Delhi page structure"""
        
        print("\n🏙️ INVESTIGATING DELHI PAGE STRUCTURE")
        print("-" * 40)
        
        try:
            # Navigate to Delhi page
            delhi_url = "https://www.magicbricks.com/property-for-sale-in-delhi-pppfs"
            print(f"🔗 Loading: {delhi_url}")
            
            self.driver.get(delhi_url)
            time.sleep(5)  # Wait for page to load
            
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Test different selectors
            selectors_to_test = [
                "div.mb-srp__card",  # Primary selector
                "div[data-testid='srp-tuple']",  # Alternative 1
                "div.mb-srp__list",  # Alternative 2
                "div.mb-srp__card--resale",  # Alternative 3
                "div.mb-srp__card--new",  # Alternative 4
                ".mb-srp__card",  # Class only
                "[data-testid*='srp']",  # Any SRP test ID
                "div.srp-tuple",  # Alternative naming
                "div.property-card",  # Generic property card
                "div.listing-card"  # Generic listing card
            ]
            
            print("\n📊 SELECTOR TESTING RESULTS:")
            print("-" * 30)
            
            working_selectors = []
            
            for selector in selectors_to_test:
                try:
                    elements = soup.select(selector)
                    count = len(elements)
                    
                    if count > 0:
                        status = "✅ WORKING"
                        working_selectors.append((selector, count))
                    else:
                        status = "❌ NO MATCH"
                    
                    print(f"{status} {selector}: {count} elements")
                    
                except Exception as e:
                    print(f"❌ ERROR {selector}: {str(e)}")
            
            # Analyze the best working selector
            if working_selectors:
                best_selector, best_count = max(working_selectors, key=lambda x: x[1])
                print(f"\n🎯 BEST SELECTOR: {best_selector} ({best_count} elements)")
                
                # Analyze structure of first few elements
                print(f"\n🔍 ANALYZING STRUCTURE OF {best_selector}:")
                print("-" * 40)
                
                best_elements = soup.select(best_selector)[:3]  # First 3 elements
                
                for i, element in enumerate(best_elements, 1):
                    print(f"\n📋 Element {i} structure:")
                    
                    # Look for title
                    title_selectors = [
                        "h2", "h3", ".mb-srp__card__title", ".title", 
                        "[data-testid*='title']", ".property-title"
                    ]
                    
                    for title_sel in title_selectors:
                        title_elem = element.select_one(title_sel)
                        if title_elem:
                            print(f"   ✅ Title ({title_sel}): {title_elem.get_text().strip()[:50]}...")
                            break
                    else:
                        print("   ❌ Title: Not found")
                    
                    # Look for price
                    price_selectors = [
                        ".mb-srp__card__price", ".price", "[data-testid*='price']",
                        ".property-price", ".cost"
                    ]
                    
                    for price_sel in price_selectors:
                        price_elem = element.select_one(price_sel)
                        if price_elem:
                            print(f"   ✅ Price ({price_sel}): {price_elem.get_text().strip()[:30]}...")
                            break
                    else:
                        print("   ❌ Price: Not found")
                    
                    # Look for area
                    area_selectors = [
                        ".mb-srp__card__area", ".area", "[data-testid*='area']",
                        ".property-area", ".size"
                    ]
                    
                    for area_sel in area_selectors:
                        area_elem = element.select_one(area_sel)
                        if area_elem:
                            print(f"   ✅ Area ({area_sel}): {area_elem.get_text().strip()[:30]}...")
                            break
                    else:
                        print("   ❌ Area: Not found")
                
                return best_selector, best_count
            
            else:
                print("\n❌ NO WORKING SELECTORS FOUND")
                
                # Fallback: analyze general page structure
                print("\n🔍 GENERAL PAGE STRUCTURE ANALYSIS:")
                print("-" * 35)
                
                # Look for any div with multiple children (likely property containers)
                all_divs = soup.find_all('div')
                div_analysis = {}
                
                for div in all_divs:
                    classes = div.get('class', [])
                    if classes:
                        class_str = ' '.join(classes)
                        if class_str not in div_analysis:
                            div_analysis[class_str] = 0
                        div_analysis[class_str] += 1
                
                # Sort by frequency
                sorted_divs = sorted(div_analysis.items(), key=lambda x: x[1], reverse=True)
                
                print("📊 Most common div classes:")
                for class_name, count in sorted_divs[:10]:
                    if count > 5:  # Only show classes that appear multiple times
                        print(f"   {class_name}: {count} occurrences")
                
                return None, 0
        
        except Exception as e:
            print(f"❌ Error investigating Delhi page: {str(e)}")
            return None, 0
    
    def test_mumbai_comparison(self):
        """Test Mumbai page for comparison"""
        
        print("\n🏙️ MUMBAI COMPARISON TEST")
        print("-" * 25)
        
        try:
            mumbai_url = "https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs"
            print(f"🔗 Loading: {mumbai_url}")
            
            self.driver.get(mumbai_url)
            time.sleep(5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Test primary selector
            primary_elements = soup.select("div.mb-srp__card")
            print(f"✅ Mumbai primary selector: {len(primary_elements)} elements")
            
            if primary_elements:
                print("✅ Mumbai uses standard selectors correctly")
                return True
            else:
                print("❌ Mumbai also has selector issues")
                return False
        
        except Exception as e:
            print(f"❌ Error testing Mumbai: {str(e)}")
            return False
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 WebDriver closed")
    
    def run_investigation(self):
        """Run complete investigation"""
        
        try:
            self.setup_driver()
            
            # Test Mumbai first (baseline)
            mumbai_works = self.test_mumbai_comparison()
            
            # Investigate Delhi
            delhi_selector, delhi_count = self.investigate_delhi_page_structure()
            
            # Summary
            print(f"\n📊 INVESTIGATION SUMMARY")
            print("="*30)
            print(f"Mumbai primary selector works: {mumbai_works}")
            print(f"Delhi best selector: {delhi_selector}")
            print(f"Delhi element count: {delhi_count}")
            
            if delhi_selector and delhi_count > 0:
                print("✅ Solution found for Delhi")
                return delhi_selector
            else:
                print("❌ No solution found - need manual inspection")
                return None
        
        finally:
            self.close()


def main():
    """Run Delhi selector investigation"""
    
    investigator = DelhiSelectorInvestigator()
    result = investigator.run_investigation()
    
    if result:
        print(f"\n🎯 RECOMMENDED SELECTOR FOR DELHI: {result}")
        return result
    else:
        print("\n⚠️ Manual investigation needed")
        return None


if __name__ == "__main__":
    main()
