# MagicBricks Scraper - Extraction Scope Documentation
## Comprehensive Guide to Data Extraction Capabilities

**Document Date**: 2025-10-02  
**Purpose**: Clarify what data the scraper extracts and how

---

## EXECUTIVE SUMMARY

### Extraction Modes

The MagicBricks scraper operates in **TWO PHASES**:

1. **Phase 1: Listing Page Extraction** (ALWAYS ENABLED)
   - Extracts property cards from search result pages
   - Fast, efficient, bulk data collection
   - ~30 properties per page
   - **Default**: ENABLED

2. **Phase 2: Individual Property Page Extraction** (OPTIONAL)
   - Visits each property's detailed page
   - Extracts comprehensive property information
   - Slower, more detailed data collection
   - **Default**: DISABLED (requires explicit flag)

---

## PART 1: LISTING PAGE EXTRACTION (Phase 1)

### What is Extracted?

**Source**: Property listing/search result pages  
**URL Pattern**: `https://www.magicbricks.com/property-for-sale-in-{city}-pppfs?page={N}`  
**Status**: ✅ **ALWAYS ENABLED**

### Data Fields Extracted (Listing Pages)

| Field Category | Fields Extracted | Completeness |
|----------------|------------------|--------------|
| **Basic Info** | title, price, area, property_url | 95-100% |
| **Location** | locality, society | 85-94% |
| **Property Details** | property_type, bathrooms, balcony, floor_details | 85-92% |
| **Status & Features** | status, furnishing, facing, parking | 76-92% |
| **Ownership** | ownership, transaction | 70-85% |
| **Metadata** | page_number, property_index, scraped_at, posting_date | 100% |
| **Premium Info** | is_premium, premium_type, premium_indicators | 100% |
| **Phase 4 Enhancements** | carpet_area, builtup_area, super_area, plot_area | NEW |

**Total Fields**: 30+ fields per property  
**Average Completeness**: 86.2% (improved to 93%+ with Phase 4 enhancements)

### Performance Metrics (Listing Pages Only)

- **Speed**: 291.4 properties/minute
- **Efficiency**: 0.21 seconds/property
- **Page Load**: 6.18 seconds/page
- **Consistency**: 30 properties/page (stable)

### Configuration

```python
# Listing page extraction is ALWAYS enabled
result = scraper.scrape_properties_with_incremental(
    city='gurgaon',
    mode=ScrapingMode.FULL,
    max_pages=100,
    include_individual_pages=False,  # Phase 2 DISABLED
    export_formats=['csv', 'json']
)
```

---

## PART 2: INDIVIDUAL PROPERTY PAGE EXTRACTION (Phase 2)

### What is Extracted?

**Source**: Individual property detail pages  
**URL Pattern**: `https://www.magicbricks.com/propertydetail/...`  
**Status**: ⚠️ **OPTIONAL** (requires `include_individual_pages=True`)

### Additional Data Fields (Individual Pages)

| Field Category | Additional Fields | Benefit |
|----------------|-------------------|---------|
| **Detailed Description** | Full property description | More context |
| **Amenities** | Complete amenities list | Better filtering |
| **Property Features** | Detailed features | Comprehensive data |
| **Contact Information** | Owner/dealer details | Lead generation |
| **Images** | Image URLs and count | Visual data |
| **Location Details** | Precise location info | Better mapping |

**Additional Fields**: 10-15 extra fields  
**Total Fields**: 40-45 fields per property

### Performance Metrics (Individual Pages)

- **Speed**: 18.1 properties/minute (concurrent mode)
- **Speed**: 8-12 properties/minute (sequential mode)
- **Efficiency**: 3.3 seconds/property (concurrent)
- **Efficiency**: 5-7 seconds/property (sequential)

### Configuration

```python
# Enable individual property page extraction
result = scraper.scrape_properties_with_incremental(
    city='gurgaon',
    mode=ScrapingMode.FULL,
    max_pages=100,
    include_individual_pages=True,  # Phase 2 ENABLED
    export_formats=['csv', 'json']
)
```

### Modes Available

1. **Sequential Mode** (Default for individual pages)
   - One property at a time
   - More stable, less resource-intensive
   - 8-12 properties/minute

2. **Concurrent Mode** (Advanced)
   - Multiple properties in parallel (4 workers)
   - Faster but more resource-intensive
   - 18.1 properties/minute

---

## PART 3: TWO-PHASE SCRAPING WORKFLOW

### Complete Workflow

```
START
  ↓
PHASE 1: Listing Pages
  ├─ Load search result page
  ├─ Extract 30 property cards
  ├─ Parse basic fields (30+ fields)
  ├─ Store property URLs
  └─ Repeat for N pages
  ↓
[CHECKPOINT: Listing data complete]
  ↓
PHASE 2: Individual Pages (if enabled)
  ├─ Load each property URL
  ├─ Extract detailed fields (10-15 additional)
  ├─ Merge with listing data
  └─ Update export files
  ↓
END
```

### Time Estimates

| Scenario | Pages | Properties | Phase 1 Time | Phase 2 Time | Total Time |
|----------|-------|------------|--------------|--------------|------------|
| **Listing Only** | 100 | 3,000 | ~10 min | N/A | ~10 min |
| **With Individual (Sequential)** | 100 | 3,000 | ~10 min | ~250 min | ~260 min (4.3 hrs) |
| **With Individual (Concurrent)** | 100 | 3,000 | ~10 min | ~165 min | ~175 min (2.9 hrs) |

---

## PART 4: CONFIGURATION FLAGS

### Main Method Signature

```python
def scrape_properties_with_incremental(
    self,
    city: str,
    mode: ScrapingMode = ScrapingMode.INCREMENTAL,
    max_pages: int = None,
    include_individual_pages: bool = False,  # KEY FLAG
    export_formats: List[str] = ['csv'],
    progress_callback=None,
    force_rescrape_individual: bool = False
) -> Dict[str, Any]:
```

### Key Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `include_individual_pages` | `False` | Enable/disable Phase 2 |
| `force_rescrape_individual` | `False` | Re-scrape already scraped properties |
| `use_concurrent` | `False` | Use concurrent mode for individual pages |

---

## PART 5: CURRENT TESTING CONFIGURATION

### Phase 3 Large-Scale Test (Completed)

```python
test_config = {
    'city': 'gurgaon',
    'mode': ScrapingMode.FULL,
    'max_pages': 15,
    'headless': True,
    'incremental_enabled': False,
    'individual_pages': False,  # ← LISTING PAGES ONLY
    'export_formats': ['csv', 'json']
}
```

**Result**: 450 properties in 1.54 minutes (291.4 props/min)

### Recommended Configuration for Multi-City Testing

**Option 1: Fast Testing (Listing Pages Only)**
```python
test_config = {
    'city': 'gurgaon',
    'mode': ScrapingMode.FULL,
    'max_pages': 100,
    'include_individual_pages': False,  # Fast
    'export_formats': ['csv', 'json']
}
```
**Estimated Time**: ~10 minutes per city (3,000 properties)

**Option 2: Comprehensive Testing (With Individual Pages)**
```python
test_config = {
    'city': 'gurgaon',
    'mode': ScrapingMode.FULL,
    'max_pages': 100,
    'include_individual_pages': True,  # Comprehensive
    'export_formats': ['csv', 'json']
}
```
**Estimated Time**: ~3-4 hours per city (3,000 properties with details)

---

## PART 6: RECOMMENDATIONS FOR MULTI-CITY TESTING

### Recommended Approach

**For 5 cities × 100 pages each:**

1. **Phase 1: Listing Pages Only** (RECOMMENDED)
   - Test all 5 cities with listing pages only
   - Fast, efficient, validates core extraction
   - Total time: ~50 minutes (5 cities × 10 min)
   - Total properties: ~15,000

2. **Phase 2: Sample Individual Pages** (OPTIONAL)
   - Test 1-2 cities with individual pages
   - Validates individual page extraction
   - Total time: ~6-8 hours (2 cities × 3-4 hrs)
   - Total properties: ~6,000 with details

### Rationale

- **Listing pages** provide 86.2-93% field completeness
- **Individual pages** add 10-15 extra fields but take 15-25x longer
- **For validation testing**, listing pages are sufficient
- **For production use**, individual pages can be enabled selectively

---

## PART 7: DECISION FOR MULTI-CITY TESTING

### Recommended Configuration

```python
# Multi-City Test Configuration
test_config = {
    'cities': ['gurgaon', 'mumbai', 'bangalore', 'pune', 'hyderabad'],
    'mode': ScrapingMode.FULL,
    'max_pages': 100,
    'include_individual_pages': False,  # ← LISTING PAGES ONLY
    'export_formats': ['csv', 'json']
}
```

**Justification**:
1. ✅ **Fast**: 50 minutes total vs 15-20 hours
2. ✅ **Sufficient**: 86.2-93% field completeness
3. ✅ **Validates**: Core extraction improvements (status, area types)
4. ✅ **Scalable**: Can test more cities/pages
5. ✅ **Production-ready**: Listing data is primary use case

---

## SUMMARY

### Current Extraction Scope

**Phase 1: Listing Pages**
- ✅ ALWAYS ENABLED
- ✅ 30+ fields per property
- ✅ 86.2-93% completeness
- ✅ 291.4 properties/minute
- ✅ PRIMARY DATA SOURCE

**Phase 2: Individual Pages**
- ⚠️ OPTIONAL (disabled by default)
- ⚠️ 40-45 fields per property
- ⚠️ 18.1 properties/minute (concurrent)
- ⚠️ SUPPLEMENTARY DATA SOURCE

### For Multi-City Testing

**Recommended**: Listing pages only (`include_individual_pages=False`)

**Reason**: Fast, efficient, validates core improvements, production-ready

---

**Documentation Complete**: 2025-10-02  
**Status**: ✅ CLARIFIED  
**Next**: Multi-City Testing (Listing Pages Only)

