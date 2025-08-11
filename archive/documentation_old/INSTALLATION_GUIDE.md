# MagicBricks Property Scraper - Installation Guide

## Overview

This guide provides detailed installation instructions for the MagicBricks Property Scraper on Windows systems. Choose the installation method that best suits your needs and technical expertise.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (64-bit)
- **Processor**: Intel Core i3 or AMD equivalent
- **Memory**: 4GB RAM
- **Storage**: 500MB free disk space
- **Internet**: Broadband connection
- **Browser**: Chrome (automatically managed)

### Recommended Requirements
- **Operating System**: Windows 11 (64-bit)
- **Processor**: Intel Core i5 or AMD equivalent
- **Memory**: 8GB RAM
- **Storage**: 2GB free disk space
- **Internet**: High-speed broadband
- **Additional**: SSD for better performance

## Installation Methods

### Method 1: Windows Installer (Recommended for Most Users)

#### Step 1: Download the Installer
1. Visit the official releases page
2. Download `MagicBricksScraperInstaller.exe`
3. Verify the file size (approximately 150MB)
4. Check digital signature for authenticity

#### Step 2: Prepare for Installation
1. **Close all running applications**
2. **Disable antivirus temporarily** (if it blocks the installer)
3. **Ensure administrator privileges**
4. **Check available disk space** (minimum 500MB)

#### Step 3: Run the Installer
1. **Right-click** `MagicBricksScraperInstaller.exe`
2. Select **"Run as administrator"**
3. If Windows SmartScreen appears:
   - Click **"More info"**
   - Click **"Run anyway"**

#### Step 4: Installation Wizard
1. **Welcome Screen**
   - Click "Next" to continue
   - Review license agreement

2. **Installation Location**
   - Default: `C:\Program Files\Property Data Solutions\MagicBricks Property Scraper`
   - Click "Browse" to change location
   - Ensure sufficient space available

3. **Component Selection**
   - ✅ Main Application (Required)
   - ✅ Desktop Shortcut (Recommended)
   - ✅ Start Menu Shortcuts (Recommended)
   - ✅ File Associations (Optional)

4. **Installation Progress**
   - Wait for files to be copied
   - Chrome driver will be installed automatically
   - Dependencies will be configured

5. **Completion**
   - ✅ Launch application immediately
   - Click "Finish"

#### Step 5: First Launch Verification
1. Application should start automatically
2. Main window should appear within 10-15 seconds
3. Check "About" menu for version information
4. Verify all menu items are accessible

### Method 2: Portable Version (No Installation Required)

#### Step 1: Download Portable Package
1. Download `MagicBricksScraper_v1.0.0_Portable.zip`
2. File size: approximately 120MB
3. Verify download integrity

#### Step 2: Extract Files
1. **Choose extraction location**
   - Desktop folder (for easy access)
   - Documents folder (for organization)
   - External drive (for portability)

2. **Extract the archive**
   - Right-click the ZIP file
   - Select "Extract All..."
   - Choose destination folder
   - Click "Extract"

#### Step 3: Verify Extraction
1. Navigate to extracted folder
2. Verify these files exist:
   - `MagicBricksScraper.exe` (main executable)
   - `README.txt` (quick start guide)
   - Supporting files and folders

#### Step 4: Create Shortcuts (Optional)
1. **Desktop Shortcut**
   - Right-click `MagicBricksScraper.exe`
   - Select "Create shortcut"
   - Move shortcut to desktop

2. **Start Menu Shortcut**
   - Copy executable path
   - Right-click Start Menu
   - Select "Open file location"
   - Create shortcut in Programs folder

#### Step 5: First Launch
1. Double-click `MagicBricksScraper.exe`
2. Windows may show security warning
3. Click "Run" to proceed
4. Application should start normally

### Method 3: Python Source Installation (Advanced Users)

#### Prerequisites
- Python 3.8 or later
- pip package manager
- Git (optional, for cloning)
- Basic command line knowledge

#### Step 1: Install Python
1. Download Python from python.org
2. **Important**: Check "Add Python to PATH"
3. Install with default settings
4. Verify installation: `python --version`

#### Step 2: Download Source Code
**Option A: Git Clone**
```bash
git clone https://github.com/your-repo/magicbricks-scraper.git
cd magicbricks-scraper
```

**Option B: Direct Download**
1. Download source ZIP from GitHub
2. Extract to desired location
3. Open command prompt in folder

#### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Install Chrome Driver
```bash
# Automatic installation (recommended)
python -c "from selenium import webdriver; webdriver.Chrome()"

# Manual installation if needed
# Download ChromeDriver from https://chromedriver.chromium.org/
# Place in PATH or project folder
```

#### Step 5: Launch Application
```bash
# Run the GUI application
python magicbricks_gui.py

# Alternative: Run from any location
python /path/to/magicbricks_gui.py
```

## Post-Installation Setup

### Initial Configuration
1. **Launch the application**
2. **Set output directory**
   - Click "Settings" → "Output Directory"
   - Choose folder for saved files
   - Ensure write permissions

3. **Test basic functionality**
   - Select a city (e.g., Mumbai)
   - Set max pages to 2
   - Run a test scrape

### Windows Defender Configuration
1. **Add exclusions** (if needed):
   - Go to Windows Security
   - Virus & threat protection
   - Manage settings
   - Add exclusions
   - Add the installation folder

### Firewall Configuration
1. **Allow network access**:
   - Windows may prompt for firewall permission
   - Click "Allow access"
   - Ensure both private and public networks are allowed

### Browser Configuration
- Chrome browser is managed automatically
- No manual configuration required
- Driver updates handled by application

## Troubleshooting Installation Issues

### Common Installation Problems

#### Issue: "Windows protected your PC"
**Cause**: Windows SmartScreen blocking unsigned executable
**Solution**:
1. Click "More info"
2. Click "Run anyway"
3. Alternatively, disable SmartScreen temporarily

#### Issue: "Access denied" during installation
**Cause**: Insufficient permissions
**Solution**:
1. Right-click installer
2. Select "Run as administrator"
3. Ensure user has admin rights

#### Issue: Antivirus blocking installation
**Cause**: False positive detection
**Solution**:
1. Temporarily disable antivirus
2. Add installation folder to exclusions
3. Re-enable antivirus after installation

#### Issue: Installation fails with error
**Cause**: Corrupted download or system issues
**Solution**:
1. Re-download installer
2. Verify file integrity
3. Check available disk space
4. Restart computer and retry

### Runtime Issues

#### Issue: Application won't start
**Symptoms**: No window appears, immediate crash
**Solutions**:
1. **Check system requirements**
2. **Run as administrator**
3. **Install Visual C++ Redistributables**
4. **Update Windows**

#### Issue: "Chrome driver not found"
**Symptoms**: Error message about missing driver
**Solutions**:
1. **Reinstall application** (driver included)
2. **Manual driver installation**:
   - Download ChromeDriver
   - Place in application folder
   - Restart application

#### Issue: Network connection errors
**Symptoms**: Cannot connect to MagicBricks
**Solutions**:
1. **Check internet connection**
2. **Configure firewall**
3. **Check proxy settings**
4. **Verify MagicBricks.com accessibility**

### Performance Issues

#### Issue: Slow startup
**Causes**: System resources, antivirus scanning
**Solutions**:
1. Close unnecessary applications
2. Add antivirus exclusions
3. Install on SSD if available
4. Increase system memory

#### Issue: High memory usage
**Causes**: Large datasets, multiple cities
**Solutions**:
1. Reduce page limits
2. Use incremental mode
3. Process fewer cities simultaneously
4. Restart application periodically

## Uninstallation

### Method 1: Windows Installer Version
1. **Control Panel Method**:
   - Open Control Panel
   - Programs and Features
   - Find "MagicBricks Property Scraper"
   - Click "Uninstall"

2. **Settings Method** (Windows 10/11):
   - Open Settings
   - Apps & features
   - Search for "MagicBricks"
   - Click "Uninstall"

3. **Start Menu Method**:
   - Right-click Start Menu
   - Find application in list
   - Right-click → Uninstall

### Method 2: Portable Version
1. **Delete application folder**
2. **Remove shortcuts** (if created)
3. **Clear temporary files** (optional)

### Method 3: Python Source
1. **Delete source folder**
2. **Uninstall packages** (optional):
   ```bash
   pip uninstall -r requirements.txt
   ```

## Updating the Application

### Automatic Updates (Installer Version)
1. Application checks for updates on startup
2. Notification appears if update available
3. Click "Download" to get latest version
4. Run new installer to update

### Manual Updates
1. **Download latest version**
2. **Backup your data** (optional)
3. **Uninstall old version**
4. **Install new version**
5. **Restore settings** (if needed)

### Portable Version Updates
1. **Download new portable package**
2. **Extract to new folder**
3. **Copy settings** from old version
4. **Delete old folder**

## Support and Resources

### Getting Help
- **Documentation**: Complete user manual available
- **FAQ**: Common questions answered
- **Support Email**: support@magicbricks-scraper.com
- **Community**: User forums and discussions

### Additional Resources
- **Video Tutorials**: Step-by-step installation guides
- **Knowledge Base**: Detailed troubleshooting articles
- **Release Notes**: Update information and changes
- **System Requirements**: Detailed compatibility information

### Reporting Issues
When reporting installation issues, please include:
1. **Operating System** version and architecture
2. **Error messages** (exact text or screenshots)
3. **Installation method** used
4. **System specifications**
5. **Antivirus software** in use

---

**Installation Complete!** 🎉

Your MagicBricks Property Scraper is now ready to use. Launch the application and refer to the User Manual for detailed usage instructions.

For immediate help, check the Quick Start Guide in the main documentation.
