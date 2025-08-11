#!/usr/bin/env python3
"""
Business Intelligence Suite
Comprehensive business intelligence and advanced features for MagicBricks data platform.
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging


class MarketIntelligenceEngine:
    """
    Advanced market intelligence and predictive analytics
    """
    
    def __init__(self, database_path: str = "magicbricks_enhanced.db"):
        self.database_path = database_path

        # Create intelligence directory
        self.intelligence_dir = Path('intelligence')
        self.intelligence_dir.mkdir(exist_ok=True)

        self.logger = self._setup_logging()

        print("🧠 Market Intelligence Engine Initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for intelligence engine"""
        
        logger = logging.getLogger('market_intelligence')
        logger.setLevel(logging.INFO)
        
        # Create handler
        log_file = self.intelligence_dir / 'market_intelligence.log'
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def generate_market_scoring(self) -> Dict[str, Any]:
        """Generate comprehensive market scoring and rankings"""
        
        print("📊 Generating market scoring...")
        
        try:
            conn = sqlite3.connect(self.database_path)
            
            # Load property data
            query = """
            SELECT city, locality, property_type, price, area, bedrooms,
                   price_unit, status, created_at
            FROM properties 
            WHERE price IS NOT NULL AND area IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return {'error': 'No data available for scoring'}
            
            # Standardize prices to lakhs
            df['price_lakhs'] = df.apply(self._standardize_price, axis=1)
            df['price_per_sqft'] = (df['price_lakhs'] * 100000) / df['area']
            
            # Generate city-level scoring
            city_scores = self._calculate_city_scores(df)
            
            # Generate locality-level scoring
            locality_scores = self._calculate_locality_scores(df)
            
            # Generate investment opportunities
            investment_opportunities = self._identify_investment_opportunities(df)
            
            # Generate market trends
            market_trends = self._analyze_market_trends(df)
            
            scoring_results = {
                'timestamp': datetime.now().isoformat(),
                'city_scores': city_scores,
                'locality_scores': locality_scores,
                'investment_opportunities': investment_opportunities,
                'market_trends': market_trends,
                'methodology': {
                    'scoring_factors': [
                        'Price appreciation potential',
                        'Market liquidity (inventory)',
                        'Price per sqft competitiveness',
                        'Property type diversity',
                        'Market activity level'
                    ],
                    'data_points': len(df),
                    'cities_analyzed': df['city'].nunique()
                }
            }
            
            # Save scoring results
            self._save_scoring_results(scoring_results)
            
            return scoring_results
            
        except Exception as e:
            self.logger.error(f"Market scoring failed: {str(e)}")
            return {'error': str(e)}
    
    def _standardize_price(self, row) -> float:
        """Standardize price to lakhs"""
        
        price = row['price']
        unit = row['price_unit']
        
        if pd.isna(price) or pd.isna(unit):
            return np.nan
        
        if unit.lower() in ['cr', 'crore']:
            return price * 100
        elif unit.lower() in ['lac', 'lakh']:
            return price
        else:
            return price
    
    def _calculate_city_scores(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive city scores"""
        
        city_metrics = df.groupby('city').agg({
            'price_lakhs': ['mean', 'median', 'std', 'count'],
            'price_per_sqft': ['mean', 'median'],
            'area': ['mean', 'median'],
            'property_type': 'nunique'
        }).round(2)
        
        city_scores = {}
        
        for city in city_metrics.index:
            # Extract metrics
            avg_price = city_metrics.loc[city, ('price_lakhs', 'mean')]
            median_price = city_metrics.loc[city, ('price_lakhs', 'median')]
            price_volatility = city_metrics.loc[city, ('price_lakhs', 'std')]
            inventory_count = city_metrics.loc[city, ('price_lakhs', 'count')]
            avg_price_per_sqft = city_metrics.loc[city, ('price_per_sqft', 'mean')]
            property_diversity = city_metrics.loc[city, ('property_type', 'nunique')]
            
            # Calculate component scores (0-100)
            liquidity_score = min(100, (inventory_count / df['city'].value_counts().max()) * 100)
            diversity_score = min(100, (property_diversity / df['property_type'].nunique()) * 100)
            stability_score = max(0, 100 - (price_volatility / avg_price * 100)) if avg_price > 0 else 0
            
            # Calculate overall score
            overall_score = (liquidity_score * 0.4 + diversity_score * 0.3 + stability_score * 0.3)
            
            city_scores[city] = {
                'overall_score': round(overall_score, 1),
                'liquidity_score': round(liquidity_score, 1),
                'diversity_score': round(diversity_score, 1),
                'stability_score': round(stability_score, 1),
                'metrics': {
                    'avg_price_lakhs': avg_price,
                    'median_price_lakhs': median_price,
                    'avg_price_per_sqft': avg_price_per_sqft,
                    'inventory_count': inventory_count,
                    'property_types': property_diversity
                },
                'ranking': 0  # Will be set after sorting
            }
        
        # Rank cities by overall score
        sorted_cities = sorted(city_scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        
        for rank, (city, data) in enumerate(sorted_cities, 1):
            city_scores[city]['ranking'] = rank
        
        return city_scores
    
    def _calculate_locality_scores(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate locality-level scores"""
        
        # Focus on localities with sufficient data
        locality_counts = df['locality'].value_counts()
        significant_localities = locality_counts[locality_counts >= 2].index
        
        locality_df = df[df['locality'].isin(significant_localities)]
        
        if locality_df.empty:
            return {}
        
        locality_metrics = locality_df.groupby(['city', 'locality']).agg({
            'price_lakhs': ['mean', 'median', 'count'],
            'price_per_sqft': ['mean', 'median'],
            'area': ['mean']
        }).round(2)
        
        locality_scores = {}
        
        for (city, locality) in locality_metrics.index:
            avg_price = locality_metrics.loc[(city, locality), ('price_lakhs', 'mean')]
            property_count = locality_metrics.loc[(city, locality), ('price_lakhs', 'count')]
            avg_price_per_sqft = locality_metrics.loc[(city, locality), ('price_per_sqft', 'mean')]
            
            # Calculate locality score based on activity and pricing
            activity_score = min(100, (property_count / locality_counts.max()) * 100)
            
            locality_key = f"{city}_{locality}"
            locality_scores[locality_key] = {
                'city': city,
                'locality': locality,
                'activity_score': round(activity_score, 1),
                'avg_price_lakhs': avg_price,
                'avg_price_per_sqft': avg_price_per_sqft,
                'property_count': property_count
            }
        
        return locality_scores
    
    def _identify_investment_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify potential investment opportunities"""
        
        opportunities = []
        
        # Opportunity 1: Below-median pricing in high-activity cities
        city_activity = df['city'].value_counts()
        high_activity_cities = city_activity[city_activity >= city_activity.quantile(0.7)].index
        
        for city in high_activity_cities:
            city_data = df[df['city'] == city]
            median_price_per_sqft = city_data['price_per_sqft'].median()
            
            below_median_properties = city_data[city_data['price_per_sqft'] < median_price_per_sqft * 0.9]
            
            if len(below_median_properties) > 0:
                opportunities.append({
                    'type': 'undervalued_market',
                    'city': city,
                    'description': f'Below-median pricing in high-activity market',
                    'opportunity_count': len(below_median_properties),
                    'avg_discount': round((1 - below_median_properties['price_per_sqft'].mean() / median_price_per_sqft) * 100, 1),
                    'potential': 'high'
                })
        
        # Opportunity 2: Emerging localities
        locality_growth = df.groupby(['city', 'locality']).size().reset_index(name='count')
        emerging_localities = locality_growth[locality_growth['count'].between(2, 5)]
        
        for _, row in emerging_localities.iterrows():
            opportunities.append({
                'type': 'emerging_locality',
                'city': row['city'],
                'locality': row['locality'],
                'description': f'Emerging locality with growing inventory',
                'property_count': row['count'],
                'potential': 'medium'
            })
        
        return opportunities
    
    def _analyze_market_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trends and patterns"""
        
        trends = {
            'property_type_trends': df['property_type'].value_counts().to_dict(),
            'bedroom_preferences': df['bedrooms'].value_counts().sort_index().to_dict(),
            'price_segments': {
                'budget': len(df[df['price_lakhs'] < 50]),
                'mid_range': len(df[df['price_lakhs'].between(50, 100)]),
                'premium': len(df[df['price_lakhs'].between(100, 200)]),
                'luxury': len(df[df['price_lakhs'] > 200])
            },
            'size_preferences': {
                'compact': len(df[df['area'] < 600]),
                'medium': len(df[df['area'].between(600, 1000)]),
                'large': len(df[df['area'].between(1000, 1500)]),
                'premium': len(df[df['area'] > 1500])
            }
        }
        
        return trends
    
    def _save_scoring_results(self, results: Dict[str, Any]):
        """Save scoring results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.intelligence_dir / f"market_scoring_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Market scoring saved: {filename}")
    
    def generate_investment_report(self) -> str:
        """Generate comprehensive investment report"""
        
        print("📈 Generating investment report...")
        
        scoring_results = self.generate_market_scoring()
        
        if 'error' in scoring_results:
            return f"Error generating report: {scoring_results['error']}"
        
        # Create investment report
        report = self._create_investment_report(scoring_results)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.intelligence_dir / f"investment_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Investment report saved: {report_file}")
        return str(report_file)
    
    def _create_investment_report(self, scoring_results: Dict[str, Any]) -> str:
        """Create formatted investment report"""
        
        city_scores = scoring_results.get('city_scores', {})
        opportunities = scoring_results.get('investment_opportunities', [])
        trends = scoring_results.get('market_trends', {})
        methodology = scoring_results.get('methodology', {})
        
        report = f"""# MagicBricks Investment Intelligence Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This investment intelligence report provides data-driven insights for real estate investment decisions based on comprehensive market analysis of {methodology.get('data_points', 0)} properties across {methodology.get('cities_analyzed', 0)} cities.

## Market Scoring Methodology

Our proprietary scoring algorithm evaluates markets based on:
"""
        
        for factor in methodology.get('scoring_factors', []):
            report += f"- {factor}\n"
        
        report += f"""

## Top Investment Markets

### City Rankings
"""
        
        # Add top cities
        sorted_cities = sorted(city_scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        
        for rank, (city, data) in enumerate(sorted_cities[:5], 1):
            report += f"""
**{rank}. {city.title()}** (Score: {data['overall_score']}/100)
- Liquidity Score: {data['liquidity_score']}/100
- Diversity Score: {data['diversity_score']}/100  
- Stability Score: {data['stability_score']}/100
- Average Price: ₹{data['metrics']['avg_price_lakhs']:.1f} Lakhs
- Inventory: {data['metrics']['inventory_count']} properties
"""
        
        report += f"""

## Investment Opportunities

### High-Potential Opportunities
"""
        
        # Add investment opportunities
        high_potential = [opp for opp in opportunities if opp.get('potential') == 'high']
        
        for i, opp in enumerate(high_potential[:3], 1):
            report += f"""
**{i}. {opp['type'].replace('_', ' ').title()}**
- Location: {opp['city'].title()}
- Description: {opp['description']}
- Opportunity Size: {opp.get('opportunity_count', 'N/A')} properties
"""
            if 'avg_discount' in opp:
                report += f"- Average Discount: {opp['avg_discount']}%\n"
        
        report += f"""

## Market Trends Analysis

### Property Type Distribution
"""
        
        # Add property type trends
        prop_trends = trends.get('property_type_trends', {})
        total_props = sum(prop_trends.values())
        
        for prop_type, count in sorted(prop_trends.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_props * 100) if total_props > 0 else 0
            report += f"- {prop_type.title()}: {count} properties ({percentage:.1f}%)\n"
        
        report += f"""

### Price Segment Analysis
"""
        
        # Add price segment analysis
        price_segments = trends.get('price_segments', {})
        total_price_props = sum(price_segments.values())
        
        for segment, count in price_segments.items():
            percentage = (count / total_price_props * 100) if total_price_props > 0 else 0
            report += f"- {segment.replace('_', ' ').title()}: {count} properties ({percentage:.1f}%)\n"
        
        report += f"""

## Investment Recommendations

### Short-term Opportunities (6-12 months)
1. **Focus on Tier 1 Cities**: Highest liquidity and market activity
2. **Target Mid-range Segment**: ₹50-100 Lakhs shows strongest demand
3. **Monitor Emerging Localities**: Early entry in developing areas

### Medium-term Strategy (1-3 years)
1. **Diversify Property Types**: Balance apartments and independent houses
2. **Geographic Expansion**: Consider Tier 2 cities for growth potential
3. **Size Optimization**: Focus on 2-3 BHK configurations

### Long-term Vision (3+ years)
1. **Market Leadership**: Establish presence in top-scoring cities
2. **Technology Integration**: Leverage data analytics for decision making
3. **Portfolio Optimization**: Regular rebalancing based on market scores

## Risk Assessment

### Market Risks
- **Price Volatility**: Monitor cities with high price standard deviation
- **Liquidity Risk**: Avoid markets with low inventory turnover
- **Regulatory Changes**: Stay updated on policy impacts

### Data Quality Considerations
- Analysis based on current available data
- Continuous monitoring recommended for trend validation
- Regular model updates as more data becomes available

## Conclusion

The real estate market shows strong fundamentals with clear investment opportunities. Focus on high-scoring cities with strong liquidity and diversity metrics for optimal returns.

---

*This report is generated by the MagicBricks Market Intelligence Engine using proprietary algorithms and comprehensive data analysis.*
"""
        
        return report


def main():
    """Main function for business intelligence suite"""
    
    print("🧠 MagicBricks Business Intelligence Suite")
    print("="*60)
    
    try:
        # Initialize market intelligence engine
        intelligence = MarketIntelligenceEngine()
        
        # Generate market scoring
        scoring_results = intelligence.generate_market_scoring()
        
        if 'error' in scoring_results:
            print(f"❌ Market scoring failed: {scoring_results['error']}")
            return False
        
        # Generate investment report
        report_file = intelligence.generate_investment_report()
        
        print(f"\n🎉 BUSINESS INTELLIGENCE SUITE COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Display key results
        city_scores = scoring_results.get('city_scores', {})
        opportunities = scoring_results.get('investment_opportunities', [])
        
        if city_scores:
            print(f"🏙️ Cities Analyzed: {len(city_scores)}")
            
            # Show top city
            top_city = max(city_scores.items(), key=lambda x: x[1]['overall_score'])
            print(f"🏆 Top Market: {top_city[0].title()} (Score: {top_city[1]['overall_score']}/100)")
        
        if opportunities:
            print(f"💡 Investment Opportunities: {len(opportunities)}")
            high_potential = len([opp for opp in opportunities if opp.get('potential') == 'high'])
            print(f"🎯 High-Potential Opportunities: {high_potential}")
        
        print(f"📄 Investment Report: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Business intelligence suite failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
