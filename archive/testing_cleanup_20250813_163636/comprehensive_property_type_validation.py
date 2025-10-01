#!/usr/bin/env python3
"""
Comprehensive Property Type Validation
Systematically test field extraction across all property types
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd
import time
from collections import defaultdict

def comprehensive_property_type_validation():
    """Test field extraction across all property types"""
    
    print('🏠 COMPREHENSIVE PROPERTY TYPE VALIDATION')
    print('=' * 60)
    print('🎯 Goal: Validate field extraction across all property types')
    print('📊 Testing: Apartments, Houses, Plots, Villas, Builder Floors, Commercial')
    print('=' * 60)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    print('\n📋 STEP 1: Collecting Diverse Property Types')
    print('-' * 50)
    
    # Scrape multiple pages to get diverse property types
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=5,  # More pages for better diversity
        export_formats=['csv']
    )
    
    if not scraper.properties:
        print('❌ No properties scraped')
        scraper.close()
        return
    
    print(f'✅ Scraped {len(scraper.properties)} total properties')
    
    # Analyze property types
    property_type_analysis = analyze_property_types(scraper.properties)
    
    print('\n📊 PROPERTY TYPE DISTRIBUTION:')
    print('-' * 40)
    
    for prop_type, count in property_type_analysis['distribution'].items():
        percentage = (count / len(scraper.properties)) * 100
        print(f'   🏠 {prop_type}: {count} properties ({percentage:.1f}%)')
    
    print('\n📋 STEP 2: Field Extraction Analysis by Property Type')
    print('-' * 50)
    
    # Analyze field extraction by property type
    field_analysis = analyze_fields_by_property_type(scraper.properties)
    
    # Critical fields to analyze
    critical_fields = [
        'title', 'price', 'area', 'property_type', 'locality', 
        'society', 'status', 'description', 'photo_count', 
        'owner_name', 'contact_options'
    ]
    
    print('\n📊 FIELD EXTRACTION SUCCESS RATES BY PROPERTY TYPE:')
    print('=' * 70)
    
    # Create comprehensive report
    report_data = []
    
    for prop_type in property_type_analysis['distribution'].keys():
        print(f'\n🏠 {prop_type.upper()}:')
        print('-' * 40)
        
        type_properties = [p for p in scraper.properties if p.get('property_type', '').lower() == prop_type.lower()]
        type_count = len(type_properties)
        
        print(f'   📊 Sample Size: {type_count} properties')
        
        type_report = {
            'property_type': prop_type,
            'sample_size': type_count
        }
        
        for field in critical_fields:
            filled_count = sum(1 for prop in type_properties 
                             if prop.get(field) and str(prop.get(field)).strip())
            completeness = (filled_count / type_count) * 100 if type_count > 0 else 0
            
            status = '✅' if completeness >= 90 else '⚠️' if completeness >= 70 else '❌'
            print(f'   {status} {field}: {completeness:.1f}% ({filled_count}/{type_count})')
            
            type_report[f'{field}_completeness'] = completeness
            type_report[f'{field}_filled'] = filled_count
        
        report_data.append(type_report)
    
    # Save detailed analysis
    df_report = pd.DataFrame(report_data)
    df_report.to_csv('property_type_validation_report.csv', index=False)
    print(f'\n💾 Saved detailed report to: property_type_validation_report.csv')
    
    print('\n📋 STEP 3: Cross-Type Consistency Analysis')
    print('-' * 50)
    
    # Analyze consistency across property types
    consistency_analysis = analyze_cross_type_consistency(report_data, critical_fields)
    
    print('\n📊 FIELD CONSISTENCY ACROSS PROPERTY TYPES:')
    print('=' * 50)
    
    for field in critical_fields:
        field_key = f'{field}_completeness'
        completeness_values = [r[field_key] for r in report_data if field_key in r]
        
        if completeness_values:
            avg_completeness = sum(completeness_values) / len(completeness_values)
            min_completeness = min(completeness_values)
            max_completeness = max(completeness_values)
            variance = max_completeness - min_completeness
            
            consistency_status = '✅' if variance <= 20 else '⚠️' if variance <= 40 else '❌'
            
            print(f'   {consistency_status} {field}:')
            print(f'      📊 Average: {avg_completeness:.1f}%')
            print(f'      📈 Range: {min_completeness:.1f}% - {max_completeness:.1f}%')
            print(f'      📏 Variance: {variance:.1f}%')
    
    print('\n📋 STEP 4: Property Type Specific Issues')
    print('-' * 50)
    
    # Identify property type specific issues
    issues = identify_property_type_issues(report_data, critical_fields)
    
    if issues:
        print('\n⚠️ IDENTIFIED ISSUES:')
        for issue in issues:
            print(f'   🔧 {issue}')
    else:
        print('\n✅ No significant property type specific issues identified')
    
    print('\n🎯 OVERALL ASSESSMENT:')
    print('=' * 50)
    
    # Overall assessment
    overall_assessment = generate_overall_assessment(report_data, critical_fields)
    
    print(f'📊 Property Types Tested: {len(report_data)}')
    print(f'📊 Total Properties Analyzed: {len(scraper.properties)}')
    print(f'📊 Average Field Completeness: {overall_assessment["avg_completeness"]:.1f}%')
    print(f'📊 Most Consistent Field: {overall_assessment["most_consistent_field"]}')
    print(f'📊 Least Consistent Field: {overall_assessment["least_consistent_field"]}')
    
    if overall_assessment["avg_completeness"] >= 80:
        print('🎉 EXCELLENT: Field extraction works consistently across all property types!')
    elif overall_assessment["avg_completeness"] >= 70:
        print('✅ GOOD: Field extraction works well across most property types')
    elif overall_assessment["avg_completeness"] >= 60:
        print('⚠️ MODERATE: Some property types need field extraction improvements')
    else:
        print('❌ POOR: Significant property type specific issues need addressing')
    
    # Save comprehensive results
    all_properties_df = pd.DataFrame(scraper.properties)
    all_properties_df.to_csv('comprehensive_property_type_analysis.csv', index=False)
    print(f'\n💾 Saved all property data to: comprehensive_property_type_analysis.csv')
    
    scraper.close()
    return overall_assessment

def analyze_property_types(properties):
    """Analyze distribution of property types"""
    
    type_distribution = defaultdict(int)
    
    for prop in properties:
        prop_type = prop.get('property_type', 'Unknown').strip()
        if prop_type:
            # Normalize property type names
            prop_type = prop_type.lower()
            if 'bhk' in prop_type:
                if 'apartment' in prop_type or 'flat' in prop_type:
                    prop_type = 'apartment'
                elif 'house' in prop_type or 'independent' in prop_type:
                    prop_type = 'house'
                elif 'floor' in prop_type or 'builder floor' in prop_type:
                    prop_type = 'builder_floor'
                else:
                    prop_type = 'apartment'  # Default for BHK
            elif 'villa' in prop_type:
                prop_type = 'villa'
            elif 'plot' in prop_type or 'land' in prop_type:
                prop_type = 'plot'
            elif 'commercial' in prop_type or 'office' in prop_type or 'shop' in prop_type:
                prop_type = 'commercial'
            elif 'house' in prop_type:
                prop_type = 'house'
            else:
                prop_type = 'other'
            
            type_distribution[prop_type] += 1
    
    return {
        'distribution': dict(type_distribution),
        'total_types': len(type_distribution)
    }

def analyze_fields_by_property_type(properties):
    """Analyze field completeness by property type"""
    
    # This function would contain detailed analysis logic
    # For now, return basic structure
    return {
        'analysis_complete': True,
        'timestamp': time.time()
    }

def analyze_cross_type_consistency(report_data, fields):
    """Analyze consistency of field extraction across property types"""
    
    consistency_scores = {}
    
    for field in fields:
        field_key = f'{field}_completeness'
        values = [r.get(field_key, 0) for r in report_data]
        
        if values:
            variance = max(values) - min(values)
            consistency_scores[field] = {
                'variance': variance,
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values)
            }
    
    return consistency_scores

def identify_property_type_issues(report_data, fields):
    """Identify property type specific issues"""
    
    issues = []
    
    for field in fields:
        field_key = f'{field}_completeness'
        
        # Find property types with significantly lower completeness
        avg_completeness = sum(r.get(field_key, 0) for r in report_data) / len(report_data)
        
        for report in report_data:
            completeness = report.get(field_key, 0)
            if completeness < avg_completeness - 30:  # 30% below average
                issues.append(f'{field} extraction poor for {report["property_type"]} ({completeness:.1f}% vs {avg_completeness:.1f}% avg)')
    
    return issues

def generate_overall_assessment(report_data, fields):
    """Generate overall assessment of property type validation"""
    
    # Calculate average completeness across all fields and property types
    all_completeness = []
    field_variances = {}
    
    for field in fields:
        field_key = f'{field}_completeness'
        field_values = [r.get(field_key, 0) for r in report_data]
        
        if field_values:
            all_completeness.extend(field_values)
            field_variances[field] = max(field_values) - min(field_values)
    
    avg_completeness = sum(all_completeness) / len(all_completeness) if all_completeness else 0
    
    # Find most and least consistent fields
    most_consistent = min(field_variances.keys(), key=lambda k: field_variances[k]) if field_variances else 'N/A'
    least_consistent = max(field_variances.keys(), key=lambda k: field_variances[k]) if field_variances else 'N/A'
    
    return {
        'avg_completeness': avg_completeness,
        'most_consistent_field': most_consistent,
        'least_consistent_field': least_consistent,
        'total_property_types': len(report_data),
        'field_variances': field_variances
    }

if __name__ == "__main__":
    comprehensive_property_type_validation()
