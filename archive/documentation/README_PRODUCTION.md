# MagicBricks Production Scraper

A modern, production-ready web scraper for MagicBricks property listings with comprehensive logging, error handling, and database-ready data models.

## 🚀 Features

### ✅ Production Ready
- **Modern React Support** - Handles dynamic content loading
- **Advanced Anti-Detection** - Sophisticated stealth techniques
- **Comprehensive Error Handling** - Automatic retry with exponential backoff
- **Circuit Breaker Pattern** - Prevents cascading failures
- **Detailed Logging** - Real-time progress tracking with performance metrics

### 📊 Data Quality
- **22+ Property Fields** - Comprehensive data extraction
- **Data Validation** - Quality scoring and validation
- **Database-Ready Models** - Easy migration from CSV/JSON to database
- **Duplicate Detection** - Intelligent deduplication
- **Field Standardization** - Consistent data formatting

### 🛡️ Reliability
- **Checkpoint System** - Resume from interruptions
- **Session Management** - Smart cookie and session handling
- **Rate Limiting** - Intelligent delay algorithms
- **Performance Monitoring** - Real-time metrics and alerts

## 📋 Requirements

- Python 3.8+
- Chrome browser (latest version)
- 4GB+ RAM recommended
- Stable internet connection

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd magicbricks-scraper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify installation**
```bash
python main_scraper.py --test-mode
```

## 🎯 Quick Start

### Basic Usage
```bash
# Scrape all available pages
python main_scraper.py

# Start from specific page
python main_scraper.py --start-page 5

# Limit number of pages
python main_scraper.py --max-pages 10

# Test mode (2 pages only)
python main_scraper.py --test-mode
```

### Advanced Usage
```bash
# Custom configuration
python main_scraper.py --config custom_config.json

# Force headless mode
python main_scraper.py --headless

# Verbose logging
python main_scraper.py --verbose

# Production run with specific parameters
python main_scraper.py --start-page 1 --max-pages 100 --headless
```

## 📁 Project Structure

```
magicbricks-scraper/
├── config/
│   └── scraper_config.json      # Main configuration file
├── src/
│   ├── core/
│   │   └── modern_scraper.py    # Main scraper implementation
│   ├── models/
│   │   └── property_model.py    # Database-ready data models
│   └── utils/
│       └── logger.py            # Comprehensive logging system
├── output/                      # Generated output files
├── main_scraper.py             # Main entry point
├── requirements.txt            # Dependencies
└── README_PRODUCTION.md        # This file
```

## ⚙️ Configuration

The scraper uses `config/scraper_config.json` for all settings:

### Key Configuration Sections:

**Website Settings**
```json
{
  "website": {
    "base_url": "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs",
    "properties_per_page": 30,
    "max_pages": 1000
  }
}
```

**Browser Settings**
```json
{
  "browser": {
    "headless": true,
    "user_agents": [...],
    "viewport_sizes": [...]
  }
}
```

**Delay Settings**
```json
{
  "delays": {
    "page_load_min": 3,
    "page_load_max": 7,
    "between_requests_min": 2,
    "between_requests_max": 5
  }
}
```

## 📊 Output Formats

### CSV Export
- Comprehensive property data in CSV format
- All 22+ fields included
- Database-ready structure
- UTF-8 encoding

### JSON Export
- Structured JSON with metadata
- Session statistics included
- Easy programmatic access
- Nested data preservation

### Checkpoint Files
- Automatic progress saving
- Resume capability
- Session state preservation
- Error recovery data

## 📈 Logging and Monitoring

### Real-Time Progress Tracking
```
📄 PAGE 15 - PROCESSING STARTED
🔗 URL: https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs?page=15
⏱️  Session Elapsed: 12m 34s
⏳ Estimated Remaining: 45m 12s

✅ PAGE 15 - COMPLETED
⏱️  Page Time: 8.2s
🏠 Properties Found: 30
📊 Properties Extracted: 28 (93.3%)
✔️  Properties Valid: 26 (92.9%)

📈 SESSION TOTALS:
   📄 Pages Processed: 15
   🏠 Total Properties: 420
   ✔️  Valid Properties: 389
   ⚠️  Total Errors: 12
   ⏱️  Avg Page Time: 7.8s
```

### Performance Metrics
- Page processing times
- Extraction success rates
- Data quality scores
- Error rates and types
- Memory usage tracking

## 🛠️ Maintenance

### Weekly/Bi-weekly Runs
The scraper is designed for reliable unattended operation:

1. **Automated Scheduling**
```bash
# Add to crontab for weekly runs
0 2 * * 1 /path/to/python /path/to/main_scraper.py --headless
```

2. **Monitoring Setup**
- Check log files for errors
- Monitor output file sizes
- Verify data quality scores
- Review session statistics

3. **Error Recovery**
- Automatic checkpoint saving
- Resume from last successful page
- Circuit breaker for critical failures
- Detailed error logging

### Configuration Updates
- Selector updates for website changes
- Delay adjustments for rate limiting
- User agent rotation updates
- Anti-detection enhancements

## 🔍 Troubleshooting

### Common Issues

**Browser Not Found**
```bash
# Install ChromeDriver automatically
pip install webdriver-manager
```

**Memory Issues**
```bash
# Reduce batch size in config
"checkpoint_interval": 25  # Save more frequently
```

**Rate Limiting**
```bash
# Increase delays in config
"between_requests_min": 5,
"between_requests_max": 10
```

**Stale Elements**
```bash
# Automatic retry mechanism handles this
# Check logs for retry attempts
```

### Log Analysis
- Check `output/scraper_log_*.log` for detailed information
- Review checkpoint files for session state
- Analyze session statistics for performance insights

## 🚀 Future Enhancements

### Phase II: Detailed Page Scraping
- Individual property page extraction
- Enhanced property details
- Image gallery processing
- Contact information extraction

### Database Integration
- PostgreSQL/MySQL support
- Incremental updates
- Data versioning
- Query optimization

### Advanced Features
- Multi-city support
- Property type filtering
- Price change tracking
- Market analysis tools

## 📞 Support

For issues and questions:
1. Check the log files for detailed error information
2. Review the configuration settings
3. Test with `--test-mode` for debugging
4. Check the troubleshooting section above

## 📄 License

This project is for educational and research purposes only. Please respect MagicBricks' terms of service and robots.txt file.
