#!/usr/bin/env python3
"""
Enhanced Pattern Validation Script
Tests the improved regex patterns and selectors based on comprehensive research findings.
"""

import re
import json
from pathlib import Path

def test_enhanced_area_patterns():
    """Test enhanced area extraction patterns"""
    
    print("🔬 Testing Enhanced Area Extraction Patterns")
    print("="*60)
    
    # Load configuration
    config_path = Path("config/scraper_config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    area_patterns = config['selectors']['area']['regex_patterns']
    
    # Test data from our research findings
    test_cases = {
        "apartments": [
            "Super Area 1500 sqft",
            "Carpet Area 1200 sqft", 
            "Built-up Area: 1800 sqft",
            "Super Area: 2,423 sqft",
            "Carpet Area: 1,850 sq ft"
        ],
        "houses": [
            "Carpet Area 800 sqft",
            "Super Area 1500 sqft",
            "Carpet Area 151 sqyrd",
            "Built-up Area: 200 sq yard",
            "Carpet Area: 1,200 sq ft"
        ],
        "plots": [
            "Plot Area 900 sqft",
            "Plot Area 4521 sqft",
            "Plot Area: 1,200 sq ft",
            "Plot Area 2 acres",
            "Land Area: 500 sqyrd"
        ]
    }
    
    results = {}
    
    for property_type, test_texts in test_cases.items():
        print(f"\n🏠 Testing {property_type.upper()}:")
        results[property_type] = {"total": len(test_texts), "matched": 0, "details": []}
        
        for text in test_texts:
            matched = False
            matched_pattern = None
            extracted_value = None
            
            for pattern in area_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    matched = True
                    matched_pattern = pattern
                    extracted_value = match.group(1) if match.groups() else match.group(0)
                    results[property_type]["matched"] += 1
                    break
            
            status = "✅" if matched else "❌"
            print(f"   {status} '{text}' -> {extracted_value or 'No match'}")
            
            results[property_type]["details"].append({
                "text": text,
                "matched": matched,
                "pattern": matched_pattern,
                "extracted": extracted_value
            })
    
    # Summary
    print(f"\n📊 AREA EXTRACTION SUMMARY:")
    for property_type, data in results.items():
        success_rate = (data["matched"] / data["total"]) * 100
        print(f"   {property_type.capitalize()}: {data['matched']}/{data['total']} ({success_rate:.1f}%)")
    
    return results

def test_enhanced_status_patterns():
    """Test enhanced status extraction patterns"""
    
    print("\n🏷️  Testing Enhanced Status Extraction Patterns")
    print("="*60)
    
    # Load configuration
    config_path = Path("config/scraper_config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    status_patterns = config['selectors']['status']['regex_patterns']
    
    # Test data from our research findings
    test_cases = {
        "apartments": [
            "Ready to Move",
            "Under Construction",
            "New Launch",
            "Possession by Dec '25",
            "Ready to Move In"
        ],
        "houses": [
            "Ready to Move",
            "Under Construction", 
            "New Property",
            "Resale",
            "Immediate Possession"
        ],
        "plots": [
            "Transaction: Resale",
            "Type: New",
            "Available for Sale",
            "Resale Plot",
            "New Development"
        ]
    }
    
    results = {}
    
    for property_type, test_texts in test_cases.items():
        print(f"\n🏠 Testing {property_type.upper()}:")
        results[property_type] = {"total": len(test_texts), "matched": 0, "details": []}
        
        for text in test_texts:
            matched = False
            matched_pattern = None
            extracted_value = None
            
            # Test regular status patterns
            for pattern in status_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    matched = True
                    matched_pattern = pattern
                    extracted_value = match.group(0)
                    results[property_type]["matched"] += 1
                    break
            
            # For plots, test transaction patterns
            if not matched and property_type == "plots":
                transaction_patterns = [
                    r'Transaction[:\s]*(\w+)',
                    r'(Resale|New|Available)',
                    r'Type[:\s]*(\w+)'
                ]
                
                for pattern in transaction_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        matched = True
                        matched_pattern = pattern
                        extracted_value = match.group(1) if match.groups() else match.group(0)
                        results[property_type]["matched"] += 1
                        break
            
            status = "✅" if matched else "❌"
            print(f"   {status} '{text}' -> {extracted_value or 'No match'}")
            
            results[property_type]["details"].append({
                "text": text,
                "matched": matched,
                "pattern": matched_pattern,
                "extracted": extracted_value
            })
    
    # Summary
    print(f"\n📊 STATUS EXTRACTION SUMMARY:")
    for property_type, data in results.items():
        success_rate = (data["matched"] / data["total"]) * 100
        print(f"   {property_type.capitalize()}: {data['matched']}/{data['total']} ({success_rate:.1f}%)")
    
    return results

def test_property_type_detection():
    """Test property type detection logic"""
    
    print("\n🔍 Testing Property Type Detection")
    print("="*60)
    
    # Test titles from our research
    test_titles = [
        "3 BHK Apartment for Sale in DLF Phase 1, Gurgaon",
        "4 BHK Independent House for Sale in Sector 57, Gurgaon", 
        "Residential Land / Plot in Sohna, Gurgaon",
        "2 BHK Builder Floor for Sale in Palam Vihar",
        "5 BHK Villa for Sale in Golf Course Road",
        "Residential Plot in Block I South City 1, Gurgaon"
    ]
    
    plot_keywords = ["Plot", "Land", "plot", "land"]
    house_keywords = ["house", "villa", "independent"]
    
    for title in test_titles:
        is_plot = any(keyword in title for keyword in plot_keywords)
        is_house = any(keyword in title.lower() for keyword in house_keywords)
        
        if is_plot:
            property_type = "PLOT"
        elif is_house:
            property_type = "HOUSE"
        else:
            property_type = "APARTMENT"
        
        print(f"   📋 '{title[:50]}...'")
        print(f"      -> Detected as: {property_type}")
    
    return True

def main():
    """Main validation function"""
    
    print("🚀 Enhanced Pattern Validation Script")
    print("Testing improved patterns based on comprehensive research...")
    print()
    
    try:
        # Test area patterns
        area_results = test_enhanced_area_patterns()
        
        # Test status patterns  
        status_results = test_enhanced_status_patterns()
        
        # Test property type detection
        test_property_type_detection()
        
        # Overall summary
        print("\n" + "="*80)
        print("🎯 OVERALL VALIDATION SUMMARY")
        print("="*80)
        
        total_area_tests = sum(data["total"] for data in area_results.values())
        total_area_matches = sum(data["matched"] for data in area_results.values())
        area_success_rate = (total_area_matches / total_area_tests) * 100
        
        total_status_tests = sum(data["total"] for data in status_results.values())
        total_status_matches = sum(data["matched"] for data in status_results.values())
        status_success_rate = (total_status_matches / total_status_tests) * 100
        
        print(f"📏 Area Pattern Success: {total_area_matches}/{total_area_tests} ({area_success_rate:.1f}%)")
        print(f"🏷️  Status Pattern Success: {total_status_matches}/{total_status_tests} ({status_success_rate:.1f}%)")
        
        if area_success_rate >= 90 and status_success_rate >= 80:
            print("\n✅ VALIDATION PASSED - Enhanced patterns are ready for production!")
        else:
            print("\n⚠️  VALIDATION NEEDS IMPROVEMENT - Some patterns need refinement")
        
        # Save results
        validation_results = {
            "area_results": area_results,
            "status_results": status_results,
            "summary": {
                "area_success_rate": area_success_rate,
                "status_success_rate": status_success_rate,
                "overall_status": "PASSED" if area_success_rate >= 90 and status_success_rate >= 80 else "NEEDS_IMPROVEMENT"
            }
        }
        
        with open("enhanced_pattern_validation_results.json", 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: enhanced_pattern_validation_results.json")
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
