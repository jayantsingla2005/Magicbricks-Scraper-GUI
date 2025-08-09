#!/usr/bin/env python3
"""
MagicBricks Production Scraper - Main Entry Point
Modern, production-ready scraper with comprehensive logging and error handling
"""

import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from src.core.modern_scraper import ModernMagicBricksScraper


def main():
    """Main entry point for the scraper"""
    parser = argparse.ArgumentParser(
        description='MagicBricks Production Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_scraper.py                    # Scrape all pages with default config
  python main_scraper.py --start-page 5    # Start from page 5
  python main_scraper.py --max-pages 10    # Scrape only 10 pages
  python main_scraper.py --config custom_config.json  # Use custom config
  python main_scraper.py --test-mode       # Test mode (only 2 pages)
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/scraper_config.json',
        help='Path to configuration file (default: config/scraper_config.json)'
    )
    
    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='Starting page number (default: 1)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum number of pages to scrape (default: from config)'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Test mode: scrape only 2 pages for testing'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Force headless mode (override config)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate config file
    if not Path(args.config).exists():
        print(f"❌ Configuration file not found: {args.config}")
        print("Please ensure the config file exists or use --config to specify a different path.")
        sys.exit(1)
    
    try:
        # Load and modify config if needed
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Apply command line overrides
        if args.headless:
            config['browser']['headless'] = True
        
        if args.verbose:
            config['logging']['level'] = 'DEBUG'
            config['logging']['detailed_progress'] = True
        
        if args.test_mode:
            args.max_pages = 2
            config['logging']['detailed_progress'] = True
            print("🧪 TEST MODE: Will scrape only 2 pages")
        
        # Save modified config temporarily
        temp_config_path = 'temp_config.json'
        with open(temp_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Print startup information
        print("=" * 80)
        print("🚀 MAGICBRICKS PRODUCTION SCRAPER")
        print("=" * 80)
        print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚙️  Config File: {args.config}")
        print(f"📄 Start Page: {args.start_page}")
        print(f"📊 Max Pages: {args.max_pages or 'All available'}")
        print(f"🖥️  Headless Mode: {config['browser']['headless']}")
        print(f"📝 Log Level: {config['logging']['level']}")
        print(f"💾 Output Directory: {config['output']['export_directory']}")
        print("-" * 80)
        
        # Initialize and run scraper
        scraper = ModernMagicBricksScraper(temp_config_path)
        
        print("🔧 Scraper initialized successfully")
        print("🌐 Starting browser and beginning scraping process...")
        print("-" * 80)
        
        # Run the scraper
        results = scraper.scrape_all_pages(
            start_page=args.start_page,
            max_pages=args.max_pages
        )
        
        # Clean up temp config
        Path(temp_config_path).unlink(missing_ok=True)
        
        # Print results summary
        print("\n" + "=" * 80)
        if results['success']:
            print("✅ SCRAPING COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print(f"📊 Total Properties Scraped: {results['total_properties']}")
            print(f"✔️  Valid Properties: {results['valid_properties']}")
            print(f"📄 Pages Processed: {results['pages_processed']}")
            
            if 'output_files' in results:
                print("\n📁 Output Files:")
                for file_type, file_path in results['output_files'].items():
                    print(f"   {file_type}: {file_path}")
            
            if 'session_stats' in results:
                stats = results['session_stats']
                print(f"\n📈 Session Statistics:")
                print(f"   ⏱️  Average Page Time: {stats.get('average_page_time', 0):.1f}s")
                print(f"   🏠 Avg Properties/Page: {stats.get('average_properties_per_page', 0):.1f}")
                print(f"   ⚠️  Total Errors: {stats.get('total_errors', 0)}")
                print(f"   🔄 Total Retries: {stats.get('total_retries', 0)}")
            
            print("\n🎉 Scraping session completed successfully!")
            
        else:
            print("❌ SCRAPING FAILED")
            print("=" * 80)
            print(f"💥 Error: {results.get('error', 'Unknown error')}")
            print(f"📊 Properties Scraped: {results.get('total_properties', 0)}")
            print(f"📄 Pages Processed: {results.get('pages_processed', 0)}")
            print("\n🔍 Check the log files for detailed error information.")
            sys.exit(1)
        
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Scraping interrupted by user")
        print("💾 Any scraped data should be saved in checkpoint files")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        print("🔍 Check the configuration file and ensure all dependencies are installed")
        sys.exit(1)


if __name__ == "__main__":
    main()
