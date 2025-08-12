#!/usr/bin/env python3
"""
Manual Property Checker
Helps manually verify the 8 excluded properties from the scraping analysis.
"""

import webbrowser
import time
from bs4 import BeautifulSoup
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def main():
    print("=" * 80)
    print("MANUAL PROPERTY CHECKER")
    print("=" * 80)
    
    # The URL where 30 properties were found
    target_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
    
    print(f"\n📍 TARGET URL: {target_url}")
    print("\n🔍 ANALYSIS SUMMARY:")
    print("   • Total properties found: 30")
    print("   • Successfully extracted: 22 (73.3%)")
    print("   • Failed extractions: 8 (26.7%)")
    print("   • Failed property indices: 4, 9, 11, 14, 17, 19, 22, 24")
    
    print("\n❌ COMMON ISSUES WITH FAILED PROPERTIES:")
    print("   • Missing valid property URLs (5/8 cards)")
    print("   • Missing area information (8/8 cards)")
    print("   • Cards with 'card-luxury' and 'preferred-agent' classes")
    print("   • Incomplete HTML structures")
    
    print("\n🔧 RECOMMENDED MANUAL CHECKS:")
    print("   1. Verify if properties are actually visible on the page")
    print("   2. Check if they are premium/sponsored listings")
    print("   3. Look for different HTML structure patterns")
    print("   4. Identify missing data fields (price, area, links)")
    print("   5. Check for dynamic content loading")
    
    # Ask user if they want to open the URL
    print("\n" + "="*50)
    user_input = input("\n🌐 Would you like to open the URL in your browser? (y/n): ").lower().strip()
    
    if user_input in ['y', 'yes']:
        print("\n🚀 Opening URL in your default browser...")
        webbrowser.open(target_url)
        print("\n✅ URL opened! Please manually check the properties.")
        
        print("\n📋 MANUAL INSPECTION CHECKLIST:")
        print("   □ Count total visible properties on the page")
        print("   □ Look for properties without clickable links")
        print("   □ Identify premium/sponsored listings")
        print("   □ Check for properties missing area information")
        print("   □ Note any properties with different visual styling")
        print("   □ Check if page requires scrolling to load more properties")
        print("   □ Look for properties that might be ads or promotions")
        
    else:
        print("\n📝 You can manually visit this URL later:")
        print(f"   {target_url}")
    
    # Provide additional analysis from saved HTML
    print("\n" + "="*50)
    print("\n📊 DETAILED ANALYSIS FROM SAVED HTML:")
    
    try:
        # Read the saved HTML file
        with open('debug_bot_detection.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all property cards
        cards = soup.find_all('div', class_='mb-srp__card')
        print(f"\n   • Total cards found in saved HTML: {len(cards)}")
        
        # Analyze failed property indices
        failed_indices = [4, 9, 11, 14, 17, 19, 22, 24]
        
        print("\n🔍 FAILED PROPERTIES ANALYSIS:")
        for i, idx in enumerate(failed_indices):
            if idx < len(cards):
                card = cards[idx]
                print(f"\n   Property {idx + 1} (Index {idx}):")
                
                # Check for links
                links = card.find_all('a', href=True)
                print(f"     • Links found: {len(links)}")
                
                # Check for specific classes
                classes = card.get('class', [])
                special_classes = [cls for cls in classes if cls in ['card-luxury', 'preferred-agent', 'premium']]
                if special_classes:
                    print(f"     • Special classes: {', '.join(special_classes)}")
                
                # Check for area information
                area_selectors = ['.mb-srp__card--carpet-area', '.area', '[class*="area"]', '.carpet-area']
                area_found = False
                for selector in area_selectors:
                    if card.select(selector):
                        area_found = True
                        break
                print(f"     • Area information: {'Found' if area_found else 'Missing'}")
                
                # Check for price
                price_elem = card.find('div', class_='mb-srp__card__price--amount')
                print(f"     • Price information: {'Found' if price_elem else 'Missing'}")
                
                # Check for title
                title_elem = card.find('h2', class_='mb-srp__card--title')
                print(f"     • Title information: {'Found' if title_elem else 'Missing'}")
        
    except FileNotFoundError:
        print("\n   ⚠️  Saved HTML file not found. Run the scraper first to generate debug_bot_detection.html")
    except Exception as e:
        print(f"\n   ❌ Error analyzing saved HTML: {e}")
    
    print("\n" + "="*80)
    print("\n💡 NEXT STEPS:")
    print("   1. Visit the URL and manually count properties")
    print("   2. Compare with our analysis of 30 found vs 22 extracted")
    print("   3. Identify patterns in failed extractions")
    print("   4. Report findings for scraper improvement")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()