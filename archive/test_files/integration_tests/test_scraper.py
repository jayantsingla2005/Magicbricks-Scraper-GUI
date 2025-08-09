#!/usr/bin/env python3
"""
Test script for MagicBricks Production Scraper
Validates configuration, models, and basic functionality
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

def test_configuration():
    """Test configuration file loading"""
    print("🔧 Testing configuration loading...")
    
    try:
        config_path = "config/scraper_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required sections
        required_sections = ['website', 'selectors', 'browser', 'delays', 'retry', 'output', 'logging']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False
        
        print("✅ Configuration loaded successfully")
        print(f"   📊 Max pages: {config['website']['max_pages']}")
        print(f"   🏠 Properties per page: {config['website']['properties_per_page']}")
        print(f"   🌐 Headless mode: {config['browser']['headless']}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_property_model():
    """Test property data model"""
    print("\n📊 Testing property data model...")
    
    try:
        from src.models.property_model import PropertyModel
        
        # Create test property
        test_property = PropertyModel(
            title="3 BHK Apartment in Sector 45, Gurgaon",
            price="₹ 1.2 Cr",
            super_area="1500 sqft",
            bedrooms=3,
            bathrooms=2,
            society="DLF Phase 2",
            locality="Sector 45"
        )
        
        # Test validation
        if not test_property.is_valid():
            print("❌ Property validation failed")
            return False
        
        # Test data conversion
        csv_data = test_property.to_csv_row()
        json_data = test_property.to_dict()
        
        print("✅ Property model working correctly")
        print(f"   🏠 Title: {test_property.title}")
        print(f"   💰 Price: {test_property.price} (Numeric: ₹{test_property.price_numeric:,.0f})")
        print(f"   📐 Area: {test_property.super_area} (Numeric: {test_property.super_area_numeric})")
        print(f"   🎯 Quality Score: {test_property.data_quality_score:.1f}%")
        return True
        
    except Exception as e:
        print(f"❌ Property model test failed: {str(e)}")
        return False

def test_logger():
    """Test logging system"""
    print("\n📝 Testing logging system...")
    
    try:
        from src.utils.logger import ScraperLogger
        
        # Load config for logger
        with open("config/scraper_config.json", 'r') as f:
            config = json.load(f)
        
        # Create logger
        logger = ScraperLogger(config)
        
        # Test logging methods
        logger.log_page_start(1, "https://test.com")
        logger.log_page_complete(1, 30, 28, 26, 2)
        logger.log_error("TEST_ERROR", "This is a test error", 1, 5)
        
        print("✅ Logging system working correctly")
        print(f"   📁 Log file: {logger.log_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Logger test failed: {str(e)}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        ('selenium', 'selenium'),
        ('beautifulsoup4', 'bs4'),
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('lxml', 'lxml')
    ]
    
    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - MISSING")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def test_directory_structure():
    """Test directory structure"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'config',
        'src',
        'src/core',
        'src/models',
        'src/utils'
    ]
    
    required_files = [
        'config/scraper_config.json',
        'src/core/modern_scraper.py',
        'src/models/property_model.py',
        'src/utils/logger.py',
        'main_scraper.py',
        'requirements.txt'
    ]
    
    # Check directories
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"❌ Missing directory: {directory}")
            return False
        print(f"   ✅ {directory}/")
    
    # Check files
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
        print(f"   ✅ {file_path}")
    
    print("✅ Directory structure correct")
    return True

def test_output_directory():
    """Test output directory creation"""
    print("\n💾 Testing output directory...")
    
    try:
        # Load config to get output directory
        with open("config/scraper_config.json", 'r') as f:
            config = json.load(f)
        
        output_dir = Path(config['output']['export_directory'])
        output_dir.mkdir(exist_ok=True)
        
        if output_dir.exists():
            print(f"✅ Output directory ready: {output_dir}")
            return True
        else:
            print(f"❌ Failed to create output directory: {output_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Output directory test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 MAGICBRICKS SCRAPER - SYSTEM TESTS")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("Property Model", test_property_model),
        ("Logging System", test_logger),
        ("Output Directory", test_output_directory)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n⚠️  {test_name} test failed")
        except Exception as e:
            print(f"\n💥 {test_name} test crashed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Scraper ready for use!")
        print("\nNext steps:")
        print("1. Run test mode: python main_scraper.py --test-mode")
        print("2. Check output files in the output/ directory")
        print("3. Review logs for any issues")
        return True
    else:
        print("❌ SOME TESTS FAILED - Please fix issues before running scraper")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Verify configuration file syntax")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
