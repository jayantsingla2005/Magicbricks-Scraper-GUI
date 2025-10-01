#!/usr/bin/env python3
"""
MagicBricks CLI Scraper
Command line interface for running the scraper with various options
"""

import argparse
import sys
from pathlib import Path
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='MagicBricks Property Scraper CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_scraper.py --city gurgaon --mode full --max-pages 5
  python cli_scraper.py --city mumbai --mode incremental --include-individual-pages
  python cli_scraper.py --city delhi --mode full --max-pages 10 --include-individual-pages
  python cli_scraper.py --city bangalore --mode full --force-full --include-individual-pages
        """
    )
    
    parser.add_argument(
        '--city',
        type=str,
        default='gurgaon',
        help='City to scrape (default: gurgaon)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['incremental', 'full', 'conservative', 'date_range', 'custom'],
        default='incremental',
        help='Scraping mode (default: incremental)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum pages to scrape (default: no limit)'
    )
    
    parser.add_argument(
        '--include-individual-pages',
        action='store_true',
        help='Include individual property page scraping'
    )

    parser.add_argument(
        '--force-rescrape-individual',
        action='store_true',
        help='Force re-scrape individual properties even if already scraped'
    )

    parser.add_argument(
        '--force-full',
        action='store_true',
        help='Force full scraping, bypass incremental stopping logic'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser with visible interface'
    )
    
    parser.add_argument(
        '--export-json',
        action='store_true',
        help='Export results to JSON format'
    )
    
    parser.add_argument(
        '--export-excel',
        action='store_true',
        help='Export results to Excel format'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for results (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.city:
        print("[ERROR] Error: City is required")
        sys.exit(1)
    
    # Convert mode string to ScrapingMode enum
    mode_map = {
        'incremental': ScrapingMode.INCREMENTAL,
        'full': ScrapingMode.FULL,
        'conservative': ScrapingMode.CONSERVATIVE,
        'date_range': ScrapingMode.DATE_RANGE,
        'custom': ScrapingMode.CUSTOM
    }
    
    mode = mode_map[args.mode]
    
    # Determine headless mode
    headless = args.headless and not args.no_headless
    
    # Prepare export formats
    export_formats = ['csv']  # Always include CSV
    if args.export_json:
        export_formats.append('json')
    if args.export_excel:
        export_formats.append('excel')
    
    print(f"[START] Starting MagicBricks CLI Scraper")
    print(f"   [CITY] City: {args.city}")
    print(f"   [MODE] Mode: {args.mode}")
    print(f"   [PAGES] Max pages: {args.max_pages or 'No limit'}")
    print(f"   [INDIVIDUAL] Individual pages: {args.include_individual_pages}")
    print(f"   [FORCE] Force full: {args.force_full}")
    print(f"   [HEADLESS] Headless: {headless}")
    print(f"   [EXPORT] Export formats: {', '.join(export_formats)}")
    print()
    
    try:
        # Create custom config for force full mode
        custom_config = {}
        if args.force_full:
            custom_config['force_full_scrape'] = True
            print("⚡ Force full mode enabled - bypassing incremental stopping logic")
        
        # Initialize scraper
        scraper = IntegratedMagicBricksScraper(
            headless=headless,
            incremental_enabled=not args.force_full,  # Disable incremental if force full
            custom_config=custom_config
        )
        
        # Run scraping
        result = scraper.scrape_properties_with_incremental(
            city=args.city,
            mode=mode,
            max_pages=args.max_pages,
            include_individual_pages=args.include_individual_pages,
            export_formats=export_formats,
            force_rescrape_individual=args.force_rescrape_individual
        )
        
        if result['success']:
            print(f"\n[SUCCESS] Scraping completed successfully!")
            print(f"   [STATS] Properties scraped: {result.get('properties_scraped', 0)}")
            print(f"   [STATS] Pages scraped: {result.get('pages_scraped', 0)}")
            print(f"   [TIME] Duration: {result.get('session_stats', {}).get('duration_formatted', 'N/A')}")
            
            if result.get('output_file'):
                print(f"   [FILE] Output file: {result['output_file']}")
            
            # Print session statistics
            session_stats = result.get('session_stats', {})
            if session_stats:
                print(f"\n[STATS] Session Statistics:")
                print(f"   [ID] Session ID: {session_stats.get('session_id', 'N/A')}")
                print(f"   [QUALITY] Data quality: {session_stats.get('average_data_quality', 'N/A')}%")
                print(f"   [FOUND] Properties found: {session_stats.get('properties_found', 0)}")
                print(f"   [SAVE] Properties saved: {session_stats.get('properties_saved', 0)}")
        else:
            print(f"\n[ERROR] Scraping failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n[WARNING] Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        if 'scraper' in locals():
            scraper.close()


if __name__ == "__main__":
    main()