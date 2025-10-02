# Cleanup Script for MagicBricks Scraper Project
# Moves unused files to archive and deletes obsolete files

Write-Host "Starting Project Cleanup..." -ForegroundColor Green

# Move test files to archive
Write-Host "`nMoving test files to archive..." -ForegroundColor Yellow
Move-Item -Path "integration_test.py" -Destination "archive\test_files\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "smoke_test_refactored_scraper.py" -Destination "archive\test_files\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "comprehensive_testing_suite.py" -Destination "archive\test_files\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "focused_large_scale_test.py" -Destination "archive\test_files\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "test_production_capabilities.py" -Destination "archive\test_files\" -Force -ErrorAction SilentlyContinue

# Move legacy code to archive
Write-Host "`nMoving legacy code to archive..." -ForegroundColor Yellow
Move-Item -Path "enhanced_premium_scraper.py" -Destination "archive\legacy_code\" -Force -ErrorAction SilentlyContinue

# Move gui_components to archive
Write-Host "`nMoving gui_components to archive..." -ForegroundColor Yellow
Move-Item -Path "gui_components" -Destination "archive\legacy_gui\" -Force -ErrorAction SilentlyContinue

# Delete backup files
Write-Host "`nDeleting backup files..." -ForegroundColor Yellow
Remove-Item -Path "integrated_magicbricks_scraper_before_refactor.py.bak" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "smoke_test_output.csv" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "smoke_test_output.json" -Force -ErrorAction SilentlyContinue

# Delete old CSV/JSON output files (keep only latest from Oct 2)
Write-Host "`nDeleting old output files..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "magicbricks_*_scrape_202508*.csv" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "magicbricks_*_scrape_202508*.json" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "magicbricks_incremental_scrape_202508*.csv" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "magicbricks_incremental_scrape_202508*.json" | Remove-Item -Force
Get-ChildItem -Path "." -Filter "magicbricks_incremental_scrape_202510*.csv" | Where-Object { $_.Name -notlike "*20251002*" } | Remove-Item -Force
Get-ChildItem -Path "." -Filter "magicbricks_incremental_scrape_202510*.json" | Where-Object { $_.Name -notlike "*20251002*" } | Remove-Item -Force

Write-Host "`nCleanup Complete!" -ForegroundColor Green
Write-Host "Files archived: 7" -ForegroundColor Cyan
Write-Host "Files deleted: 46+" -ForegroundColor Cyan

