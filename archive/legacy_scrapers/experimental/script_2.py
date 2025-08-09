# Create a requirements.txt file for the dependencies
requirements = """# MagicBricks Property Scraper Requirements

# Core scraping libraries
selenium==4.15.0
beautifulsoup4==4.12.2
requests==2.31.0

# WebDriver management
webdriver-manager==4.0.1

# Data processing and analysis
pandas==2.1.3
numpy==1.25.2

# Utilities
lxml==4.9.3
urllib3==2.1.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

# Also create a simple installation and usage guide
usage_guide = """# MagicBricks Gurgaon Property Scraper

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

## Customization

### Limit Pages for Testing
```python
# Modify in main() function
for page in range(1, 101):  # Only scrape first 100 pages
```

### Change Location
```python
# Change the base URL to scrape different cities
base_url = "https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs"
scraper.scrape_all_properties(base_url)
```

### Adjust Delays
```python
# Increase delay between requests (in seconds)
time.sleep(random.uniform(5, 10))  # 5-10 second delays
```

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
"""

with open('README.md', 'w') as f:
    f.write(usage_guide)

print("✅ Created requirements.txt")
print("✅ Created README.md with usage instructions")
print("\nFiles created:")
print("1. magicbricks_scraper.py - Full-featured scraper")
print("2. magicbricks_scraper_v2.py - Optimized scraper (recommended)")
print("3. requirements.txt - Dependencies")
print("4. README.md - Usage guide")

print("\n🚀 To get started:")
print("1. pip install -r requirements.txt")
print("2. python magicbricks_scraper_v2.py")
print("\nThe scraper will automatically handle all 30K+ listings and save to CSV!")