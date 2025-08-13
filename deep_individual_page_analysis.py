#!/usr/bin/env python3
"""
Deep Individual Property Page Analysis
Comprehensive investigation into why individual property pages are blocked
Runs in NON-HEADLESS mode for visual observation
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import requests
from bs4 import BeautifulSoup
import json

def deep_individual_page_analysis():
    """Comprehensive analysis of individual property page blocking"""
    
    print('🔍 DEEP INDIVIDUAL PROPERTY PAGE ANALYSIS')
    print('=' * 60)
    print('🎯 Goal: Understand why individual property pages return "Access Denied"')
    print('👁️ Running in NON-HEADLESS mode for visual observation')
    print('=' * 60)
    
    # Test URLs - we'll get these from a quick listing page scrape first
    test_urls = []
    
    print('\n📋 STEP 1: Getting Individual Property URLs from Listing Page')
    print('-' * 50)
    
    # First, get some individual property URLs
    listing_driver = setup_non_headless_driver("Listing Page Browser")
    
    try:
        listing_url = 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs'
        print(f'🔗 Navigating to listing page: {listing_url}')
        listing_driver.get(listing_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Extract property URLs
        soup = BeautifulSoup(listing_driver.page_source, 'html.parser')
        property_cards = soup.select('.mb-srp__card')
        
        print(f'📊 Found {len(property_cards)} property cards')
        
        for i, card in enumerate(property_cards[:5]):  # Get first 5 URLs
            # Look for property URLs
            links = card.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'pdpid' in href and 'magicbricks.com' in href:
                    if href.startswith('/'):
                        href = 'https://www.magicbricks.com' + href
                    test_urls.append(href)
                    print(f'   ✅ Found URL {len(test_urls)}: {href}')
                    break
            
            if len(test_urls) >= 3:  # Get 3 test URLs
                break
        
        print(f'\n✅ Collected {len(test_urls)} individual property URLs for testing')
        
    except Exception as e:
        print(f'❌ Error getting URLs from listing page: {str(e)}')
        # Fallback URLs from previous testing
        test_urls = [
            'https://www.magicbricks.com/rof-pravasa-sector-88a-gurgaon-pdpid-4d4235343330303431',
            'https://www.magicbricks.com/ansal-sushant-lok-i-sushant-lok-1-block-e-gurgaon-pdpid-4d4235323836303037',
            'https://www.magicbricks.com/southend-floors-sector-49-gurgaon-pdpid-4d4235303130343331'
        ]
        print(f'🔄 Using fallback URLs: {len(test_urls)} URLs')
    
    finally:
        listing_driver.quit()
    
    if not test_urls:
        print('❌ No test URLs available. Cannot proceed with analysis.')
        return
    
    print(f'\n📋 STEP 2: Testing Individual Property Page Access')
    print('-' * 50)
    
    # Test each URL with different approaches
    for i, url in enumerate(test_urls):
        print(f'\n🏡 TESTING URL {i+1}: {url}')
        print('=' * 80)
        
        # Test 1: Direct access with standard browser
        print('\n🧪 TEST 1: Direct Access with Standard Browser')
        test_direct_access(url)
        
        # Test 2: Access with referrer from listing page
        print('\n🧪 TEST 2: Access with Proper Referrer')
        test_with_referrer(url)
        
        # Test 3: Access after navigating from listing page
        print('\n🧪 TEST 3: Navigation from Listing Page')
        test_navigation_flow(url)
        
        # Test 4: Different user agents
        print('\n🧪 TEST 4: Different User Agents')
        test_different_user_agents(url)
        
        # Test 5: Requests library (non-browser)
        print('\n🧪 TEST 5: Non-Browser Access (Requests)')
        test_requests_access(url)
        
        print('\n' + '='*80)
        
        # Only test first URL in detail to avoid overwhelming
        if i == 0:
            input('\n⏸️ Press Enter to continue with next URL or Ctrl+C to stop...')

def setup_non_headless_driver(window_title="MagicBricks Analysis"):
    """Setup Chrome driver in NON-HEADLESS mode for visual observation"""
    
    options = Options()
    
    # NON-HEADLESS mode for visual observation
    # options.add_argument('--headless')  # COMMENTED OUT
    
    # Standard options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Anti-detection options
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Set window title for identification
        driver.execute_script(f"document.title = '{window_title}';")
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    except Exception as e:
        print(f'❌ Error setting up Chrome driver: {str(e)}')
        raise

def test_direct_access(url):
    """Test direct access to individual property page"""
    
    print(f'   🔗 Direct access to: {url}')
    
    driver = setup_non_headless_driver("Direct Access Test")
    
    try:
        start_time = time.time()
        driver.get(url)
        load_time = time.time() - start_time
        
        # Wait a bit for page to fully load
        time.sleep(3)
        
        # Check page title and content
        title = driver.title
        page_source = driver.page_source
        
        print(f'   ⏱️ Load time: {load_time:.2f} seconds')
        print(f'   📄 Page title: "{title}"')
        print(f'   📊 Page length: {len(page_source)} characters')
        
        # Check for access denied indicators
        if 'access denied' in title.lower() or 'access denied' in page_source.lower():
            print('   ❌ ACCESS DENIED detected')
            
            # Look for specific error messages
            soup = BeautifulSoup(page_source, 'html.parser')
            error_elements = soup.find_all(text=lambda text: text and 'access denied' in text.lower())
            if error_elements:
                print(f'   🔍 Error message: "{error_elements[0][:200]}..."')
        
        elif 'property' in title.lower() or len(page_source) > 50000:
            print('   ✅ Page appears to have loaded successfully')
            
            # Check for property content
            soup = BeautifulSoup(page_source, 'html.parser')
            property_indicators = soup.find_all(text=lambda text: text and any(keyword in text.lower() for keyword in ['bhk', 'sqft', 'crore', 'lakh']))
            print(f'   🏠 Property content indicators found: {len(property_indicators)}')
        
        else:
            print('   ⚠️ Unclear page state - may be blocked or loading')
        
        # Take a screenshot for analysis
        try:
            screenshot_path = f'direct_access_screenshot_{int(time.time())}.png'
            driver.save_screenshot(screenshot_path)
            print(f'   📸 Screenshot saved: {screenshot_path}')
        except:
            pass
        
        # Wait for manual observation
        print('   👁️ Browser window is open for manual observation...')
        time.sleep(5)
        
    except Exception as e:
        print(f'   ❌ Error during direct access: {str(e)}')
    
    finally:
        driver.quit()

def test_with_referrer(url):
    """Test access with proper referrer header"""
    
    print(f'   🔗 Access with referrer: {url}')
    
    driver = setup_non_headless_driver("Referrer Test")
    
    try:
        # First navigate to listing page to establish referrer
        listing_url = 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs'
        print(f'   📋 First visiting listing page: {listing_url}')
        driver.get(listing_url)
        time.sleep(2)
        
        # Now navigate to individual page
        print(f'   🔗 Now navigating to individual page with referrer')
        driver.get(url)
        time.sleep(3)
        
        title = driver.title
        print(f'   📄 Page title: "{title}"')
        
        if 'access denied' in title.lower():
            print('   ❌ Still ACCESS DENIED with referrer')
        else:
            print('   ✅ Referrer approach may have worked')
        
        time.sleep(3)
        
    except Exception as e:
        print(f'   ❌ Error with referrer test: {str(e)}')
    
    finally:
        driver.quit()

def test_navigation_flow(url):
    """Test accessing individual page by clicking from listing page"""
    
    print(f'   🖱️ Navigation flow test for: {url}')
    
    driver = setup_non_headless_driver("Navigation Flow Test")
    
    try:
        # Navigate to listing page
        listing_url = 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs'
        print(f'   📋 Navigating to listing page: {listing_url}')
        driver.get(listing_url)
        time.sleep(3)
        
        # Try to find and click a link that matches our target URL
        print(f'   🔍 Looking for clickable link to target property...')
        
        # Extract the property ID from URL
        if 'pdpid-' in url:
            property_id = url.split('pdpid-')[1]
            print(f'   🆔 Looking for property ID: {property_id}')
            
            # Look for links containing this property ID
            links = driver.find_elements(By.TAG_NAME, 'a')
            target_link = None
            
            for link in links:
                href = link.get_attribute('href')
                if href and property_id in href:
                    target_link = link
                    print(f'   ✅ Found matching link: {href}')
                    break
            
            if target_link:
                print(f'   🖱️ Clicking on property link...')
                driver.execute_script("arguments[0].click();", target_link)
                time.sleep(5)
                
                title = driver.title
                print(f'   📄 After click - Page title: "{title}"')
                
                if 'access denied' in title.lower():
                    print('   ❌ Still ACCESS DENIED after navigation flow')
                else:
                    print('   ✅ Navigation flow may have worked!')
            else:
                print('   ⚠️ Could not find matching link on listing page')
        
        time.sleep(3)
        
    except Exception as e:
        print(f'   ❌ Error with navigation flow test: {str(e)}')
    
    finally:
        driver.quit()

def test_different_user_agents(url):
    """Test with different user agents"""
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ]
    
    for i, user_agent in enumerate(user_agents):
        print(f'   🤖 Testing User Agent {i+1}: {user_agent[:50]}...')
        
        options = Options()
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(2)
            
            title = driver.title
            if 'access denied' in title.lower():
                print(f'   ❌ User Agent {i+1}: ACCESS DENIED')
            else:
                print(f'   ✅ User Agent {i+1}: May have worked - "{title[:50]}..."')
            
            driver.quit()
            
        except Exception as e:
            print(f'   ❌ User Agent {i+1}: Error - {str(e)}')

def test_requests_access(url):
    """Test access using requests library (non-browser)"""
    
    print(f'   📡 Testing requests library access: {url}')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f'   📊 Status Code: {response.status_code}')
        print(f'   📄 Content Length: {len(response.text)} characters')
        
        if response.status_code == 200:
            if 'access denied' in response.text.lower():
                print('   ❌ Requests: ACCESS DENIED in content')
            else:
                print('   ✅ Requests: May have worked')
        else:
            print(f'   ❌ Requests: HTTP {response.status_code}')
        
    except Exception as e:
        print(f'   ❌ Requests error: {str(e)}')

if __name__ == "__main__":
    try:
        deep_individual_page_analysis()
    except KeyboardInterrupt:
        print('\n\n⏹️ Analysis stopped by user')
    except Exception as e:
        print(f'\n\n❌ Analysis failed: {str(e)}')
    
    print('\n🎯 Analysis complete. Check browser windows and screenshots for visual evidence.')
