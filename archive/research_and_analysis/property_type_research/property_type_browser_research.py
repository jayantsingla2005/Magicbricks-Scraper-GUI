#!/usr/bin/env python3
"""
Browser-based research tool to analyze different property types
Uses Playwright to systematically examine HTML structure variations
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
from pathlib import Path


class PropertyTypeBrowserResearch:
    """Browser-based research for property type analysis"""
    
    def __init__(self):
        self.research_urls = {
            "Apartments": "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs",
            "Houses": "https://www.magicbricks.com/independent-house-for-sale-in-gurgaon-pppfs", 
            "Villas": "https://www.magicbricks.com/villa-for-sale-in-gurgaon-pppfs",
            "Builder Floors": "https://www.magicbricks.com/builder-floor-for-sale-in-gurgaon-pppfs",
            "Plots": "https://www.magicbricks.com/residential-plots-land-for-sale-in-gurgaon-pppfs",
            "Penthouses": "https://www.magicbricks.com/penthouse-for-sale-in-gurgaon-pppfs"
        }
        self.results = {}
    
    async def analyze_property_type(self, browser, property_type: str, url: str):
        """Analyze a specific property type"""
        print(f"\n🔍 ANALYZING: {property_type}")
        print(f"🔗 URL: {url}")
        
        page = await browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Find property cards
            property_cards = await page.query_selector_all('.mb-srp__card')
            print(f"📊 Found {len(property_cards)} property cards")
            
            if len(property_cards) == 0:
                print("❌ No property cards found!")
                return {"error": "No property cards found"}
            
            # Analyze first 5 cards for patterns
            card_analysis = []
            
            for i, card in enumerate(property_cards[:5]):
                print(f"   Analyzing card {i+1}...")
                
                # Get card HTML and text
                card_html = await card.inner_html()
                card_text = await card.inner_text()
                
                # Extract key information
                card_info = {
                    "card_index": i + 1,
                    "html_length": len(card_html),
                    "text_length": len(card_text)
                }
                
                # Look for title
                title_element = await card.query_selector('h2')
                if title_element:
                    card_info["title"] = await title_element.inner_text()
                
                # Look for price patterns
                price_patterns = await page.evaluate('''(card) => {
                    const text = card.textContent;
                    const priceMatches = text.match(/₹[\\s\\d.,]+(?:Cr|Lac|crore|lakh)/gi);
                    return priceMatches || [];
                }''', card)
                card_info["price_patterns"] = price_patterns
                
                # Look for area patterns
                area_patterns = await page.evaluate('''(card) => {
                    const text = card.textContent;
                    const areaMatches = text.match(/\\d+[\\s,]*(?:sqft|sq\\.?\\s*ft|sq\\.?\\s*yards?|acres?)/gi);
                    return areaMatches || [];
                }''', card)
                card_info["area_patterns"] = area_patterns
                
                # Look for society/project links
                society_links = await card.query_selector_all('a[href*="pdpid"]')
                card_info["society_links"] = len(society_links)
                if society_links:
                    card_info["society_text"] = await society_links[0].inner_text()
                
                # Look for status patterns
                status_patterns = await page.evaluate('''(card) => {
                    const text = card.textContent;
                    const statusMatches = text.match(/(?:Ready to Move|Under Construction|Possession|New Launch)/gi);
                    return statusMatches || [];
                }''', card)
                card_info["status_patterns"] = status_patterns
                
                # Check for unique elements in this property type
                unique_elements = await page.evaluate('''(card) => {
                    const elements = [];
                    
                    // Look for plot-specific elements
                    if (card.textContent.includes('Plot') || card.textContent.includes('Land')) {
                        elements.push('plot_specific');
                    }
                    
                    // Look for villa-specific elements
                    if (card.textContent.includes('Villa') || card.textContent.includes('Independent')) {
                        elements.push('villa_specific');
                    }
                    
                    // Look for apartment-specific elements
                    if (card.textContent.includes('Apartment') || card.textContent.includes('Flat')) {
                        elements.push('apartment_specific');
                    }
                    
                    // Look for floor-specific elements
                    if (card.textContent.includes('Floor') && card.textContent.includes('out of')) {
                        elements.push('floor_specific');
                    }
                    
                    return elements;
                }''', card)
                card_info["unique_elements"] = unique_elements
                
                card_analysis.append(card_info)
            
            # Overall page analysis
            page_analysis = {
                "property_type": property_type,
                "url": url,
                "total_cards": len(property_cards),
                "cards_analyzed": len(card_analysis),
                "card_details": card_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Look for property type specific patterns
            page_text = await page.inner_text('body')
            
            # Identify unique patterns for this property type
            type_specific_patterns = {
                "has_plot_area": "plot" in page_text.lower() and "area" in page_text.lower(),
                "has_built_up_area": "built" in page_text.lower() and "area" in page_text.lower(),
                "has_floor_info": "floor" in page_text.lower() and "out of" in page_text.lower(),
                "has_possession_date": "possession" in page_text.lower(),
                "has_villa_amenities": any(word in page_text.lower() for word in ["swimming", "garden", "parking", "security"]),
                "price_format_variations": len(set(card["price_patterns"] for card in card_analysis if card["price_patterns"]))
            }
            
            page_analysis["type_specific_patterns"] = type_specific_patterns
            
            print(f"✅ Analysis complete for {property_type}")
            return page_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {property_type}: {str(e)}")
            return {"error": str(e), "property_type": property_type}
        
        finally:
            await page.close()
    
    async def run_comprehensive_analysis(self):
        """Run comprehensive analysis across all property types"""
        print("🔬 COMPREHENSIVE PROPERTY TYPE ANALYSIS")
        print("=" * 80)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                for property_type, url in self.research_urls.items():
                    result = await self.analyze_property_type(browser, property_type, url)
                    self.results[property_type] = result
                    
                    # Small delay between requests
                    await asyncio.sleep(2)
                
            finally:
                await browser.close()
        
        # Save results
        output_file = f"property_type_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {output_file}")
        
        # Generate summary
        self.generate_analysis_summary()
        
        return self.results
    
    def generate_analysis_summary(self):
        """Generate summary of findings"""
        print(f"\n📊 PROPERTY TYPE ANALYSIS SUMMARY")
        print("=" * 60)
        
        successful_analyses = {k: v for k, v in self.results.items() if "error" not in v}
        failed_analyses = {k: v for k, v in self.results.items() if "error" in v}
        
        print(f"✅ Successful analyses: {len(successful_analyses)}")
        print(f"❌ Failed analyses: {len(failed_analyses)}")
        
        if failed_analyses:
            print(f"\n❌ FAILED ANALYSES:")
            for prop_type, result in failed_analyses.items():
                print(f"   • {prop_type}: {result.get('error', 'Unknown error')}")
        
        if successful_analyses:
            print(f"\n📈 SUCCESSFUL ANALYSES:")
            
            for prop_type, result in successful_analyses.items():
                print(f"\n🏠 {prop_type.upper()}:")
                print(f"   Cards found: {result['total_cards']}")
                
                # Analyze patterns across cards
                all_price_patterns = []
                all_area_patterns = []
                all_status_patterns = []
                
                for card in result['card_details']:
                    all_price_patterns.extend(card.get('price_patterns', []))
                    all_area_patterns.extend(card.get('area_patterns', []))
                    all_status_patterns.extend(card.get('status_patterns', []))
                
                print(f"   Price patterns: {len(set(all_price_patterns))} unique")
                print(f"   Area patterns: {len(set(all_area_patterns))} unique")
                print(f"   Status patterns: {len(set(all_status_patterns))} unique")
                
                # Type-specific insights
                patterns = result.get('type_specific_patterns', {})
                insights = []
                if patterns.get('has_plot_area'):
                    insights.append("Plot area data")
                if patterns.get('has_floor_info'):
                    insights.append("Floor information")
                if patterns.get('has_villa_amenities'):
                    insights.append("Villa amenities")
                
                if insights:
                    print(f"   Unique features: {', '.join(insights)}")
        
        print(f"\n💡 KEY INSIGHTS:")
        print("   • Different property types may have different HTML structures")
        print("   • Area data patterns vary by property type")
        print("   • Price formats may differ across property types")
        print("   • Status information presentation varies")
        
        print(f"\n🚀 NEXT STEPS:")
        print("   1. Analyze specific differences in HTML structure")
        print("   2. Update selectors to handle property type variations")
        print("   3. Test extraction improvements across all types")


async def main():
    """Main function"""
    researcher = PropertyTypeBrowserResearch()
    await researcher.run_comprehensive_analysis()


if __name__ == "__main__":
    asyncio.run(main())
