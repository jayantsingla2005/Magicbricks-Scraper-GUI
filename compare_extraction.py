#!/usr/bin/env python3
"""
Compare field extraction improvements between old and new scraper versions
"""

import pandas as pd
from pathlib import Path


def analyze_field_completeness(csv_file, label):
    """Analyze field completeness for a CSV file"""
    print(f"\n📊 {label}")
    print("=" * 50)
    
    df = pd.read_csv(csv_file)
    total_properties = len(df)
    
    print(f"📈 Total Properties: {total_properties}")
    
    # Focus on the fields we're trying to improve
    target_fields = ['super_area', 'society', 'status']
    
    print(f"\n🎯 TARGET FIELD IMPROVEMENTS:")
    print("-" * 30)
    
    field_stats = {}
    for field in target_fields:
        non_empty = df[field].notna().sum()
        percentage = (non_empty / total_properties) * 100
        field_stats[field] = percentage
        print(f"   {field:12}: {non_empty:2d}/{total_properties} ({percentage:5.1f}%)")
    
    # Also check other important fields
    other_fields = ['title', 'price', 'property_type', 'bedrooms', 'locality', 'furnishing', 'owner_name']
    
    print(f"\n📋 OTHER IMPORTANT FIELDS:")
    print("-" * 30)
    
    for field in other_fields:
        non_empty = df[field].notna().sum()
        percentage = (non_empty / total_properties) * 100
        field_stats[field] = percentage
        print(f"   {field:12}: {non_empty:2d}/{total_properties} ({percentage:5.1f}%)")
    
    return field_stats


def compare_improvements(old_stats, new_stats):
    """Compare improvements between old and new extraction"""
    print(f"\n🔍 IMPROVEMENT ANALYSIS")
    print("=" * 50)
    
    target_fields = ['super_area', 'society', 'status']
    
    print(f"📈 TARGET FIELD IMPROVEMENTS:")
    print("-" * 40)
    print(f"{'Field':<12} {'Before':<8} {'After':<8} {'Change':<10}")
    print("-" * 40)
    
    improvements = {}
    for field in target_fields:
        old_pct = old_stats.get(field, 0)
        new_pct = new_stats.get(field, 0)
        change = new_pct - old_pct
        improvements[field] = change
        
        change_str = f"+{change:.1f}%" if change > 0 else f"{change:.1f}%"
        print(f"{field:<12} {old_pct:>6.1f}%  {new_pct:>6.1f}%  {change_str:>8}")
    
    # Overall assessment
    print(f"\n🎯 IMPROVEMENT SUMMARY:")
    print("-" * 30)
    
    total_improvement = sum(improvements.values())
    improved_fields = sum(1 for change in improvements.values() if change > 0)
    
    print(f"   Fields Improved: {improved_fields}/{len(target_fields)}")
    print(f"   Total Improvement: {total_improvement:.1f} percentage points")
    
    if total_improvement > 5:
        print("   ✅ SIGNIFICANT IMPROVEMENT!")
    elif total_improvement > 0:
        print("   ✅ Positive improvement")
    else:
        print("   ⚠️  No improvement detected")
    
    return improvements


def main():
    """Main comparison function"""
    print("🔍 FIELD EXTRACTION IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # Find the files to compare
    output_dir = Path('output')
    
    # Get the two most recent CSV files
    csv_files = sorted(output_dir.glob('magicbricks_properties_*.csv'), 
                      key=lambda x: x.stat().st_mtime, reverse=True)
    
    if len(csv_files) < 2:
        print("❌ Need at least 2 CSV files to compare. Please run the scraper again.")
        return
    
    new_file = csv_files[0]  # Most recent
    old_file = csv_files[1]  # Previous
    
    print(f"📁 Comparing:")
    print(f"   Before: {old_file.name}")
    print(f"   After:  {new_file.name}")
    
    # Analyze both files
    old_stats = analyze_field_completeness(old_file, "BEFORE (Previous Version)")
    new_stats = analyze_field_completeness(new_file, "AFTER (Enhanced Selectors)")
    
    # Compare improvements
    improvements = compare_improvements(old_stats, new_stats)
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 30)
    
    for field, change in improvements.items():
        if change < 5:  # Less than 5% improvement
            print(f"   🔧 {field}: Needs further optimization")
        else:
            print(f"   ✅ {field}: Good improvement achieved")
    
    print(f"\n📊 Next steps:")
    print("   1. If improvements are significant, commit changes")
    print("   2. If improvements are minimal, investigate selectors further")
    print("   3. Test on larger sample (5-10 pages) for validation")


if __name__ == "__main__":
    main()
