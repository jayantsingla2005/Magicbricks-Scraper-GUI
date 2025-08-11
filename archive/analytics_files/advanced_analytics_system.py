#!/usr/bin/env python3
"""
Advanced Features & Analytics System
Comprehensive analytics, insights, and business intelligence for MagicBricks data.
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class PropertyAnalytics:
    """
    Advanced property analytics and insights engine
    """
    
    def __init__(self, database_path: str = "magicbricks_enhanced.db"):
        """Initialize analytics system"""
        
        self.database_path = database_path
        self.data_cache = {}
        self.insights_cache = {}
        
        # Create analytics directory
        self.analytics_dir = Path('analytics')
        self.analytics_dir.mkdir(exist_ok=True)
        
        # Create reports directory
        self.reports_dir = Path('reports')
        self.reports_dir.mkdir(exist_ok=True)
        
        print("🔬 Advanced Analytics System Initialized")
    
    def load_property_data(self, refresh_cache: bool = False) -> pd.DataFrame:
        """Load property data from database"""
        
        if 'properties' in self.data_cache and not refresh_cache:
            return self.data_cache['properties']
        
        try:
            conn = sqlite3.connect(self.database_path)
            
            query = """
            SELECT 
                id, property_url, title, property_type, transaction_type,
                city, locality, society, bedrooms, bathrooms, balconies,
                area, super_area, carpet_area, plot_area, area_unit,
                price, price_unit, price_type, price_per_sqft,
                floor, total_floors, age, furnishing, facing, parking,
                status, possession, created_at, scraped_at,
                has_edge_cases, edge_case_severity, data_completeness_score,
                extraction_confidence
            FROM properties
            WHERE price IS NOT NULL AND area IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Data preprocessing
            df = self._preprocess_data(df)
            
            # Cache the data
            self.data_cache['properties'] = df
            
            print(f"📊 Loaded {len(df)} properties for analysis")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return pd.DataFrame()
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for analysis"""
        
        # Convert date columns
        date_columns = ['created_at', 'scraped_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        # Standardize price to lakhs
        df['price_lakhs'] = df.apply(self._standardize_price, axis=1)
        
        # Calculate price per sqft
        df['calculated_price_per_sqft'] = (df['price_lakhs'] * 100000) / df['area']
        
        # Create property size categories
        df['size_category'] = df['area'].apply(self._categorize_size)
        
        # Create price categories
        df['price_category'] = df['price_lakhs'].apply(self._categorize_price)
        
        # Create location tier
        df['location_tier'] = df['city'].apply(self._categorize_location)
        
        return df
    
    def _standardize_price(self, row) -> float:
        """Standardize price to lakhs"""
        
        price = row['price']
        unit = row['price_unit']
        
        if pd.isna(price) or pd.isna(unit):
            return np.nan
        
        if unit.lower() in ['cr', 'crore']:
            return price * 100  # Convert crores to lakhs
        elif unit.lower() in ['lac', 'lakh']:
            return price
        else:
            return price  # Assume lakhs if unclear
    
    def _categorize_size(self, area: float) -> str:
        """Categorize property by size"""
        
        if pd.isna(area):
            return 'Unknown'
        elif area < 600:
            return 'Compact'
        elif area < 1000:
            return 'Medium'
        elif area < 1500:
            return 'Large'
        else:
            return 'Premium'
    
    def _categorize_price(self, price_lakhs: float) -> str:
        """Categorize property by price"""
        
        if pd.isna(price_lakhs):
            return 'Unknown'
        elif price_lakhs < 50:
            return 'Budget'
        elif price_lakhs < 100:
            return 'Mid-Range'
        elif price_lakhs < 200:
            return 'Premium'
        else:
            return 'Luxury'
    
    def _categorize_location(self, city: str) -> str:
        """Categorize location by tier"""
        
        if pd.isna(city):
            return 'Unknown'
        
        tier1_cities = ['mumbai', 'delhi', 'bangalore', 'gurgaon', 'pune']
        tier2_cities = ['hyderabad', 'chennai', 'kolkata', 'ahmedabad']
        
        city_lower = city.lower()
        
        if city_lower in tier1_cities:
            return 'Tier 1'
        elif city_lower in tier2_cities:
            return 'Tier 2'
        else:
            return 'Tier 3'
    
    def generate_market_insights(self) -> Dict[str, Any]:
        """Generate comprehensive market insights"""
        
        print("🔍 Generating market insights...")
        
        df = self.load_property_data()
        
        if df.empty:
            return {}
        
        insights = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': self._get_data_summary(df),
            'price_analysis': self._analyze_prices(df),
            'location_analysis': self._analyze_locations(df),
            'property_type_analysis': self._analyze_property_types(df),
            'size_analysis': self._analyze_sizes(df),
            'market_trends': self._analyze_trends(df),
            'quality_metrics': self._analyze_data_quality(df)
        }
        
        # Cache insights
        self.insights_cache['market_insights'] = insights
        
        return insights
    
    def _get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic data summary"""
        
        return {
            'total_properties': len(df),
            'cities_covered': df['city'].nunique(),
            'property_types': df['property_type'].nunique(),
            'date_range': {
                'earliest': df['scraped_at'].min().isoformat() if not df['scraped_at'].isna().all() else None,
                'latest': df['scraped_at'].max().isoformat() if not df['scraped_at'].isna().all() else None
            },
            'price_range': {
                'min_lakhs': df['price_lakhs'].min(),
                'max_lakhs': df['price_lakhs'].max(),
                'median_lakhs': df['price_lakhs'].median()
            },
            'area_range': {
                'min_sqft': df['area'].min(),
                'max_sqft': df['area'].max(),
                'median_sqft': df['area'].median()
            }
        }
    
    def _analyze_prices(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price patterns"""
        
        price_analysis = {
            'overall_statistics': {
                'mean_price_lakhs': df['price_lakhs'].mean(),
                'median_price_lakhs': df['price_lakhs'].median(),
                'std_price_lakhs': df['price_lakhs'].std(),
                'price_per_sqft_mean': df['calculated_price_per_sqft'].mean(),
                'price_per_sqft_median': df['calculated_price_per_sqft'].median()
            },
            'by_city': df.groupby('city')['price_lakhs'].agg(['mean', 'median', 'count']).to_dict('index'),
            'by_property_type': df.groupby('property_type')['price_lakhs'].agg(['mean', 'median', 'count']).to_dict('index'),
            'by_size_category': df.groupby('size_category')['price_lakhs'].agg(['mean', 'median', 'count']).to_dict('index'),
            'price_distribution': df['price_category'].value_counts().to_dict()
        }
        
        return price_analysis
    
    def _analyze_locations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze location patterns"""
        
        location_analysis = {
            'city_distribution': df['city'].value_counts().to_dict(),
            'tier_distribution': df['location_tier'].value_counts().to_dict(),
            'top_localities': df['locality'].value_counts().head(10).to_dict(),
            'city_price_ranking': df.groupby('city')['price_lakhs'].median().sort_values(ascending=False).to_dict(),
            'city_inventory': df.groupby('city').size().to_dict()
        }
        
        return location_analysis
    
    def _analyze_property_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze property type patterns"""
        
        property_analysis = {
            'type_distribution': df['property_type'].value_counts().to_dict(),
            'type_price_analysis': df.groupby('property_type')['price_lakhs'].agg(['mean', 'median', 'std']).to_dict('index'),
            'type_size_analysis': df.groupby('property_type')['area'].agg(['mean', 'median', 'std']).to_dict('index'),
            'bedroom_distribution': df['bedrooms'].value_counts().to_dict(),
            'furnishing_distribution': df['furnishing'].value_counts().to_dict()
        }
        
        return property_analysis
    
    def _analyze_sizes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze size patterns"""
        
        size_analysis = {
            'size_distribution': df['size_category'].value_counts().to_dict(),
            'area_statistics': {
                'mean_area': df['area'].mean(),
                'median_area': df['area'].median(),
                'std_area': df['area'].std()
            },
            'size_price_correlation': df[['area', 'price_lakhs']].corr().iloc[0, 1],
            'bedroom_area_analysis': df.groupby('bedrooms')['area'].agg(['mean', 'median', 'count']).to_dict('index')
        }
        
        return size_analysis
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trends"""
        
        # Time-based analysis (if sufficient data)
        trends = {
            'data_collection_trend': 'Insufficient historical data for trend analysis',
            'seasonal_patterns': 'Requires longer data collection period',
            'growth_indicators': 'Baseline established for future comparison'
        }
        
        # If we have date data, analyze trends
        if not df['scraped_at'].isna().all():
            df['scrape_date'] = df['scraped_at'].dt.date
            daily_counts = df.groupby('scrape_date').size()
            
            if len(daily_counts) > 1:
                trends['daily_collection_pattern'] = daily_counts.to_dict()
                trends['collection_consistency'] = daily_counts.std() / daily_counts.mean()
        
        return trends
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        
        quality_metrics = {
            'completeness': {
                'overall_completeness': df['data_completeness_score'].mean(),
                'field_completeness': {
                    'price': (df['price'].notna().sum() / len(df)) * 100,
                    'area': (df['area'].notna().sum() / len(df)) * 100,
                    'location': (df['locality'].notna().sum() / len(df)) * 100,
                    'bedrooms': (df['bedrooms'].notna().sum() / len(df)) * 100,
                    'society': (df['society'].notna().sum() / len(df)) * 100
                }
            },
            'extraction_confidence': {
                'mean_confidence': df['extraction_confidence'].mean(),
                'high_confidence_properties': (df['extraction_confidence'] > 90).sum(),
                'low_confidence_properties': (df['extraction_confidence'] < 70).sum()
            },
            'edge_cases': {
                'properties_with_edge_cases': df['has_edge_cases'].sum(),
                'edge_case_severity_distribution': df['edge_case_severity'].value_counts().to_dict()
            }
        }
        
        return quality_metrics
    
    def create_visualizations(self) -> Dict[str, str]:
        """Create comprehensive visualizations"""
        
        print("📊 Creating visualizations...")
        
        df = self.load_property_data()
        
        if df.empty:
            return {}
        
        visualization_files = {}
        
        # 1. Price Distribution
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        df['price_lakhs'].hist(bins=30, alpha=0.7)
        plt.title('Price Distribution (Lakhs)')
        plt.xlabel('Price (Lakhs)')
        plt.ylabel('Frequency')
        
        plt.subplot(2, 2, 2)
        df['price_category'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Price Category Distribution')
        
        plt.subplot(2, 2, 3)
        city_prices = df.groupby('city')['price_lakhs'].median().sort_values(ascending=True)
        city_prices.plot(kind='barh')
        plt.title('Median Price by City')
        plt.xlabel('Price (Lakhs)')
        
        plt.subplot(2, 2, 4)
        df.boxplot(column='price_lakhs', by='property_type', ax=plt.gca())
        plt.title('Price Distribution by Property Type')
        plt.suptitle('')
        
        plt.tight_layout()
        price_viz_file = self.analytics_dir / 'price_analysis.png'
        plt.savefig(price_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        visualization_files['price_analysis'] = str(price_viz_file)
        
        # 2. Location Analysis
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        df['city'].value_counts().head(10).plot(kind='bar')
        plt.title('Top 10 Cities by Property Count')
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 2)
        df['location_tier'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Location Tier Distribution')
        
        plt.subplot(2, 2, 3)
        top_localities = df['locality'].value_counts().head(10)
        top_localities.plot(kind='barh')
        plt.title('Top 10 Localities')
        
        plt.subplot(2, 2, 4)
        tier_prices = df.groupby('location_tier')['price_lakhs'].median()
        tier_prices.plot(kind='bar')
        plt.title('Median Price by Location Tier')
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        location_viz_file = self.analytics_dir / 'location_analysis.png'
        plt.savefig(location_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        visualization_files['location_analysis'] = str(location_viz_file)
        
        # 3. Property Type Analysis
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        df['property_type'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Property Type Distribution')
        
        plt.subplot(2, 2, 2)
        df['bedrooms'].value_counts().sort_index().plot(kind='bar')
        plt.title('Bedroom Distribution')
        plt.xlabel('Number of Bedrooms')
        
        plt.subplot(2, 2, 3)
        df['size_category'].value_counts().plot(kind='bar')
        plt.title('Size Category Distribution')
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 4)
        furnishing_counts = df['furnishing'].value_counts()
        furnishing_counts.plot(kind='bar')
        plt.title('Furnishing Status Distribution')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        property_viz_file = self.analytics_dir / 'property_analysis.png'
        plt.savefig(property_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        visualization_files['property_analysis'] = str(property_viz_file)
        
        # 4. Data Quality Analysis
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        completeness_data = {
            'Price': (df['price'].notna().sum() / len(df)) * 100,
            'Area': (df['area'].notna().sum() / len(df)) * 100,
            'Location': (df['locality'].notna().sum() / len(df)) * 100,
            'Bedrooms': (df['bedrooms'].notna().sum() / len(df)) * 100,
            'Society': (df['society'].notna().sum() / len(df)) * 100
        }
        
        fields = list(completeness_data.keys())
        completeness = list(completeness_data.values())
        
        plt.bar(fields, completeness)
        plt.title('Field Completeness (%)')
        plt.ylabel('Completeness %')
        plt.xticks(rotation=45)
        
        plt.subplot(1, 2, 2)
        df['extraction_confidence'].hist(bins=20, alpha=0.7)
        plt.title('Extraction Confidence Distribution')
        plt.xlabel('Confidence Score')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        quality_viz_file = self.analytics_dir / 'quality_analysis.png'
        plt.savefig(quality_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        visualization_files['quality_analysis'] = str(quality_viz_file)
        
        print(f"📊 Created {len(visualization_files)} visualization files")
        
        return visualization_files
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive analytics report"""
        
        print("📋 Generating comprehensive analytics report...")
        
        # Generate insights
        insights = self.generate_market_insights()
        
        # Create visualizations
        visualizations = self.create_visualizations()
        
        # Generate report
        report = self._create_analytics_report(insights, visualizations)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"analytics_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Analytics report saved: {report_file}")
        
        return str(report_file)
    
    def _create_analytics_report(self, insights: Dict[str, Any], visualizations: Dict[str, str]) -> str:
        """Create formatted analytics report"""
        
        data_summary = insights.get('data_summary', {})
        price_analysis = insights.get('price_analysis', {})
        location_analysis = insights.get('location_analysis', {})
        quality_metrics = insights.get('quality_metrics', {})
        
        report = f"""# MagicBricks Real Estate Analytics Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This comprehensive analytics report provides insights into the MagicBricks real estate data, covering market trends, pricing patterns, location analysis, and data quality metrics.

### Key Highlights

- **Total Properties Analyzed:** {data_summary.get('total_properties', 0):,}
- **Cities Covered:** {data_summary.get('cities_covered', 0)}
- **Property Types:** {data_summary.get('property_types', 0)}
- **Median Price:** ₹{data_summary.get('price_range', {}).get('median_lakhs', 0):.1f} Lakhs
- **Median Area:** {data_summary.get('area_range', {}).get('median_sqft', 0):.0f} sqft

## Market Analysis

### Price Analysis

**Overall Statistics:**
- Mean Price: ₹{price_analysis.get('overall_statistics', {}).get('mean_price_lakhs', 0):.1f} Lakhs
- Median Price: ₹{price_analysis.get('overall_statistics', {}).get('median_price_lakhs', 0):.1f} Lakhs
- Average Price per sqft: ₹{price_analysis.get('overall_statistics', {}).get('price_per_sqft_mean', 0):.0f}

**Price Distribution:**
"""
        
        # Add price distribution
        price_dist = price_analysis.get('price_distribution', {})
        for category, count in price_dist.items():
            percentage = (count / data_summary.get('total_properties', 1)) * 100
            report += f"- {category}: {count:,} properties ({percentage:.1f}%)\n"
        
        report += f"""

### Location Analysis

**Top Cities by Property Count:**
"""
        
        # Add city distribution
        city_dist = location_analysis.get('city_distribution', {})
        for city, count in list(city_dist.items())[:5]:
            report += f"- {city.title()}: {count:,} properties\n"
        
        report += f"""

**Location Tier Distribution:**
"""
        
        # Add tier distribution
        tier_dist = location_analysis.get('tier_distribution', {})
        for tier, count in tier_dist.items():
            percentage = (count / data_summary.get('total_properties', 1)) * 100
            report += f"- {tier}: {count:,} properties ({percentage:.1f}%)\n"
        
        report += f"""

## Data Quality Assessment

### Completeness Metrics

**Overall Data Completeness:** {quality_metrics.get('completeness', {}).get('overall_completeness', 0):.1f}%

**Field-wise Completeness:**
"""
        
        # Add field completeness
        field_completeness = quality_metrics.get('completeness', {}).get('field_completeness', {})
        for field, completeness in field_completeness.items():
            report += f"- {field.title()}: {completeness:.1f}%\n"
        
        report += f"""

### Extraction Quality

**Mean Extraction Confidence:** {quality_metrics.get('extraction_confidence', {}).get('mean_confidence', 0):.1f}%
**High Confidence Properties:** {quality_metrics.get('extraction_confidence', {}).get('high_confidence_properties', 0):,}
**Properties with Edge Cases:** {quality_metrics.get('edge_cases', {}).get('properties_with_edge_cases', 0):,}

## Visualizations

The following visualizations have been generated:
"""
        
        # Add visualization references
        for viz_name, viz_path in visualizations.items():
            report += f"- **{viz_name.replace('_', ' ').title()}:** `{viz_path}`\n"
        
        report += f"""

## Recommendations

### Market Insights
1. **Price Segmentation:** Focus on mid-range properties (₹50-100 Lakhs) which represent the largest market segment
2. **Location Strategy:** Tier 1 cities show highest inventory and pricing potential
3. **Property Types:** Apartments dominate the market, followed by independent houses

### Data Quality Improvements
1. **Field Completeness:** Improve society and locality data extraction
2. **Edge Case Handling:** Address edge cases affecting {quality_metrics.get('edge_cases', {}).get('properties_with_edge_cases', 0)} properties
3. **Confidence Enhancement:** Focus on improving extraction confidence for better data reliability

### Business Intelligence
1. **Market Monitoring:** Establish baseline metrics for trend analysis
2. **Competitive Analysis:** Leverage location and pricing insights for market positioning
3. **Investment Opportunities:** Identify undervalued markets and emerging locations

## Technical Notes

- **Data Source:** MagicBricks Enhanced Database
- **Analysis Period:** {data_summary.get('date_range', {}).get('earliest', 'N/A')} to {data_summary.get('date_range', {}).get('latest', 'N/A')}
- **Methodology:** Statistical analysis with data quality validation
- **Tools:** Python, Pandas, Matplotlib, Seaborn

---

*This report is generated automatically by the MagicBricks Advanced Analytics System.*
"""
        
        return report


def main():
    """Main function for advanced analytics"""
    
    print("🔬 MagicBricks Advanced Features & Analytics System")
    print("="*60)
    
    try:
        # Initialize analytics system
        analytics = PropertyAnalytics()
        
        # Load data
        df = analytics.load_property_data()
        
        if df.empty:
            print("⚠️ No data available for analysis")
            print("💡 Run the scraper first to collect property data")
            return
        
        print(f"✅ Loaded {len(df)} properties for analysis")
        
        # Generate comprehensive report
        report_file = analytics.generate_comprehensive_report()
        
        print(f"\n🎉 ADVANCED ANALYTICS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Properties Analyzed: {len(df):,}")
        print(f"🏙️ Cities Covered: {df['city'].nunique()}")
        print(f"🏠 Property Types: {df['property_type'].nunique()}")
        print(f"📋 Report Generated: {report_file}")
        print(f"📊 Visualizations: analytics/ directory")
        
        # Display key insights
        insights = analytics.insights_cache.get('market_insights', {})
        if insights:
            data_summary = insights.get('data_summary', {})
            print(f"\n💰 Median Price: ₹{data_summary.get('price_range', {}).get('median_lakhs', 0):.1f} Lakhs")
            print(f"📐 Median Area: {data_summary.get('area_range', {}).get('median_sqft', 0):.0f} sqft")
            
            quality_metrics = insights.get('quality_metrics', {})
            completeness = quality_metrics.get('completeness', {}).get('overall_completeness', 0)
            print(f"✅ Data Completeness: {completeness:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced analytics failed: {str(e)}")
        return False


class BusinessIntelligenceDashboard:
    """
    Business Intelligence Dashboard for real estate insights
    """

    def __init__(self, analytics: PropertyAnalytics):
        self.analytics = analytics
        self.dashboard_dir = Path('dashboard')
        self.dashboard_dir.mkdir(exist_ok=True)

    def create_executive_dashboard(self) -> str:
        """Create executive dashboard HTML"""

        print("📊 Creating executive dashboard...")

        # Get insights
        insights = self.analytics.generate_market_insights()

        # Create HTML dashboard
        html_content = self._generate_dashboard_html(insights)

        # Save dashboard
        dashboard_file = self.dashboard_dir / 'executive_dashboard.html'
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📊 Executive dashboard created: {dashboard_file}")
        return str(dashboard_file)

    def _generate_dashboard_html(self, insights: Dict[str, Any]) -> str:
        """Generate HTML dashboard content"""

        data_summary = insights.get('data_summary', {})
        price_analysis = insights.get('price_analysis', {})
        location_analysis = insights.get('location_analysis', {})
        quality_metrics = insights.get('quality_metrics', {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MagicBricks Executive Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .insights-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .insight-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-danger {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 MagicBricks Executive Dashboard</h1>
            <p>Real Estate Market Intelligence & Analytics</p>
            <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{data_summary.get('total_properties', 0):,}</div>
                <div class="metric-label">Total Properties</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data_summary.get('cities_covered', 0)}</div>
                <div class="metric-label">Cities Covered</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">₹{data_summary.get('price_range', {}).get('median_lakhs', 0):.1f}L</div>
                <div class="metric-label">Median Price</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data_summary.get('area_range', {}).get('median_sqft', 0):.0f}</div>
                <div class="metric-label">Median Area (sqft)</div>
            </div>
        </div>

        <div class="insights-grid">
            <div class="insight-card">
                <h3>💰 Price Analysis</h3>
                <p><strong>Average Price:</strong> ₹{price_analysis.get('overall_statistics', {}).get('mean_price_lakhs', 0):.1f} Lakhs</p>
                <p><strong>Price per sqft:</strong> ₹{price_analysis.get('overall_statistics', {}).get('price_per_sqft_mean', 0):.0f}</p>
                <h4>Top Cities by Price:</h4>
                <ul>"""

        # Add top cities by price
        city_prices = price_analysis.get('by_city', {})
        sorted_cities = sorted(city_prices.items(), key=lambda x: x[1].get('median', 0), reverse=True)
        for city, stats in sorted_cities[:5]:
            html += f"<li>{city.title()}: ₹{stats.get('median', 0):.1f}L</li>"

        html += f"""
                </ul>
            </div>

            <div class="insight-card">
                <h3>🏙️ Location Insights</h3>
                <h4>Top Markets:</h4>
                <ul>"""

        # Add top cities by inventory
        city_dist = location_analysis.get('city_distribution', {})
        for city, count in list(city_dist.items())[:5]:
            html += f"<li>{city.title()}: {count:,} properties</li>"

        html += f"""
                </ul>
                <h4>Location Tiers:</h4>
                <ul>"""

        # Add tier distribution
        tier_dist = location_analysis.get('tier_distribution', {})
        for tier, count in tier_dist.items():
            percentage = (count / data_summary.get('total_properties', 1)) * 100
            html += f"<li>{tier}: {count:,} ({percentage:.1f}%)</li>"

        html += f"""
                </ul>
            </div>

            <div class="insight-card">
                <h3>📊 Data Quality</h3>
                <p><strong>Overall Completeness:</strong>
                <span class="{'status-good' if quality_metrics.get('completeness', {}).get('overall_completeness', 0) > 80 else 'status-warning' if quality_metrics.get('completeness', {}).get('overall_completeness', 0) > 60 else 'status-danger'}">
                {quality_metrics.get('completeness', {}).get('overall_completeness', 0):.1f}%
                </span></p>
                <p><strong>Extraction Confidence:</strong>
                <span class="{'status-good' if quality_metrics.get('extraction_confidence', {}).get('mean_confidence', 0) > 85 else 'status-warning' if quality_metrics.get('extraction_confidence', {}).get('mean_confidence', 0) > 70 else 'status-danger'}">
                {quality_metrics.get('extraction_confidence', {}).get('mean_confidence', 0):.1f}%
                </span></p>
                <p><strong>Edge Cases:</strong> {quality_metrics.get('edge_cases', {}).get('properties_with_edge_cases', 0):,} properties</p>
            </div>

            <div class="insight-card">
                <h3>🎯 Key Recommendations</h3>
                <ul>
                    <li><strong>Market Focus:</strong> Tier 1 cities show highest potential</li>
                    <li><strong>Price Segment:</strong> Mid-range properties (₹50-100L) dominate</li>
                    <li><strong>Data Quality:</strong> Improve society/locality extraction</li>
                    <li><strong>Growth Areas:</strong> Monitor emerging Tier 2 markets</li>
                </ul>
            </div>
        </div>

        <div class="chart-container">
            <h3>📈 Market Trends & Insights</h3>
            <p>Comprehensive visualizations available in the analytics directory:</p>
            <ul>
                <li><strong>Price Analysis:</strong> Distribution, city comparison, type analysis</li>
                <li><strong>Location Analysis:</strong> Geographic distribution, tier analysis</li>
                <li><strong>Property Analysis:</strong> Type distribution, size categories</li>
                <li><strong>Quality Analysis:</strong> Completeness metrics, confidence scores</li>
            </ul>
        </div>

        <div class="chart-container">
            <h3>🔮 Future Enhancements</h3>
            <ul>
                <li><strong>Predictive Analytics:</strong> Price trend forecasting</li>
                <li><strong>Market Scoring:</strong> Investment opportunity ranking</li>
                <li><strong>Competitive Analysis:</strong> Cross-platform comparison</li>
                <li><strong>Real-time Alerts:</strong> Market change notifications</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

        return html

    def generate_api_endpoints(self) -> str:
        """Generate API endpoints documentation"""

        api_doc = """# MagicBricks Analytics API Endpoints

## Overview
RESTful API endpoints for accessing real estate analytics and insights.

## Authentication
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

## Endpoints

### Market Analytics
- `GET /api/v1/analytics/market-summary` - Overall market summary
- `GET /api/v1/analytics/price-trends` - Price trend analysis
- `GET /api/v1/analytics/location-insights` - Location-based insights

### Property Data
- `GET /api/v1/properties` - List properties with filters
- `GET /api/v1/properties/{id}` - Get specific property details
- `GET /api/v1/properties/search` - Advanced property search

### Quality Metrics
- `GET /api/v1/quality/completeness` - Data completeness metrics
- `GET /api/v1/quality/confidence` - Extraction confidence scores
- `GET /api/v1/quality/edge-cases` - Edge case analysis

### Business Intelligence
- `GET /api/v1/bi/dashboard-data` - Dashboard data for visualization
- `GET /api/v1/bi/reports` - Available reports list
- `GET /api/v1/bi/export/{format}` - Export data (CSV, JSON, Excel)

## Response Format
```json
{
  "status": "success",
  "data": {...},
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "total_records": 1000,
    "page": 1,
    "per_page": 50
  }
}
```
"""

        api_file = self.dashboard_dir / 'api_documentation.md'
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(api_doc)

        return str(api_file)


if __name__ == "__main__":
    main()
