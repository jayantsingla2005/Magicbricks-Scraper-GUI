#!/usr/bin/env python3
"""
Comprehensive Test Runner for Refactored MagicBricks Scraper
Runs all unit tests and generates detailed report
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

def run_all_tests():
    """Run all unit tests and generate report"""
    
    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE - Refactored MagicBricks Scraper")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())

