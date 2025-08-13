#!/usr/bin/env python3
"""
Comprehensive Field Analysis for Extended MagicBricks Dataset
Analyzes 2,940 properties for field completeness and missing data
"""

import pandas as pd
import numpy as np

def analyze_field_completeness():
    """Analyze field completeness across the massive dataset"""
    
    # Load the massive dataset
    df = pd.read_csv('magicbricks_full_scrape_20250813_105254.csv')
    
    print('🎯 COMPREHENSIVE FIELD ANALYSIS - 2,940 PROPERTIES')
    print('=' * 60)
    print(f'Total Properties: {len(df)}')
    print(f'Total Fields: {len(df.columns)}')
    print()
    
    # Calculate field completeness
    print('📊 FIELD COMPLETENESS ANALYSIS:')
    print('-' * 40)
    
    field_stats = {}
    for col in df.columns:
        if col in ['scraped_at', 'page_number', 'property_index', 'is_valid']:
            continue  # Skip metadata fields
        
        total = len(df)
        non_empty_str = df[col].astype(str).str.strip().ne('').sum()
        completeness = (non_empty_str / total) * 100
        
        field_stats[col] = {
            'total': total,
            'filled': non_empty_str,
            'completeness': completeness
        }
        
        status = '✅' if completeness >= 80 else '⚠️' if completeness >= 50 else '❌'
        print(f'{status} {col:<25}: {completeness:5.1f}% ({non_empty_str:4d}/{total})')
    
    print()
    print('🎯 FIELD CATEGORIES:')
    print('-' * 40)
    
    excellent = [k for k, v in field_stats.items() if v['completeness'] >= 80]
    good = [k for k, v in field_stats.items() if 50 <= v['completeness'] < 80]
    poor = [k for k, v in field_stats.items() if v['completeness'] < 50]
    
    print(f'✅ EXCELLENT (≥80%): {len(excellent)} fields')
    for field in excellent:
        print(f'   • {field}: {field_stats[field]["completeness"]:.1f}%')
    
    print(f'⚠️ GOOD (50-79%): {len(good)} fields')
    for field in good:
        print(f'   • {field}: {field_stats[field]["completeness"]:.1f}%')
    
    print(f'❌ POOR (<50%): {len(poor)} fields')
    for field in poor:
        print(f'   • {field}: {field_stats[field]["completeness"]:.1f}%')
    
    print()
    print('🔍 MISSING FIELD ANALYSIS:')
    print('-' * 40)
    
    # Check for completely missing fields that should be there
    expected_fields = [
        'photo_count', 'owner_name', 'contact_options', 'description', 
        'amenities', 'nearby_landmarks', 'floor_plan', 'age_of_property',
        'total_floors', 'carpet_area', 'super_area', 'built_up_area'
    ]
    
    missing_fields = [field for field in expected_fields if field not in df.columns]
    print(f'🚨 COMPLETELY MISSING FIELDS: {len(missing_fields)}')
    for field in missing_fields:
        print(f'   • {field}')
    
    print()
    print('📈 OVERALL STATISTICS:')
    print('-' * 40)
    avg_completeness = np.mean([v['completeness'] for v in field_stats.values()])
    print(f'Average Field Completeness: {avg_completeness:.1f}%')
    print(f'Data Quality Score: {df["data_quality_score"].mean():.1f}%')
    print(f'Validation Success Rate: {(df["is_valid"].sum() / len(df)) * 100:.1f}%')
    
    print()
    print('🎯 PROPERTY TYPE DISTRIBUTION:')
    print('-' * 40)
    property_types = df['property_type'].value_counts()
    for prop_type, count in property_types.head(10).items():
        percentage = (count / len(df)) * 100
        print(f'   • {prop_type}: {count} ({percentage:.1f}%)')
    
    print()
    print('💰 PRICE RANGE ANALYSIS:')
    print('-' * 40)
    # Extract numeric prices for analysis
    df['price_numeric'] = df['price'].str.extract(r'([\d.]+)').astype(float)
    df['price_unit'] = df['price'].str.extract(r'(Cr|Lac)')
    
    # Convert to consistent units (Lac)
    df['price_in_lac'] = df.apply(lambda row: 
        row['price_numeric'] * 100 if row['price_unit'] == 'Cr' 
        else row['price_numeric'], axis=1)
    
    price_ranges = [
        ('< ₹50 Lac', df['price_in_lac'] < 50),
        ('₹50-100 Lac', (df['price_in_lac'] >= 50) & (df['price_in_lac'] < 100)),
        ('₹1-2 Cr', (df['price_in_lac'] >= 100) & (df['price_in_lac'] < 200)),
        ('₹2-5 Cr', (df['price_in_lac'] >= 200) & (df['price_in_lac'] < 500)),
        ('₹5+ Cr', df['price_in_lac'] >= 500)
    ]
    
    for range_name, condition in price_ranges:
        count = condition.sum()
        percentage = (count / len(df)) * 100
        print(f'   • {range_name}: {count} ({percentage:.1f}%)')
    
    return field_stats, excellent, good, poor, missing_fields

if __name__ == "__main__":
    analyze_field_completeness()
