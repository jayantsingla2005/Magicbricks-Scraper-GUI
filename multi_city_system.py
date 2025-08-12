#!/usr/bin/env python3
"""
Multi-City Selection System
Comprehensive city selection and management system with geographic coverage for MagicBricks scraping.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class CityTier(Enum):
    """City tier classification"""
    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"


class Region(Enum):
    """Geographic regions of India"""
    NORTH = "North India"
    SOUTH = "South India"
    WEST = "West India"
    EAST = "East India"
    CENTRAL = "Central India"
    NORTHEAST = "Northeast India"


@dataclass
class CityInfo:
    """City information data class"""
    code: str
    name: str
    state: str
    region: Region
    tier: CityTier
    population: int
    is_metro: bool
    magicbricks_url_code: str
    is_active: bool = True
    last_scraped: Optional[datetime] = None
    properties_count: int = 0
    avg_scrape_time_minutes: int = 0


class MultiCitySystem:
    """
    Comprehensive multi-city selection and management system
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize multi-city system"""
        
        self.db_path = db_path
        self.connection = None
        
        # Initialize city database
        self.cities = self._initialize_city_database()
        
        # User preferences
        self.user_preferences = {
            'favorite_cities': [],
            'default_region': None,
            'preferred_tier': None,
            'auto_select_metros': False,
            'max_concurrent_cities': 3
        }
        
        print("[CITY] Multi-City System Initialized")
        print(f"   [STATS] Total cities available: {len(self.cities)}")
        print(f"   [METRO] Metro cities: {len([c for c in self.cities.values() if c.is_metro])}")
        print(f"   [TIER1] Tier 1 cities: {len([c for c in self.cities.values() if c.tier == CityTier.TIER_1])}")
    
    def _initialize_city_database(self) -> Dict[str, CityInfo]:
        """Initialize comprehensive city database"""
        
        cities_data = [
            # Tier 1 Cities (Major metros)
            CityInfo("DEL", "Delhi", "Delhi", Region.NORTH, CityTier.TIER_1, 32900000, True, "delhi", True),
            CityInfo("MUM", "Mumbai", "Maharashtra", Region.WEST, CityTier.TIER_1, 20400000, True, "mumbai", True),
            CityInfo("BLR", "Bangalore", "Karnataka", Region.SOUTH, CityTier.TIER_1, 13200000, True, "bangalore", True),
            CityInfo("HYD", "Hyderabad", "Telangana", Region.SOUTH, CityTier.TIER_1, 10500000, True, "hyderabad", True),
            CityInfo("CHE", "Chennai", "Tamil Nadu", Region.SOUTH, CityTier.TIER_1, 11700000, True, "chennai", True),
            CityInfo("KOL", "Kolkata", "West Bengal", Region.EAST, CityTier.TIER_1, 15700000, True, "kolkata", True),
            CityInfo("PUN", "Pune", "Maharashtra", Region.WEST, CityTier.TIER_1, 7400000, True, "pune", True),
            CityInfo("GUR", "Gurgaon", "Haryana", Region.NORTH, CityTier.TIER_1, 1100000, True, "gurgaon", True),
            
            # Tier 2 Cities (Major urban centers)
            CityInfo("AHM", "Ahmedabad", "Gujarat", Region.WEST, CityTier.TIER_2, 8400000, False, "ahmedabad", True),
            CityInfo("SUR", "Surat", "Gujarat", Region.WEST, CityTier.TIER_2, 6600000, False, "surat", True),
            CityInfo("JAI", "Jaipur", "Rajasthan", Region.NORTH, CityTier.TIER_2, 3900000, False, "jaipur", True),
            CityInfo("LUC", "Lucknow", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 3400000, False, "lucknow", True),
            CityInfo("KAN", "Kanpur", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 3200000, False, "kanpur", True),
            CityInfo("NAG", "Nagpur", "Maharashtra", Region.CENTRAL, CityTier.TIER_2, 2500000, False, "nagpur", True),
            CityInfo("IND", "Indore", "Madhya Pradesh", Region.CENTRAL, CityTier.TIER_2, 2200000, False, "indore", True),
            CityInfo("THN", "Thane", "Maharashtra", Region.WEST, CityTier.TIER_2, 1900000, False, "thane", True),
            CityInfo("BHO", "Bhopal", "Madhya Pradesh", Region.CENTRAL, CityTier.TIER_2, 1900000, False, "bhopal", True),
            CityInfo("VIS", "Visakhapatnam", "Andhra Pradesh", Region.SOUTH, CityTier.TIER_2, 2000000, False, "visakhapatnam", True),
            CityInfo("VAD", "Vadodara", "Gujarat", Region.WEST, CityTier.TIER_2, 2100000, False, "vadodara", True),
            CityInfo("FAR", "Faridabad", "Haryana", Region.NORTH, CityTier.TIER_2, 1400000, False, "faridabad", True),
            CityInfo("GAZ", "Ghaziabad", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 1700000, False, "ghaziabad", True),
            CityInfo("LUD", "Ludhiana", "Punjab", Region.NORTH, CityTier.TIER_2, 1600000, False, "ludhiana", True),
            CityInfo("AGR", "Agra", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 1700000, False, "agra", True),
            CityInfo("NAS", "Nashik", "Maharashtra", Region.WEST, CityTier.TIER_2, 1500000, False, "nashik", True),
            CityInfo("RAJ", "Rajkot", "Gujarat", Region.WEST, CityTier.TIER_2, 1400000, False, "rajkot", True),
            CityInfo("MER", "Meerut", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 1400000, False, "meerut", True),
            CityInfo("KAL", "Kalyan-Dombivli", "Maharashtra", Region.WEST, CityTier.TIER_2, 1200000, False, "kalyan", True),
            CityInfo("VAS", "Vasai-Virar", "Maharashtra", Region.WEST, CityTier.TIER_2, 1200000, False, "vasai", True),
            CityInfo("VAR", "Varanasi", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 1200000, False, "varanasi", True),
            CityInfo("SRI", "Srinagar", "Jammu and Kashmir", Region.NORTH, CityTier.TIER_2, 1200000, False, "srinagar", True),
            CityInfo("AUR", "Aurangabad", "Maharashtra", Region.CENTRAL, CityTier.TIER_2, 1200000, False, "aurangabad", True),
            CityInfo("DHN", "Dhanbad", "Jharkhand", Region.EAST, CityTier.TIER_2, 1200000, False, "dhanbad", True),
            CityInfo("AMR", "Amritsar", "Punjab", Region.NORTH, CityTier.TIER_2, 1100000, False, "amritsar", True),
            CityInfo("ALL", "Allahabad", "Uttar Pradesh", Region.NORTH, CityTier.TIER_2, 1100000, False, "allahabad", True),
            CityInfo("RAN", "Ranchi", "Jharkhand", Region.EAST, CityTier.TIER_2, 1100000, False, "ranchi", True),
            CityInfo("HOW", "Howrah", "West Bengal", Region.EAST, CityTier.TIER_2, 1100000, False, "howrah", True),
            CityInfo("COI", "Coimbatore", "Tamil Nadu", Region.SOUTH, CityTier.TIER_2, 1100000, False, "coimbatore", True),
            CityInfo("JAB", "Jabalpur", "Madhya Pradesh", Region.CENTRAL, CityTier.TIER_2, 1000000, False, "jabalpur", True),
            CityInfo("GWA", "Gwalior", "Madhya Pradesh", Region.CENTRAL, CityTier.TIER_2, 1100000, False, "gwalior", True),
            CityInfo("VIJ", "Vijayawada", "Andhra Pradesh", Region.SOUTH, CityTier.TIER_2, 1000000, False, "vijayawada", True),
            CityInfo("JOD", "Jodhpur", "Rajasthan", Region.NORTH, CityTier.TIER_2, 1000000, False, "jodhpur", True),
            CityInfo("MAD", "Madurai", "Tamil Nadu", Region.SOUTH, CityTier.TIER_2, 1000000, False, "madurai", True),
            CityInfo("RAI", "Raipur", "Chhattisgarh", Region.CENTRAL, CityTier.TIER_2, 1000000, False, "raipur", True),
            CityInfo("KOT", "Kota", "Rajasthan", Region.NORTH, CityTier.TIER_2, 1000000, False, "kota", True),
            
            # Tier 3 Cities (Emerging markets)
            CityInfo("GUW", "Guwahati", "Assam", Region.NORTHEAST, CityTier.TIER_3, 900000, False, "guwahati", True),
            CityInfo("CHA", "Chandigarh", "Chandigarh", Region.NORTH, CityTier.TIER_3, 1100000, False, "chandigarh", True),
            CityInfo("TIR", "Tiruppur", "Tamil Nadu", Region.SOUTH, CityTier.TIER_3, 900000, False, "tiruppur", True),
            CityInfo("MOH", "Moradabad", "Uttar Pradesh", Region.NORTH, CityTier.TIER_3, 900000, False, "moradabad", True),
            CityInfo("MYS", "Mysore", "Karnataka", Region.SOUTH, CityTier.TIER_3, 900000, False, "mysore", True),
            CityInfo("BAR", "Bareilly", "Uttar Pradesh", Region.NORTH, CityTier.TIER_3, 900000, False, "bareilly", True),
            CityInfo("GOR", "Gorakhpur", "Uttar Pradesh", Region.NORTH, CityTier.TIER_3, 700000, False, "gorakhpur", True),
            CityInfo("TIR2", "Tiruchirapalli", "Tamil Nadu", Region.SOUTH, CityTier.TIER_3, 800000, False, "tiruchirapalli", True),
            CityInfo("KOC", "Kochi", "Kerala", Region.SOUTH, CityTier.TIER_3, 2100000, False, "kochi", True),
            CityInfo("TVM", "Thiruvananthapuram", "Kerala", Region.SOUTH, CityTier.TIER_3, 1700000, False, "thiruvananthapuram", True)
        ]
        
        # Convert to dictionary with code as key
        return {city.code: city for city in cities_data}
    
    def get_cities_by_region(self, region: Region) -> List[CityInfo]:
        """Get cities by geographic region"""
        return [city for city in self.cities.values() if city.region == region and city.is_active]
    
    def get_cities_by_tier(self, tier: CityTier) -> List[CityInfo]:
        """Get cities by tier classification"""
        return [city for city in self.cities.values() if city.tier == tier and city.is_active]
    
    def get_metro_cities(self) -> List[CityInfo]:
        """Get all metro cities"""
        return [city for city in self.cities.values() if city.is_metro and city.is_active]
    
    def search_cities(self, query: str) -> List[CityInfo]:
        """Search cities by name or state"""
        query = query.lower()
        results = []
        
        for city in self.cities.values():
            if not city.is_active:
                continue
                
            if (query in city.name.lower() or 
                query in city.state.lower() or 
                query in city.magicbricks_url_code.lower()):
                results.append(city)
        
        return sorted(results, key=lambda x: x.population, reverse=True)
    
    def get_city_recommendations(self, user_preferences: Dict[str, Any] = None) -> List[CityInfo]:
        """Get intelligent city recommendations based on user preferences"""
        
        if user_preferences:
            self.user_preferences.update(user_preferences)
        
        recommendations = []
        
        # Start with favorite cities
        for city_code in self.user_preferences.get('favorite_cities', []):
            if city_code in self.cities and self.cities[city_code].is_active:
                recommendations.append(self.cities[city_code])
        
        # Add metro cities if preferred
        if self.user_preferences.get('auto_select_metros', False):
            metro_cities = self.get_metro_cities()
            for city in metro_cities:
                if city not in recommendations:
                    recommendations.append(city)
        
        # Add cities by preferred region
        preferred_region = self.user_preferences.get('default_region')
        if preferred_region:
            region_cities = self.get_cities_by_region(preferred_region)
            for city in region_cities[:5]:  # Top 5 from region
                if city not in recommendations:
                    recommendations.append(city)
        
        # Add cities by preferred tier
        preferred_tier = self.user_preferences.get('preferred_tier')
        if preferred_tier:
            tier_cities = self.get_cities_by_tier(preferred_tier)
            for city in sorted(tier_cities, key=lambda x: x.population, reverse=True)[:5]:
                if city not in recommendations:
                    recommendations.append(city)
        
        # If still empty, add top tier 1 cities
        if not recommendations:
            tier1_cities = self.get_cities_by_tier(CityTier.TIER_1)
            recommendations.extend(sorted(tier1_cities, key=lambda x: x.population, reverse=True)[:8])
        
        return recommendations[:10]  # Limit to top 10
    
    def validate_city_selection(self, selected_cities: List[str]) -> Dict[str, Any]:
        """Validate city selection and provide recommendations"""
        
        validation_result = {
            'valid_cities': [],
            'invalid_cities': [],
            'warnings': [],
            'recommendations': [],
            'estimated_time': 0,
            'total_properties_estimate': 0
        }
        
        for city_code in selected_cities:
            if city_code in self.cities and self.cities[city_code].is_active:
                city = self.cities[city_code]
                validation_result['valid_cities'].append(city)
                
                # Add to time estimate
                validation_result['estimated_time'] += city.avg_scrape_time_minutes or 60
                validation_result['total_properties_estimate'] += city.properties_count or 1000
            else:
                validation_result['invalid_cities'].append(city_code)
        
        # Generate warnings
        if len(validation_result['valid_cities']) > self.user_preferences.get('max_concurrent_cities', 3):
            validation_result['warnings'].append(
                f"Selected {len(validation_result['valid_cities'])} cities. "
                f"Consider limiting to {self.user_preferences['max_concurrent_cities']} for optimal performance."
            )
        
        # Check for regional diversity
        regions = set(city.region for city in validation_result['valid_cities'])
        if len(regions) > 3:
            validation_result['warnings'].append(
                "Selected cities span multiple regions. Consider grouping by region for better performance."
            )
        
        # Generate recommendations
        if len(validation_result['valid_cities']) < 3:
            remaining_slots = 3 - len(validation_result['valid_cities'])
            recommendations = self.get_city_recommendations()
            
            for city in recommendations:
                if city not in validation_result['valid_cities'] and remaining_slots > 0:
                    validation_result['recommendations'].append(city)
                    remaining_slots -= 1
        
        return validation_result
    
    def generate_scraping_urls(self, selected_cities: List[str], property_type: str = "sale") -> Dict[str, str]:
        """Generate MagicBricks URLs for selected cities"""
        
        urls = {}
        
        for city_code in selected_cities:
            if city_code in self.cities:
                city = self.cities[city_code]
                
                if property_type == "sale":
                    url = f"https://www.magicbricks.com/property-for-sale-in-{city.magicbricks_url_code}-pppfs"
                elif property_type == "rent":
                    url = f"https://www.magicbricks.com/property-for-rent-in-{city.magicbricks_url_code}-pppfr"
                else:
                    url = f"https://www.magicbricks.com/property-for-{property_type}-in-{city.magicbricks_url_code}-pppfs"
                
                urls[city_code] = url
        
        return urls
    
    def update_city_statistics(self, city_code: str, properties_count: int, scrape_time_minutes: int):
        """Update city statistics after scraping"""
        
        if city_code in self.cities:
            city = self.cities[city_code]
            city.last_scraped = datetime.now()
            city.properties_count = properties_count
            city.avg_scrape_time_minutes = scrape_time_minutes
            
            # Save to database if available
            self._save_city_statistics(city)
    
    def _save_city_statistics(self, city: CityInfo):
        """Save city statistics to database"""
        
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS city_statistics (
                    city_code TEXT PRIMARY KEY,
                    city_name TEXT,
                    last_scraped DATETIME,
                    properties_count INTEGER,
                    avg_scrape_time_minutes INTEGER,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert or update statistics
            cursor.execute('''
                INSERT OR REPLACE INTO city_statistics 
                (city_code, city_name, last_scraped, properties_count, avg_scrape_time_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (city.code, city.name, city.last_scraped, city.properties_count, city.avg_scrape_time_minutes))
            
            connection.commit()
            connection.close()
            
        except Exception as e:
            print(f"[WARNING] Error saving city statistics: {str(e)}")
    
    def get_city_statistics_summary(self) -> Dict[str, Any]:
        """Get summary of city statistics"""
        
        active_cities = [city for city in self.cities.values() if city.is_active]
        
        summary = {
            'total_cities': len(active_cities),
            'metro_cities': len([c for c in active_cities if c.is_metro]),
            'tier_1_cities': len([c for c in active_cities if c.tier == CityTier.TIER_1]),
            'tier_2_cities': len([c for c in active_cities if c.tier == CityTier.TIER_2]),
            'tier_3_cities': len([c for c in active_cities if c.tier == CityTier.TIER_3]),
            'regions': {
                'north': len([c for c in active_cities if c.region == Region.NORTH]),
                'south': len([c for c in active_cities if c.region == Region.SOUTH]),
                'west': len([c for c in active_cities if c.region == Region.WEST]),
                'east': len([c for c in active_cities if c.region == Region.EAST]),
                'central': len([c for c in active_cities if c.region == Region.CENTRAL]),
                'northeast': len([c for c in active_cities if c.region == Region.NORTHEAST])
            },
            'recently_scraped': len([c for c in active_cities if c.last_scraped and 
                                   (datetime.now() - c.last_scraped).days <= 7])
        }
        
        return summary
    
    def export_city_data(self, format: str = 'json') -> str:
        """Export city data in specified format"""
        
        city_data = []
        for city in self.cities.values():
            city_dict = {
                'code': city.code,
                'name': city.name,
                'state': city.state,
                'region': city.region.value,
                'tier': city.tier.value,
                'population': city.population,
                'is_metro': city.is_metro,
                'magicbricks_url_code': city.magicbricks_url_code,
                'is_active': city.is_active,
                'last_scraped': city.last_scraped.isoformat() if city.last_scraped else None,
                'properties_count': city.properties_count,
                'avg_scrape_time_minutes': city.avg_scrape_time_minutes
            }
            city_data.append(city_dict)
        
        if format == 'json':
            return json.dumps(city_data, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if city_data:
                writer = csv.DictWriter(output, fieldnames=city_data[0].keys())
                writer.writeheader()
                writer.writerows(city_data)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Test the multi-city system"""
    
    try:
        print("🧪 TESTING MULTI-CITY SYSTEM")
        print("="*50)
        
        # Initialize system
        city_system = MultiCitySystem()
        
        # Test city search
        print("\n🔍 Testing city search...")
        search_results = city_system.search_cities("mumbai")
        print(f"Search 'mumbai': {len(search_results)} results")
        for city in search_results[:3]:
            print(f"   - {city.name}, {city.state} ({city.tier.value})")
        
        # Test recommendations
        print("\n[TARGET] Testing recommendations...")
        recommendations = city_system.get_city_recommendations({
            'auto_select_metros': True,
            'preferred_tier': CityTier.TIER_1
        })
        print(f"Recommendations: {len(recommendations)} cities")
        for city in recommendations[:5]:
            print(f"   - {city.name} ({city.tier.value}, {city.region.value})")
        
        # Test validation
        print("\n[SUCCESS] Testing validation...")
        selected_cities = ['DEL', 'MUM', 'BLR', 'CHE', 'HYD']
        validation = city_system.validate_city_selection(selected_cities)
        print(f"Valid cities: {len(validation['valid_cities'])}")
        print(f"Warnings: {len(validation['warnings'])}")
        print(f"Estimated time: {validation['estimated_time']} minutes")
        
        # Test URL generation
        print("\n🔗 Testing URL generation...")
        urls = city_system.generate_scraping_urls(['DEL', 'MUM', 'BLR'])
        for city_code, url in urls.items():
            print(f"   {city_code}: {url}")
        
        # Test statistics
        print("\n[STATS] Testing statistics...")
        stats = city_system.get_city_statistics_summary()
        print(f"Total cities: {stats['total_cities']}")
        print(f"Metro cities: {stats['metro_cities']}")
        print(f"Tier 1 cities: {stats['tier_1_cities']}")
        
        print("\n[SUCCESS] Multi-city system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Multi-city system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
