#!/usr/bin/env python3
"""
Fixed Property Type Analysis
Corrected analysis of field extraction across property types
"""

import pandas as pd
from collections import defaultdict

def analyze_existing_data():
    """Analyze the existing scraped data for property type validation"""
    
    print('🔍 FIXED PROPERTY TYPE ANALYSIS')
    print('=' * 60)
    print('📊 Analyzing existing scraped data for property type validation')
    print('=' * 60)
    
    # Load the existing data
    try:
        df = pd.read_csv('comprehensive_property_type_analysis.csv')
        print(f'✅ Loaded {len(df)} properties from existing data')
    except FileNotFoundError:
        print('❌ No existing data file found. Please run the scraper first.')
        return
    
    print('\n📋 STEP 1: Property Type Distribution Analysis')
    print('-' * 50)
    
    # Analyze actual property types
    property_types = df['property_type'].value_counts()
    
    print('📊 ACTUAL PROPERTY TYPE DISTRIBUTION:')
    for prop_type, count in property_types.items():
        percentage = (count / len(df)) * 100
        print(f'   🏠 {prop_type}: {count} properties ({percentage:.1f}%)')
    
    # Categorize property types
    categorized_types = categorize_property_types(df)
    
    print('\n📊 CATEGORIZED PROPERTY TYPE DISTRIBUTION:')
    for category, properties in categorized_types.items():
        count = len(properties)
        percentage = (count / len(df)) * 100
        print(f'   🏠 {category}: {count} properties ({percentage:.1f}%)')
    
    print('\n📋 STEP 2: Field Extraction Analysis by Category')
    print('-' * 50)
    
    # Critical fields to analyze
    critical_fields = [
        'title', 'price', 'area', 'locality', 'society', 'status', 
        'description', 'photo_count', 'owner_name', 'contact_options'
    ]
    
    # Analyze field completeness by category
    category_analysis = {}
    
    for category, properties in categorized_types.items():
        if len(properties) == 0:
            continue
            
        print(f'\n🏠 {category.upper()} ({len(properties)} properties):')
        print('-' * 40)
        
        category_data = {
            'category': category,
            'sample_size': len(properties),
            'properties': properties
        }
        
        for field in critical_fields:
            filled_count = sum(1 for _, prop in properties.iterrows() 
                             if pd.notna(prop.get(field)) and str(prop.get(field)).strip())
            completeness = (filled_count / len(properties)) * 100
            
            status = '✅' if completeness >= 90 else '⚠️' if completeness >= 70 else '❌'
            print(f'   {status} {field}: {completeness:.1f}% ({filled_count}/{len(properties)})')
            
            category_data[f'{field}_completeness'] = completeness
            category_data[f'{field}_filled'] = filled_count
        
        category_analysis[category] = category_data
    
    print('\n📋 STEP 3: Cross-Category Consistency Analysis')
    print('-' * 50)
    
    # Analyze consistency across categories
    field_consistency = {}
    
    for field in critical_fields:
        field_values = []
        for category, data in category_analysis.items():
            completeness = data.get(f'{field}_completeness', 0)
            field_values.append(completeness)
        
        if field_values:
            avg_completeness = sum(field_values) / len(field_values)
            min_completeness = min(field_values)
            max_completeness = max(field_values)
            variance = max_completeness - min_completeness
            
            consistency_status = '✅' if variance <= 20 else '⚠️' if variance <= 40 else '❌'
            
            field_consistency[field] = {
                'avg': avg_completeness,
                'min': min_completeness,
                'max': max_completeness,
                'variance': variance,
                'status': consistency_status
            }
    
    print('\n📊 FIELD CONSISTENCY ACROSS PROPERTY CATEGORIES:')
    print('=' * 60)
    
    for field, stats in field_consistency.items():
        print(f'   {stats["status"]} {field}:')
        print(f'      📊 Average: {stats["avg"]:.1f}%')
        print(f'      📈 Range: {stats["min"]:.1f}% - {stats["max"]:.1f}%')
        print(f'      📏 Variance: {stats["variance"]:.1f}%')
    
    print('\n📋 STEP 4: Sample Properties by Category')
    print('-' * 50)
    
    # Show sample properties from each category
    for category, data in category_analysis.items():
        properties = data['properties']
        if len(properties) > 0:
            print(f'\n🏠 SAMPLE {category.upper()} PROPERTIES:')
            
            # Show first 3 properties as samples
            for i, (_, prop) in enumerate(properties.head(3).iterrows()):
                title = prop.get('title', 'NO TITLE')[:60]
                price = prop.get('price', 'NO PRICE')
                area = prop.get('area', 'NO AREA')
                locality = prop.get('locality', 'NO LOCALITY')
                
                print(f'   {i+1}. {title}...')
                print(f'      💰 Price: {price} | 📏 Area: {area} | 📍 Locality: {locality}')
    
    print('\n🎯 OVERALL ASSESSMENT:')
    print('=' * 50)
    
    # Calculate overall metrics
    total_categories = len(category_analysis)
    total_properties = len(df)
    
    # Average field completeness across all categories
    all_completeness = []
    for field in critical_fields:
        if field in field_consistency:
            all_completeness.append(field_consistency[field]['avg'])
    
    overall_avg = sum(all_completeness) / len(all_completeness) if all_completeness else 0
    
    # Find best and worst performing fields
    best_field = max(field_consistency.keys(), key=lambda f: field_consistency[f]['avg']) if field_consistency else 'N/A'
    worst_field = min(field_consistency.keys(), key=lambda f: field_consistency[f]['avg']) if field_consistency else 'N/A'
    
    # Find most and least consistent fields
    most_consistent = min(field_consistency.keys(), key=lambda f: field_consistency[f]['variance']) if field_consistency else 'N/A'
    least_consistent = max(field_consistency.keys(), key=lambda f: field_consistency[f]['variance']) if field_consistency else 'N/A'
    
    print(f'📊 Property Categories Analyzed: {total_categories}')
    print(f'📊 Total Properties: {total_properties}')
    print(f'📊 Overall Average Field Completeness: {overall_avg:.1f}%')
    print(f'📊 Best Performing Field: {best_field} ({field_consistency.get(best_field, {}).get("avg", 0):.1f}%)')
    print(f'📊 Worst Performing Field: {worst_field} ({field_consistency.get(worst_field, {}).get("avg", 0):.1f}%)')
    print(f'📊 Most Consistent Field: {most_consistent} ({field_consistency.get(most_consistent, {}).get("variance", 0):.1f}% variance)')
    print(f'📊 Least Consistent Field: {least_consistent} ({field_consistency.get(least_consistent, {}).get("variance", 0):.1f}% variance)')
    
    # Overall assessment
    if overall_avg >= 85:
        print('\n🎉 EXCELLENT: Field extraction works consistently across all property types!')
        assessment = 'EXCELLENT'
    elif overall_avg >= 75:
        print('\n✅ GOOD: Field extraction works well across most property types')
        assessment = 'GOOD'
    elif overall_avg >= 65:
        print('\n⚠️ MODERATE: Some property types need field extraction improvements')
        assessment = 'MODERATE'
    else:
        print('\n❌ POOR: Significant property type specific issues need addressing')
        assessment = 'POOR'
    
    # Save analysis results
    analysis_results = {
        'total_categories': total_categories,
        'total_properties': total_properties,
        'overall_avg_completeness': overall_avg,
        'best_field': best_field,
        'worst_field': worst_field,
        'most_consistent_field': most_consistent,
        'least_consistent_field': least_consistent,
        'assessment': assessment,
        'field_consistency': field_consistency,
        'category_analysis': {k: {key: val for key, val in v.items() if key != 'properties'} 
                            for k, v in category_analysis.items()}
    }
    
    # Save to JSON for detailed analysis
    import json
    with open('property_type_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f'\n💾 Saved detailed analysis to: property_type_analysis_results.json')
    
    return analysis_results

def categorize_property_types(df):
    """Categorize properties into logical groups"""
    
    categories = {
        'Apartments/Flats': df[df['property_type'].str.contains('BHK', na=False) & 
                              ~df['property_type'].str.contains('House|Villa|Floor', na=False)],
        'Houses': df[df['property_type'].str.contains('House', na=False)],
        'Builder Floors': df[df['property_type'].str.contains('Builder Floor|Floor', na=False)],
        'Villas': df[df['property_type'].str.contains('Villa', na=False)],
        'Plots/Land': df[df['property_type'].str.contains('Plot|Land', na=False)],
        'Commercial': df[df['property_type'].str.contains('Commercial|Office|Shop', na=False)]
    }
    
    # Remove empty categories
    categories = {k: v for k, v in categories.items() if len(v) > 0}
    
    return categories

if __name__ == "__main__":
    analyze_existing_data()
