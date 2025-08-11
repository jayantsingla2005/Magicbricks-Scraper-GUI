# MagicBricks Property Scraper - Developer Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Configuration System](#configuration-system)
6. [Extension Points](#extension-points)
7. [Testing Framework](#testing-framework)
8. [Deployment Guide](#deployment-guide)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### System Architecture
The MagicBricks Property Scraper follows a modular, component-based architecture designed for scalability, maintainability, and extensibility.

```
┌─────────────────────────────────────────────────────────────┐
│                    GUI Layer (Tkinter)                     │
├─────────────────────────────────────────────────────────────┤
│                  Application Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Scraper Manager │  │ Config Manager  │  │ Task Manager│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Incremental     │  │ Multi-City      │  │ Error       │ │
│  │ System          │  │ Processor       │  │ Handler     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ SQLite Database │  │ File Exports    │  │ URL Tracker │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Selenium WebDriver│ │ Network Manager │  │ Logging     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles
1. **Separation of Concerns**: Each component has a single responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Event-Driven Architecture**: Loose coupling through event/callback mechanisms
4. **Configuration-Driven**: Behavior controlled through external configuration
5. **Testability**: All components designed for unit and integration testing

### Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (built-in)
- **Web Automation**: Selenium WebDriver
- **Database**: SQLite3
- **Data Processing**: Pandas, BeautifulSoup4
- **Export Formats**: CSV, Excel (openpyxl), JSON
- **Testing**: unittest, pytest
- **Packaging**: PyInstaller

## Core Components

### 1. Integrated MagicBricks Scraper
**File**: `integrated_magicbricks_scraper.py`
**Purpose**: Main scraping engine with comprehensive data extraction

#### Key Classes
```python
class IntegratedMagicBricksScraper:
    """Main scraper class with integrated functionality"""
    
    def __init__(self, headless=True, incremental_enabled=True):
        """Initialize scraper with configuration"""
        
    def scrape_properties_with_incremental(self, city, mode, max_pages):
        """Primary scraping method with incremental support"""
        
    def extract_property_data(self, property_element):
        """Extract data from individual property card"""
```

#### Configuration Options
```python
SCRAPER_CONFIG = {
    'delays': {
        'page_load': (3, 6),      # Random delay range
        'between_pages': (4, 7),   # Delay between page requests
        'element_wait': 10         # Maximum wait for elements
    },
    'selectors': {
        'property_cards': 'div.mb-srp__card',
        'title': 'h2[data-summary="title"]',
        'price': 'div.mb-srp__card__price--amount',
        # ... additional selectors
    },
    'extraction': {
        'max_retries': 3,
        'timeout_seconds': 30,
        'validate_data': True
    }
}
```

### 2. Incremental Scraping System
**File**: `incremental_scraping_system.py`
**Purpose**: Intelligent incremental updates with 60-75% time savings

#### Core Algorithm
```python
def analyze_page_for_incremental_decision(self, property_texts, session_id, 
                                        page_number, last_scrape_date):
    """
    Analyze page properties to determine if scraping should continue
    
    Returns:
        {
            'should_stop': bool,
            'confidence': float,
            'old_percentage': float,
            'stop_reason': str
        }
    """
```

#### Database Schema
```sql
-- Incremental tracking tables
CREATE TABLE scrape_sessions (
    id INTEGER PRIMARY KEY,
    city TEXT NOT NULL,
    mode TEXT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    pages_scraped INTEGER,
    properties_found INTEGER
);

CREATE TABLE property_urls_seen (
    url TEXT PRIMARY KEY,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    city TEXT,
    session_id INTEGER
);
```

### 3. Multi-City System
**File**: `multi_city_system.py`
**Purpose**: Comprehensive city management and URL generation

#### City Data Structure
```python
@dataclass
class CityInfo:
    code: str           # 3-letter city code (e.g., 'MUM')
    name: str           # Full city name
    state: str          # State name
    region: Region      # Geographic region
    tier: CityTier      # City tier classification
    is_metro: bool      # Metro city status
    population: int     # Population (optional)
    coordinates: tuple  # (latitude, longitude)
```

#### URL Generation
```python
def generate_scraping_urls(self, city_codes: List[str], 
                          property_type: str = 'sale') -> Dict[str, str]:
    """
    Generate scraping URLs for multiple cities
    
    Args:
        city_codes: List of 3-letter city codes
        property_type: 'sale' or 'rent'
        
    Returns:
        Dict mapping city codes to URLs
    """
```

### 4. Error Handling System
**File**: `error_handling_system.py`
**Purpose**: Comprehensive error management and recovery

#### Error Categories
```python
class ErrorCategory(Enum):
    NETWORK = "network"
    PARSING = "parsing"
    DATABASE = "database"
    VALIDATION = "validation"
    SYSTEM = "system"

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

#### Error Handling Flow
```python
def handle_error(self, error: Exception, context: Dict = None, 
                action: str = None) -> ErrorInfo:
    """
    Centralized error handling with categorization and recovery
    
    Returns:
        ErrorInfo object with category, severity, and suggestions
    """
```

### 5. Multi-City Parallel Processor
**File**: `multi_city_parallel_processor.py`
**Purpose**: Concurrent processing of multiple cities

#### Parallel Processing Architecture
```python
class MultiCityParallelProcessor:
    def __init__(self, max_workers=3, progress_callback=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.progress_callback = progress_callback
        
    def start_parallel_processing(self, cities, config):
        """Start parallel processing for multiple cities"""
        futures = {}
        for city in cities:
            future = self.executor.submit(self._process_city, city, config)
            futures[city] = future
        return futures
```

## API Reference

### Core Scraper API

#### IntegratedMagicBricksScraper

##### Constructor
```python
IntegratedMagicBricksScraper(
    headless: bool = True,
    incremental_enabled: bool = True,
    db_path: str = "magicbricks_enhanced.db"
)
```

##### Primary Methods
```python
def scrape_properties_with_incremental(
    self, 
    city: str, 
    mode: ScrapingMode, 
    max_pages: int = 100
) -> Dict[str, Any]:
    """
    Main scraping method with incremental support
    
    Args:
        city: City name or code
        mode: Scraping mode (INCREMENTAL, FULL, CONSERVATIVE, DATE_RANGE)
        max_pages: Maximum pages to scrape
        
    Returns:
        {
            'success': bool,
            'session_id': int,
            'pages_scraped': int,
            'properties_found': int,
            'session_stats': dict,
            'output_file': str,
            'error': str (if failed)
        }
    """

def extract_property_data(self, property_element) -> Dict[str, Any]:
    """
    Extract data from property card element
    
    Returns:
        Dictionary with 22+ property fields
    """

def close(self):
    """Clean up resources and close browser"""
```

### Incremental System API

#### IncrementalScrapingSystem

```python
def setup_system(self) -> bool:
    """Initialize incremental scraping system"""

def start_incremental_scraping(
    self, 
    city: str, 
    mode: ScrapingMode
) -> Dict[str, Any]:
    """Start new incremental scraping session"""

def analyze_page_for_incremental_decision(
    self,
    property_texts: List[str],
    session_id: int,
    page_number: int,
    last_scrape_date: datetime
) -> Dict[str, Any]:
    """Analyze page to determine if scraping should continue"""
```

### Multi-City System API

#### MultiCitySystem

```python
def get_cities_by_region(self, region: Region) -> List[CityInfo]:
    """Get cities filtered by geographic region"""

def get_cities_by_tier(self, tier: CityTier) -> List[CityInfo]:
    """Get cities filtered by tier classification"""

def search_cities(self, query: str) -> List[CityInfo]:
    """Search cities by name or code"""

def validate_city_selection(self, city_codes: List[str]) -> Dict[str, Any]:
    """Validate city selection and return recommendations"""

def generate_scraping_urls(
    self, 
    city_codes: List[str], 
    property_type: str = 'sale'
) -> Dict[str, str]:
    """Generate scraping URLs for selected cities"""
```

## Database Schema

### Core Tables

#### Properties Table
```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    price TEXT,
    price_numeric REAL,
    location TEXT,
    area TEXT,
    area_numeric REAL,
    bedrooms TEXT,
    bathrooms TEXT,
    property_type TEXT,
    furnishing TEXT,
    society TEXT,
    locality TEXT,
    city TEXT,
    state TEXT,
    posted_date TEXT,
    contact_info TEXT,
    amenities TEXT,
    description TEXT,
    images_count INTEGER,
    
    -- Incremental tracking fields
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posting_date_text TEXT,
    parsed_posting_date TIMESTAMP,
    scrape_session_id INTEGER,
    is_incremental_new BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_completeness_score REAL,
    validation_status TEXT DEFAULT 'pending'
);
```

#### Incremental Tracking Tables
```sql
-- Session management
CREATE TABLE scrape_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    mode TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    pages_scraped INTEGER DEFAULT 0,
    properties_found INTEGER DEFAULT 0,
    properties_saved INTEGER DEFAULT 0,
    success_rate REAL,
    error_count INTEGER DEFAULT 0,
    configuration TEXT -- JSON configuration
);

-- URL tracking for deduplication
CREATE TABLE property_urls_seen (
    url TEXT PRIMARY KEY,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city TEXT,
    session_id INTEGER,
    title TEXT,
    FOREIGN KEY (session_id) REFERENCES scrape_sessions(id)
);

-- Date parsing results
CREATE TABLE property_posting_dates (
    url TEXT PRIMARY KEY,
    original_text TEXT,
    parsed_datetime TIMESTAMP,
    confidence_score REAL,
    parsing_method TEXT,
    session_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES scrape_sessions(id)
);

-- System settings
CREATE TABLE incremental_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance statistics
CREATE TABLE scrape_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    page_number INTEGER,
    properties_found INTEGER,
    processing_time_seconds REAL,
    memory_usage_mb REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES scrape_sessions(id)
);
```

### Performance Indexes
```sql
-- Core performance indexes
CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_properties_date ON properties(extraction_timestamp);
CREATE INDEX idx_properties_url ON properties(url);
CREATE INDEX idx_properties_price ON properties(price_numeric);

-- Incremental system indexes
CREATE INDEX idx_property_urls_url ON property_urls_seen(url);
CREATE INDEX idx_property_urls_first_seen ON property_urls_seen(first_seen);
CREATE INDEX idx_property_urls_city ON property_urls_seen(city);
CREATE INDEX idx_posting_dates_parsed ON property_posting_dates(parsed_datetime);
CREATE INDEX idx_sessions_start_time ON scrape_sessions(start_time);
CREATE INDEX idx_sessions_city_mode ON scrape_sessions(city, mode);
```

## Configuration System

### Configuration Files

#### Main Configuration (`config.json`)
```json
{
    "scraping": {
        "default_mode": "incremental",
        "max_pages_default": 100,
        "headless_browser": true,
        "delays": {
            "page_load_min": 3,
            "page_load_max": 6,
            "between_pages_min": 4,
            "between_pages_max": 7
        }
    },
    "incremental": {
        "stop_threshold_percentage": 80,
        "date_buffer_hours": 2,
        "max_pages_incremental": 100,
        "conservative_mode": false
    },
    "parallel_processing": {
        "max_workers": 3,
        "enable_parallel": true,
        "worker_timeout_minutes": 30
    },
    "output": {
        "default_directory": "./output",
        "file_formats": ["csv", "excel", "json"],
        "include_metadata": true
    },
    "error_handling": {
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "email_notifications": false,
        "log_level": "INFO"
    }
}
```

#### City Configuration (`cities.json`)
```json
{
    "cities": [
        {
            "code": "MUM",
            "name": "Mumbai",
            "state": "Maharashtra",
            "region": "WEST",
            "tier": "METRO",
            "is_metro": true,
            "population": 12442373,
            "coordinates": [19.0760, 72.8777]
        }
        // ... additional cities
    ],
    "regions": {
        "NORTH": ["Delhi", "Gurgaon", "Noida", "Faridabad"],
        "SOUTH": ["Bangalore", "Chennai", "Hyderabad", "Kochi"],
        "WEST": ["Mumbai", "Pune", "Ahmedabad", "Surat"],
        "EAST": ["Kolkata", "Bhubaneswar"],
        "CENTRAL": ["Indore", "Bhopal", "Nagpur"]
    }
}
```

### Configuration Management
```python
class ConfigurationManager:
    """Centralized configuration management"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_configuration()
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        
    def save_configuration(self, config: Dict[str, Any]):
        """Save configuration to file"""
        
    def get_setting(self, key_path: str, default=None):
        """Get setting using dot notation (e.g., 'scraping.delays.page_load_min')"""
        
    def update_setting(self, key_path: str, value):
        """Update setting and save to file"""
```

## Extension Points

### Custom Extractors
```python
class CustomExtractor:
    """Base class for custom field extractors"""
    
    def extract(self, element, context: Dict) -> Any:
        """Extract custom field from property element"""
        raise NotImplementedError
        
    def validate(self, value: Any) -> bool:
        """Validate extracted value"""
        return True

# Example custom extractor
class PropertyAgeExtractor(CustomExtractor):
    def extract(self, element, context):
        # Custom logic to extract property age
        pass
```

### Custom Export Formats
```python
class CustomExporter:
    """Base class for custom export formats"""
    
    def export(self, data: List[Dict], filename: str) -> bool:
        """Export data to custom format"""
        raise NotImplementedError

# Example custom exporter
class XMLExporter(CustomExporter):
    def export(self, data, filename):
        # Custom XML export logic
        pass
```

### Plugin System
```python
class PluginManager:
    """Manage custom plugins and extensions"""
    
    def register_extractor(self, name: str, extractor: CustomExtractor):
        """Register custom field extractor"""
        
    def register_exporter(self, format_name: str, exporter: CustomExporter):
        """Register custom export format"""
        
    def load_plugins(self, plugin_directory: str):
        """Load plugins from directory"""
```

## Testing Framework

### Unit Tests
```python
# Example unit test structure
class TestIncrementalSystem(unittest.TestCase):
    def setUp(self):
        self.incremental_system = IncrementalScrapingSystem(":memory:")
        
    def test_date_parsing(self):
        """Test date parsing functionality"""
        
    def test_stopping_logic(self):
        """Test smart stopping logic"""
        
    def test_url_tracking(self):
        """Test URL tracking and deduplication"""
```

### Integration Tests
```python
class TestScrapingIntegration(unittest.TestCase):
    def test_full_scraping_workflow(self):
        """Test complete scraping workflow"""
        
    def test_incremental_workflow(self):
        """Test incremental scraping workflow"""
        
    def test_multi_city_processing(self):
        """Test parallel multi-city processing"""
```

### Performance Tests
```python
class TestPerformance(unittest.TestCase):
    def test_memory_usage(self):
        """Test memory usage under load"""
        
    def test_scraping_speed(self):
        """Test scraping speed benchmarks"""
        
    def test_concurrent_processing(self):
        """Test concurrent processing performance"""
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/performance/

# Run with coverage
python -m pytest --cov=. tests/

# Run specific test file
python -m pytest tests/test_incremental_system.py
```

## Deployment Guide

### Development Environment Setup
```bash
# Clone repository
git clone https://github.com/your-repo/magicbricks-scraper.git
cd magicbricks-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Start development server
python magicbricks_gui.py
```

### Production Deployment
```bash
# Build executable
python package_builder.py

# Create installer (Windows)
makensis installer.nsi

# Deploy to distribution platform
# Upload installer and portable packages
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "magicbricks_gui.py"]
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- Monitor error logs for critical issues
- Check system resource usage
- Verify scheduled scraping runs

#### Weekly
- Review scraping performance metrics
- Update ChromeDriver if needed
- Clean up old log files
- Backup database

#### Monthly
- Full system performance review
- Update dependencies
- Review and optimize database
- User feedback analysis

### Database Maintenance
```sql
-- Clean old sessions (older than 90 days)
DELETE FROM scrape_sessions 
WHERE start_time < datetime('now', '-90 days');

-- Vacuum database to reclaim space
VACUUM;

-- Update statistics
ANALYZE;

-- Check database integrity
PRAGMA integrity_check;
```

### Log Management
```python
# Log rotation configuration
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'magicbricks_scraper.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Performance Monitoring
```python
# Monitor key metrics
def monitor_performance():
    metrics = {
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/').percent,
        'active_sessions': get_active_session_count(),
        'error_rate': calculate_error_rate()
    }
    return metrics
```

## Contributing Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Document all public methods with docstrings
- Maximum line length: 100 characters

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push and create pull request
git push origin feature/new-feature
```

### Commit Message Format
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scope: component being modified
Description: brief description of changes
```

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Create pull request with description
6. Address review feedback
7. Merge after approval

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

---

This developer documentation provides comprehensive technical information for maintaining, extending, and contributing to the MagicBricks Property Scraper. For user-facing documentation, refer to the User Manual and Installation Guide.
