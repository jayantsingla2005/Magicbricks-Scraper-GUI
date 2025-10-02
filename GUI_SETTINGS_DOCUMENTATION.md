# MagicBricks Scraper - Complete GUI Settings Documentation
## Comprehensive Guide to All Configurable Settings

**Document Date**: 2025-10-02  
**GUI Version**: v2.0 Professional Edition  
**Purpose**: Complete reference for all GUI settings and testing strategies

---

## PART A: COMPLETE LIST OF GUI SETTINGS

### 1. CITY SELECTION SETTINGS

| Setting | Type | Default | Options | Description |
|---------|------|---------|---------|-------------|
| **Selected Cities** | Multi-select | Gurgaon | 100+ cities | Cities to scrape (single or multiple) |
| **City Selector** | Dialog | - | Tier 1/2/3, Regions | Advanced city selection with filtering |

**Location**: Top of configuration panel  
**Access**: "🌍 Select Cities" button  
**Features**:
- Multi-city selection with checkboxes
- Filter by tier (Metro/Tier 1/Tier 2/Tier 3)
- Filter by region (North/South/East/West/Central)
- Select all / Deselect all options

---

### 2. SCRAPING MODE SETTINGS

| Setting | Type | Default | Options | Description |
|---------|------|---------|---------|-------------|
| **Mode** | Dropdown | Incremental | incremental, full, conservative, date_range, custom | Scraping strategy |

**Mode Descriptions**:
- **Incremental**: Skip already scraped properties (60-75% faster)
- **Full**: Scrape all properties regardless of history
- **Conservative**: Extra delays, safer for large scrapes
- **Date Range**: Scrape properties within specific date range
- **Custom**: User-defined custom scraping logic

---

### 3. BASIC SETTINGS

| Setting | Type | Default | Range/Options | Description |
|---------|------|---------|---------------|-------------|
| **Max Pages** | Number | 100 | 1-10000 | Maximum pages to scrape per city |
| **Output Directory** | Path | Current dir | Any valid path | Where to save scraped data |

**Validation**:
- Max Pages: Must be positive integer
- Output Directory: Must be writable directory

---

### 4. ADVANCED OPTIONS (Checkboxes)

| Setting | Type | Default | Description | Impact |
|---------|------|---------|-------------|--------|
| **Headless Mode** | Boolean | True | Run browser in background | ~10-15% faster |
| **Incremental Scraping** | Boolean | True | Skip already scraped properties | 60-75% faster |
| **Individual Property Details** | Boolean | False | Scrape individual property pages | 10x slower |

**Warnings**:
- Individual Property Details: Shows warning about 10x slower speed
- Displays estimated time impact

---

### 5. INDIVIDUAL PROPERTY MANAGEMENT

| Setting | Type | Default | Options | Description |
|---------|------|---------|---------|-------------|
| **Individual Scraping Mode** | Dropdown | with_listing | with_listing, individual_only, skip_individual | How to handle individual pages |
| **Max Individual Properties** | Number | 100 | 0-unlimited | Limit individual page scraping (0=all) |
| **Force Re-scrape** | Boolean | False | - | Re-scrape already scraped properties |
| **Already Scraped Count** | Display | - | - | Shows count of previously scraped properties |

**Mode Descriptions**:
- **with_listing**: Scrape listing pages first, then individual pages
- **individual_only**: Skip listing pages, only scrape individual property pages
- **skip_individual**: Only scrape listing pages, skip individual pages

---

### 6. EXPORT OPTIONS

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| **CSV Export** | Mandatory | Always | CSV file export (always enabled) |
| **Database Export** | Mandatory | Always | SQLite database (always enabled) |
| **JSON Export** | Boolean | False | Optional JSON structured data export |
| **Excel Export** | Boolean | False | Optional Excel multi-sheet export with summary |

**Export Formats**:
- CSV: Flat file, easy to import
- Database: SQLite for incremental tracking
- JSON: Structured data for APIs
- Excel: Multi-sheet with summary statistics

---

### 7. TIMING & PERFORMANCE SETTINGS

#### 7.1 Page Scraping Timing

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| **Page Delay Min** | Number | 2 | 1-30 sec | Minimum delay between listing pages |
| **Page Delay Max** | Number | 5 | 1-30 sec | Maximum delay between listing pages |
| **Max Retries** | Number | 2 | 1-10 | Retry attempts for failed pages |

**Behavior**: Random delay between min-max for each page to avoid bot detection

#### 7.2 Individual Property Timing

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| **Individual Delay Min** | Number | 1 | 1-30 sec | Minimum delay between individual properties |
| **Individual Delay Max** | Number | 5 | 1-30 sec | Maximum delay between individual properties |
| **Batch Break Delay** | Number | 15 | 5-60 sec | Delay between batches of properties |
| **Bot Detection Delay** | Number | 30 | 10-120 sec | Delay after bot detection recovery |

#### 7.3 Performance Controls

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| **Individual Property Batch Size** | Number | 10 | 1-50 | Properties per batch |
| **Individual Property Workers** | Number | 3 | 1-8 | Parallel browser windows for individual scraping |
| **Page Scraping Mode** | Boolean | False | - | Enable concurrent page scraping (experimental) |
| **Memory Optimization** | Boolean | True | - | Reduce memory usage during scraping |

---

### 8. BROWSER SPEED SETTINGS

| Setting | Type | Default | Options | Description |
|---------|------|---------|---------|-------------|
| **Page Loading Speed** | Dropdown | normal | normal, eager, none | Page load wait strategy |
| **Skip Images** | Boolean | True | - | Don't load property images (faster) |
| **Skip Styling (CSS)** | Boolean | False | - | Don't load CSS (faster but may affect extraction) |
| **Skip JavaScript** | Boolean | False | - | Don't run JS (fastest but may miss data) |

**Page Load Strategies**:
- **normal**: Wait for everything (slower but safer)
- **eager**: Faster loading, may miss some content
- **none**: Fastest but may miss dynamic content

**Speed Impact**:
- Skip Images: ~30-40% faster
- Skip CSS: ~10-15% faster
- Skip JavaScript: ~20-30% faster (may break extraction)

---

### 9. PROPERTY FILTERING

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| **Enable Filtering** | Boolean | False | - | Enable property filtering |
| **Min Price** | Number | - | Any | Minimum property price (in Lakhs/Crores) |
| **Max Price** | Number | - | Any | Maximum property price |
| **Min Area** | Number | - | Any | Minimum property area (sqft) |
| **Max Area** | Number | - | Any | Maximum property area |
| **Property Types** | Multi-select | All | Apartment, House, Plot, etc. | Filter by property type |
| **Furnishing** | Multi-select | All | Furnished, Semi-furnished, Unfurnished | Filter by furnishing |

**Behavior**: Filters are applied during scraping, only matching properties are saved

---

### 10. MONITORING & DISPLAY SETTINGS

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| **Real-time Progress** | Display | - | Shows current page, properties scraped, time elapsed |
| **Statistics Panel** | Display | - | Total properties, success rate, errors, performance |
| **Activity Log** | Display | - | Scrollable log of scraping activities |
| **Auto-scroll Log** | Boolean | True | Automatically scroll to latest log entry |

---

## SUMMARY TABLE: ALL SETTINGS

| Category | Settings Count | Configurable | Display Only |
|----------|----------------|--------------|--------------|
| City Selection | 2 | 2 | 0 |
| Scraping Mode | 1 | 1 | 0 |
| Basic Settings | 2 | 2 | 0 |
| Advanced Options | 3 | 3 | 0 |
| Individual Property | 4 | 3 | 1 |
| Export Options | 4 | 2 | 2 |
| Timing Settings | 8 | 8 | 0 |
| Performance | 4 | 4 | 0 |
| Browser Speed | 4 | 4 | 0 |
| Property Filtering | 7 | 7 | 0 |
| Monitoring | 4 | 1 | 3 |
| **TOTAL** | **43** | **37** | **6** |

---

## CONFIGURATION FILE

All settings are saved to `scraper_config.json`:

```json
{
  "city": "gurgaon",
  "mode": "incremental",
  "max_pages": 100,
  "headless": true,
  "output_directory": ".",
  "incremental_enabled": true,
  "individual_pages": false,
  "export_json": false,
  "export_excel": false,
  "page_delay_min": 2,
  "page_delay_max": 5,
  "individual_delay_min": 1,
  "individual_delay_max": 5,
  "batch_size": 10,
  "max_workers": 3,
  "max_retries": 2
}
```

---

---

## PART B: COMPREHENSIVE GUI TESTING STRATEGY

### TESTING APPROACH OVERVIEW

**Three-Tier Testing Strategy**:
1. **Manual Testing**: Human interaction with GUI
2. **Automated Testing**: Programmatic GUI testing (Playwright/Selenium)
3. **Integration Testing**: End-to-end scraping validation

---

### 1. MANUAL TESTING APPROACH

#### 1.1 Basic Settings Testing

**Test Case 1.1.1: City Selection**
- **Steps**:
  1. Launch GUI: `python magicbricks_gui.py`
  2. Click "🌍 Select Cities" button
  3. Select multiple cities (e.g., Gurgaon, Mumbai, Bangalore)
  4. Click "Apply Selection"
  5. Verify selected cities display updates
- **Expected**: Selected cities shown in label
- **Validation**: Check config file contains selected cities

**Test Case 1.1.2: Scraping Mode**
- **Steps**:
  1. Change mode dropdown to each option
  2. Verify mode description updates
  3. Start scraping with each mode
- **Expected**: Different behavior per mode
- **Validation**: Check log output for mode-specific messages

**Test Case 1.1.3: Max Pages**
- **Steps**:
  1. Enter various values (1, 10, 100, 1000)
  2. Enter invalid values (0, -1, "abc")
  3. Start scraping
- **Expected**: Valid values accepted, invalid rejected
- **Validation**: Scraper stops at specified page count

#### 1.2 Timing Controls Testing

**Test Case 1.2.1: Page Delay Range**
- **Steps**:
  1. Set Page Delay Min = 2, Max = 5
  2. Start scraping
  3. Monitor log output for delay messages
  4. Record actual delays for 10 pages
- **Expected**: All delays between 2-5 seconds
- **Validation**: Calculate average, min, max from logs
- **Pass Criteria**: All delays within range ±0.5 sec

**Test Case 1.2.2: Individual Property Delay**
- **Steps**:
  1. Enable individual pages
  2. Set Individual Delay Min = 1, Max = 3
  3. Start scraping
  4. Monitor individual property delays
- **Expected**: Delays between 1-3 seconds
- **Validation**: Check log timestamps

**Test Case 1.2.3: Bot Detection Delay**
- **Steps**:
  1. Set Bot Detection Delay = 30 seconds
  2. Trigger bot detection (rapid requests)
  3. Observe recovery delay
- **Expected**: 30-second pause after detection
- **Validation**: Check log timestamps

#### 1.3 Performance Settings Testing

**Test Case 1.3.1: Batch Size**
- **Steps**:
  1. Set batch size to 5, 10, 20
  2. Enable individual pages
  3. Monitor batch processing
- **Expected**: Properties processed in specified batch sizes
- **Validation**: Count properties per batch in logs

**Test Case 1.3.2: Parallel Workers**
- **Steps**:
  1. Set workers to 1, 3, 5
  2. Enable individual pages
  3. Monitor concurrent browser windows
- **Expected**: Specified number of parallel processes
- **Validation**: Check system processes, performance metrics

#### 1.4 Export Options Testing

**Test Case 1.4.1: CSV Export (Mandatory)**
- **Steps**:
  1. Run scraping
  2. Check output directory
- **Expected**: CSV file created
- **Validation**: File exists, contains data, proper format

**Test Case 1.4.2: JSON Export (Optional)**
- **Steps**:
  1. Enable JSON export
  2. Run scraping
  3. Check output directory
- **Expected**: JSON file created
- **Validation**: Valid JSON format, matches CSV data

**Test Case 1.4.3: Excel Export (Optional)**
- **Steps**:
  1. Enable Excel export
  2. Run scraping
  3. Open Excel file
- **Expected**: Multi-sheet Excel with summary
- **Validation**: Sheets present, data accurate, summary correct

#### 1.5 Browser Speed Settings Testing

**Test Case 1.5.1: Page Load Strategy**
- **Steps**:
  1. Test each strategy (normal, eager, none)
  2. Measure page load times
  3. Compare data completeness
- **Expected**: Faster with eager/none, may miss data
- **Validation**: Time measurements, field completeness %

**Test Case 1.5.2: Skip Images**
- **Steps**:
  1. Run with images enabled
  2. Run with images disabled
  3. Compare speed and data
- **Expected**: 30-40% faster with images disabled
- **Validation**: Time comparison, image URLs still captured

---

### 2. AUTOMATED TESTING APPROACH

#### 2.1 Using Playwright for GUI Testing

**Setup**:
```python
from playwright.sync_api import sync_playwright
import time

def test_gui_settings():
    with sync_playwright() as p:
        # Launch GUI application
        # Note: Tkinter apps can't be directly controlled by Playwright
        # Alternative: Use pyautogui or similar for desktop automation
        pass
```

**Note**: Playwright is designed for web applications. For Tkinter desktop apps, use:
- **pyautogui**: Mouse/keyboard automation
- **pywinauto**: Windows GUI automation
- **sikuli**: Image-based automation

#### 2.2 Using pyautogui for Desktop GUI Testing

**Installation**:
```bash
pip install pyautogui pillow
```

**Test Script Example**:
```python
import pyautogui
import time
import subprocess

def test_gui_automated():
    # Launch GUI
    process = subprocess.Popen(['python', 'magicbricks_gui.py'])
    time.sleep(5)  # Wait for GUI to load

    # Test Case: Change Max Pages
    # 1. Click on Max Pages field (coordinates need to be determined)
    pyautogui.click(x=500, y=300)

    # 2. Clear field
    pyautogui.hotkey('ctrl', 'a')

    # 3. Type new value
    pyautogui.write('50')

    # 4. Verify value (screenshot comparison)
    screenshot = pyautogui.screenshot()
    screenshot.save('test_max_pages.png')

    # Cleanup
    process.terminate()
```

#### 2.3 Automated Test Cases

**Test Suite Structure**:
```python
class GUIAutomatedTests:
    def test_city_selection(self):
        """Test multi-city selection"""
        # Click Select Cities button
        # Select multiple cities
        # Verify selection
        pass

    def test_timing_controls(self):
        """Test all timing spinboxes"""
        # Set each timing control
        # Verify values saved
        pass

    def test_export_options(self):
        """Test export checkboxes"""
        # Toggle each export option
        # Verify config updated
        pass

    def test_start_scraping(self):
        """Test start button functionality"""
        # Configure settings
        # Click start
        # Monitor progress
        # Verify completion
        pass
```

---

### 3. INTEGRATION TESTING

#### 3.1 End-to-End Test Scenarios

**Scenario 1: Basic Scraping**
```python
def test_basic_scraping():
    """
    Test: Basic scraping with default settings
    Expected: 5 pages, CSV output, no errors
    """
    config = {
        'city': 'gurgaon',
        'mode': 'full',
        'max_pages': 5,
        'headless': True,
        'individual_pages': False
    }
    # Run scraping
    # Validate output
    # Check metrics
```

**Scenario 2: Multi-City Scraping**
```python
def test_multi_city():
    """
    Test: Multiple cities with incremental mode
    Expected: All cities scraped, incremental working
    """
    config = {
        'cities': ['gurgaon', 'mumbai', 'bangalore'],
        'mode': 'incremental',
        'max_pages': 10
    }
    # Run scraping
    # Validate each city output
```

**Scenario 3: Individual Pages with Timing**
```python
def test_individual_pages_timing():
    """
    Test: Individual pages with custom timing
    Expected: Delays within specified range
    """
    config = {
        'city': 'gurgaon',
        'max_pages': 3,
        'individual_pages': True,
        'individual_delay_min': 2,
        'individual_delay_max': 4
    }
    # Run scraping
    # Measure actual delays
    # Validate timing compliance
```

---

### 4. VALIDATION CRITERIA

#### 4.1 Setting Validation

| Setting | Validation Method | Pass Criteria |
|---------|-------------------|---------------|
| Max Pages | Count pages scraped | Exactly max_pages or less (if fewer available) |
| Page Delay | Measure time between pages | Within min-max range ±10% |
| Individual Delay | Measure time between properties | Within min-max range ±10% |
| Batch Size | Count properties per batch | Exactly batch_size (except last batch) |
| Workers | Count concurrent processes | Exactly max_workers |
| Export Formats | Check file existence | All enabled formats present |

#### 4.2 Output Validation

**CSV Validation**:
```python
import pandas as pd

def validate_csv_output(file_path):
    df = pd.read_csv(file_path)

    # Check required columns
    required_cols = ['title', 'price', 'area', 'locality']
    assert all(col in df.columns for col in required_cols)

    # Check data completeness
    completeness = (df.notna().sum() / len(df)) * 100
    assert completeness.mean() > 85  # 85% minimum

    # Check row count
    assert len(df) > 0
```

**JSON Validation**:
```python
import json

def validate_json_output(file_path):
    with open(file_path) as f:
        data = json.load(f)

    # Check structure
    assert isinstance(data, list)
    assert len(data) > 0

    # Check first property
    prop = data[0]
    assert 'title' in prop
    assert 'price' in prop
```

---

### 5. EDGE CASES & STRESS TESTING

#### 5.1 Edge Cases

**Test Case 5.1.1: Invalid Inputs**
- Max Pages = 0, -1, 10000000
- Delays = 0, -5, 1000
- Empty city selection
- Invalid output directory

**Test Case 5.1.2: Boundary Values**
- Max Pages = 1 (minimum)
- Max Pages = 10000 (very large)
- Delay Min = Delay Max (no range)
- Workers = 1 (sequential)
- Workers = 8 (maximum)

**Test Case 5.1.3: Conflicting Settings**
- Individual pages enabled + incremental mode
- Very short delays + high worker count
- Skip JavaScript + dynamic content extraction

#### 5.2 Stress Testing

**Test Case 5.2.1: Long-Running Scraping**
- Max Pages = 500
- Duration: 2-3 hours
- Monitor: Memory usage, CPU, errors

**Test Case 5.2.2: High Concurrency**
- Workers = 8
- Batch Size = 50
- Monitor: System resources, bot detection

**Test Case 5.2.3: Multiple Cities**
- Cities = 10
- Max Pages = 100 each
- Monitor: Total duration, success rate

---

### 6. TESTING CHECKLIST

#### Pre-Test Setup
- [ ] Clean output directory
- [ ] Reset database
- [ ] Clear logs
- [ ] Verify internet connection
- [ ] Check system resources

#### During Testing
- [ ] Monitor GUI responsiveness
- [ ] Check log output
- [ ] Verify progress updates
- [ ] Monitor system resources
- [ ] Watch for errors

#### Post-Test Validation
- [ ] Verify output files exist
- [ ] Check data completeness
- [ ] Validate timing compliance
- [ ] Review error logs
- [ ] Compare with expected results

---

## TESTING SUMMARY

**Total Test Cases**: 25+
- Manual Tests: 15
- Automated Tests: 5
- Integration Tests: 3
- Edge Cases: 3
- Stress Tests: 3

**Recommended Testing Sequence**:
1. Manual basic settings (1 hour)
2. Manual timing controls (1 hour)
3. Automated setting validation (2 hours)
4. Integration end-to-end (2 hours)
5. Edge cases (1 hour)
6. Stress testing (4 hours)

**Total Testing Time**: ~11 hours for comprehensive validation

---

**Documentation Complete**: Parts A & B
**Total Settings Documented**: 43
**Total Test Cases**: 25+
**Ready for**: Production testing and validation

