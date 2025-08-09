#!/usr/bin/env python3
"""
Automated Research Tool for Comprehensive Property Type Analysis
Tests extraction across all property types and identifies patterns/issues
"""

import json
import pandas as pd
from pathlib import Path
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any
import argparse


class AutomatedResearchTool:
    """Automated tool for comprehensive property type research"""
    
    def __init__(self):
        self.research_plan = self.load_research_plan()
        self.results = []
        self.output_dir = Path('research_output')
        self.output_dir.mkdir(exist_ok=True)
    
    def load_research_plan(self) -> Dict[str, Any]:
        """Load research plan from JSON file"""
        try:
            with open('research_plan.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Research plan not found. Run comprehensive_research_plan.py first.")
            return {"research_targets": []}
    
    def run_targeted_scraping(self, url: str, pages: int = 2) -> Dict[str, Any]:
        """Run scraper on specific URL and return results"""
        print(f"🔍 Testing: {url}")
        print(f"📄 Pages: {pages}")

        # Run scraper with test mode using default config and URL override
        start_time = time.time()
        try:
            # Set environment variable for URL override
            import os
            env = os.environ.copy()
            env['MAGICBRICKS_URL_OVERRIDE'] = url

            result = subprocess.run([
                'python', 'main_scraper.py',
                '--test-mode',
                '--max-pages', str(pages)
            ], capture_output=True, text=True, timeout=300, env=env)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "duration": duration,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": 300,
                "error": "Timeout after 5 minutes"
            }
        
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def analyze_extraction_results(self) -> Dict[str, Any]:
        """Analyze latest extraction results"""
        # Find latest CSV file
        output_files = sorted(Path('output').glob('magicbricks_properties_*.csv'), 
                            key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not output_files:
            return {"error": "No output files found"}
        
        latest_file = output_files[0]
        
        try:
            df = pd.read_csv(latest_file)
            total_properties = len(df)
            
            # Analyze key fields
            analysis = {
                "total_properties": total_properties,
                "file": latest_file.name,
                "field_analysis": {}
            }
            
            # Key fields to analyze
            key_fields = [
                'title', 'price', 'super_area', 'carpet_area', 'society', 
                'status', 'property_type', 'bedrooms', 'locality', 'furnishing'
            ]
            
            for field in key_fields:
                if field in df.columns:
                    non_null_count = df[field].notna().sum()
                    percentage = (non_null_count / total_properties) * 100
                    analysis['field_analysis'][field] = {
                        "count": non_null_count,
                        "percentage": round(percentage, 1),
                        "sample_values": df[field].dropna().head(3).tolist()
                    }
            
            # Special analysis for area fields (combined)
            if 'super_area' in df.columns and 'carpet_area' in df.columns:
                has_any_area = ((df['super_area'].notna()) | (df['carpet_area'].notna())).sum()
                area_percentage = (has_any_area / total_properties) * 100
                analysis['field_analysis']['any_area'] = {
                    "count": has_any_area,
                    "percentage": round(area_percentage, 1),
                    "note": "Combined super_area OR carpet_area"
                }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze results: {str(e)}"}
    
    def run_property_type_research(self, property_type: str = None, max_targets: int = None):
        """Run research on specific property type or all types"""
        print("🔬 STARTING AUTOMATED PROPERTY TYPE RESEARCH")
        print("=" * 80)
        
        targets = self.research_plan.get('research_targets', [])
        
        # Filter by property type if specified
        if property_type:
            targets = [t for t in targets if property_type.lower() in t['property_type'].lower()]
            print(f"🎯 Filtering for property type: {property_type}")
        
        # Limit number of targets if specified
        if max_targets:
            targets = targets[:max_targets]
            print(f"📊 Limited to first {max_targets} targets")
        
        print(f"📋 Total targets to test: {len(targets)}")
        print()
        
        research_results = []
        
        for i, target in enumerate(targets, 1):
            print(f"🔍 TARGET {i}/{len(targets)}: {target['name']}")
            print(f"   Property Type: {target['property_type']}")
            print(f"   Location: {target['location']}")
            print(f"   URL: {target['url']}")
            
            # Run scraping test
            scrape_result = self.run_targeted_scraping(target['url'], pages=2)
            
            if scrape_result['success']:
                print(f"   ✅ Scraping completed in {scrape_result['duration']:.1f}s")
                
                # Analyze results
                analysis = self.analyze_extraction_results()
                
                if 'error' not in analysis:
                    print(f"   📊 Properties extracted: {analysis['total_properties']}")
                    
                    # Key field analysis
                    key_metrics = {}
                    if 'any_area' in analysis['field_analysis']:
                        key_metrics['area'] = analysis['field_analysis']['any_area']['percentage']
                    if 'society' in analysis['field_analysis']:
                        key_metrics['society'] = analysis['field_analysis']['society']['percentage']
                    if 'status' in analysis['field_analysis']:
                        key_metrics['status'] = analysis['field_analysis']['status']['percentage']
                    
                    print(f"   📈 Key metrics: {key_metrics}")
                    
                    # Store results
                    research_results.append({
                        "target": target,
                        "scrape_result": scrape_result,
                        "analysis": analysis,
                        "key_metrics": key_metrics,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                else:
                    print(f"   ⚠️ Analysis failed: {analysis['error']}")
            else:
                print(f"   ❌ Scraping failed: {scrape_result.get('error', 'Unknown error')}")
            
            print()
            
            # Small delay between targets
            time.sleep(2)
        
        # Save comprehensive results
        results_file = self.output_dir / f"research_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(research_results, f, indent=2)
        
        print(f"💾 Research results saved to: {results_file}")
        
        # Generate summary
        self.generate_research_summary(research_results)
        
        return research_results
    
    def generate_research_summary(self, results: List[Dict[str, Any]]):
        """Generate summary of research findings"""
        print("\n📊 RESEARCH SUMMARY")
        print("=" * 50)
        
        if not results:
            print("❌ No results to summarize")
            return
        
        # Overall statistics
        total_targets = len(results)
        successful_targets = sum(1 for r in results if r['scrape_result']['success'])
        total_properties = sum(r['analysis'].get('total_properties', 0) for r in results)
        
        print(f"🎯 Targets Tested: {total_targets}")
        print(f"✅ Successful: {successful_targets} ({successful_targets/total_targets*100:.1f}%)")
        print(f"🏠 Total Properties: {total_properties}")
        
        # Property type breakdown
        property_types = {}
        for result in results:
            prop_type = result['target']['property_type']
            if prop_type not in property_types:
                property_types[prop_type] = []
            property_types[prop_type].append(result)
        
        print(f"\n🏠 PROPERTY TYPE ANALYSIS:")
        print("-" * 40)
        for prop_type, type_results in property_types.items():
            successful = sum(1 for r in type_results if r['scrape_result']['success'])
            avg_area = sum(r['key_metrics'].get('area', 0) for r in type_results) / len(type_results)
            avg_society = sum(r['key_metrics'].get('society', 0) for r in type_results) / len(type_results)
            avg_status = sum(r['key_metrics'].get('status', 0) for r in type_results) / len(type_results)
            
            print(f"{prop_type}:")
            print(f"   Success Rate: {successful}/{len(type_results)} ({successful/len(type_results)*100:.1f}%)")
            print(f"   Avg Area Extraction: {avg_area:.1f}%")
            print(f"   Avg Society Extraction: {avg_society:.1f}%")
            print(f"   Avg Status Extraction: {avg_status:.1f}%")
            print()


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Automated Property Type Research Tool')
    parser.add_argument('--property-type', help='Filter by property type (e.g., "Apartments", "Villas")')
    parser.add_argument('--max-targets', type=int, help='Maximum number of targets to test')
    parser.add_argument('--quick-test', action='store_true', help='Run quick test on first 3 targets')
    
    args = parser.parse_args()
    
    tool = AutomatedResearchTool()
    
    if args.quick_test:
        print("🚀 QUICK TEST MODE - Testing first 3 targets")
        tool.run_property_type_research(max_targets=3)
    else:
        tool.run_property_type_research(
            property_type=args.property_type,
            max_targets=args.max_targets
        )


if __name__ == "__main__":
    main()
