# MagicBricks Gurgaon Property Scraper

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Chrome browser (required for Selenium)

## Usage

### Quick Start
```python
python magicbricks_scraper_v2.py
```

### Custom Usage
```python
from magicbricks_scraper_v2 import MagicBricksScraperV2

# Initialize scraper
scraper = MagicBricksScraperV2()

# Scrape all properties (30K+)
scraper.scrape_all_properties()

# Save to CSV
df = scraper.save_to_csv("my_properties.csv")

# Close driver
scraper.close()
```

## Features

✅ **Comprehensive Data Extraction**:
- Property title, price, area, bedrooms, bathrooms
- Floor details, age, furnishing, parking
- Location (locality, society, builder)
- Agent contact information
- Property URLs and image URLs
- GPS coordinates (when available)

✅ **Robust Scraping**:
- Handles pagination automatically
- Random delays to avoid blocking
- Error handling and retries
- Progress checkpoints every 50 pages
- Detailed logging

✅ **Data Export**:
- CSV format with all fields
- Duplicate removal
- Data cleaning and validation
- Summary statistics

## Output

The scraper will create:
- `magicbricks_gurgaon_properties_complete.csv` - Main output file
- `checkpoint_page_X.csv` - Checkpoint files every 50 pages
- `scraper.log` - Detailed execution log

## Expected Runtime

- **Full scrape (30K+ properties)**: 8-12 hours
- **Test run (first 100 pages)**: 30-45 minutes
- **Single page**: 5-10 seconds

## CLI Options

The hardened v2 scraper supports runtime flags so you don't need to modify the code.

Common runs:
- Smoke test (1 page, visible browser):
  python magicbricks_scraper_v2.py --max-pages 1 --no-headless
- Change city (example: Mumbai), scrape first 5 pages:
  python magicbricks_scraper_v2.py --base-url https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs --max-pages 5
- Add proxy and tune delays/retries:
  python magicbricks_scraper_v2.py --proxy http://127.0.0.1:8888 --delay-min 3 --delay-max 7 --retries 3

All flags:
- --base-url STRING (default: Gurgaon for-sale)
- --max-pages INT (default: None = all estimated pages)
- --headless / --no-headless (default: --headless)
- --delay-min FLOAT (default: 2.0)
- --delay-max FLOAT (default: 5.0)
- --retries INT (per-page retries, default: 2)
- --backoff-base FLOAT (default: 2.0)
- --backoff-cap FLOAT seconds (default: 20.0)
- --proxy STRING (e.g., http://host:port or socks5://host:port)
- --driver-path STRING (local ChromeDriver path; overrides webdriver-manager)
- --checkpoint-interval INT (default: 50 pages)

## Customization

You can achieve most customization via CLI flags instead of editing code:

- Limit pages for testing:
  python magicbricks_scraper_v2.py --max-pages 100
- Change location/city:
  python magicbricks_scraper_v2.py --base-url https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs
- Adjust delays between page fetches:
  python magicbricks_scraper_v2.py --delay-min 5 --delay-max 10

## Troubleshooting

**Chrome Driver Issues**:
- The script automatically downloads compatible ChromeDriver
- Ensure Chrome browser is installed and updated

**Memory Issues**:
- The scraper saves checkpoints every 50 pages
- You can restart from a checkpoint if needed

**Rate Limiting**:
- Increase delays if you get blocked
- Use headless=False to see browser activity

**No Data Found**:
- Check if website structure changed
- Review logs for specific errors
- Try different CSS selectors

## Legal Notes

- Respect robots.txt and terms of service
- Don't overload the server with requests
- Use scraped data responsibly
- Consider contacting the website for API access

## Support

Check the log files for detailed error information:
- `scraper.log` - Main execution log
- Console output for real-time progress
