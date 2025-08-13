#!/usr/bin/env python3
"""
Manual test to verify URL extraction on live MagicBricks page
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


def test_url_extraction_manually():
    """Manually test URL extraction on live page"""
    
    print("🔍 MANUAL URL EXTRACTION TEST")
    print("=" * 50)
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to MagicBricks Gurgaon page
        url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all property cards
        cards = soup.select('.mb-srp__card')
        print(f"📋 Found {len(cards)} property cards")
        
        if len(cards) == 0:
            print("❌ No property cards found! Checking alternative selectors...")
            # Try alternative selectors
            alt_selectors = ['.SRPTuple', '.property-card', '.listing-card', '[class*="card"]']
            for selector in alt_selectors:
                alt_cards = soup.select(selector)
                if alt_cards:
                    print(f"   ✅ Found {len(alt_cards)} cards with selector: {selector}")
                    cards = alt_cards[:5]  # Take first 5
                    break
        
        # Test URL extraction on first 5 cards
        url_selectors = [
            'a[href*="pdpid"]',  # Most common current pattern
            'a[href*="propertyDetails"]',
            'a[href*="property-details"]',
            'a[href*="/property/"]',
            'a[href*="propertydetail"]',
            'h2.mb-srp__card--title a',
            'h2 a[href]',
            'a[class*="title"]',
            '.mb-srp__card--title a',
            'a[href]'  # Any link
        ]
        
        print(f"\n🔍 Testing URL extraction on first 5 cards:")
        print("-" * 50)
        
        for i, card in enumerate(cards[:5]):
            print(f"\nCard {i+1}:")
            
            # Try to extract title first
            title_selectors = ['h2.mb-srp__card--title', 'h2', 'h3', '.title', '[class*="title"]']
            title = "Unknown"
            for title_sel in title_selectors:
                title_elem = card.select_one(title_sel)
                if title_elem:
                    title = title_elem.get_text(strip=True)[:50]
                    break
            
            print(f"   Title: {title}")
            
            # Test each URL selector
            found_url = False
            for selector in url_selectors:
                try:
                    url_elem = card.select_one(selector)
                    if url_elem and url_elem.get('href'):
                        url = url_elem.get('href')
                        if url and ('property' in url or 'pdpid' in url):
                            print(f"   ✅ URL found with '{selector}': {url[:80]}...")
                            found_url = True
                            break
                except Exception as e:
                    continue
            
            if not found_url:
                print(f"   ❌ NO URL FOUND")
                # Debug: show all links in this card
                all_links = card.select('a[href]')
                print(f"   🔍 All links in card ({len(all_links)}):")
                for j, link in enumerate(all_links[:3]):  # Show first 3 links
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:30]
                    print(f"      {j+1}. {href[:50]} | Text: {text}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        cards_with_urls = 0
        for card in cards[:10]:  # Check first 10 cards
            for selector in url_selectors:
                try:
                    url_elem = card.select_one(selector)
                    if url_elem and url_elem.get('href'):
                        url = url_elem.get('href')
                        if url and ('property' in url or 'pdpid' in url):
                            cards_with_urls += 1
                            break
                except Exception:
                    continue
        
        print(f"   📋 Cards checked: {min(10, len(cards))}")
        print(f"   ✅ Cards with URLs: {cards_with_urls}")
        print(f"   ❌ Cards without URLs: {min(10, len(cards)) - cards_with_urls}")
        print(f"   📈 URL extraction rate: {(cards_with_urls / min(10, len(cards))) * 100:.1f}%")
        
        if cards_with_urls < min(10, len(cards)) * 0.7:  # Less than 70%
            print(f"\n🚨 ISSUE CONFIRMED: URL extraction rate is too low!")
            print(f"   Expected: >90% of properties should have URLs")
            print(f"   Actual: {(cards_with_urls / min(10, len(cards))) * 100:.1f}%")
            return False
        else:
            print(f"\n✅ URL extraction looks normal")
            return True
            
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")
        return False
    finally:
        driver.quit()


def main():
    """Run manual URL extraction test"""
    
    success = test_url_extraction_manually()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ URL EXTRACTION WORKING NORMALLY")
        print("   The 31.3% missing URLs might be expected")
    else:
        print("❌ URL EXTRACTION HAS ISSUES")
        print("   Need to investigate and fix URL selectors")
    
    return success


if __name__ == "__main__":
    main()
