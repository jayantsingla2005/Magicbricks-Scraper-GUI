#!/usr/bin/env python3
"""
Executable Package Builder
Create Windows executable with professional installer for MagicBricks scraper.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import json
import zipfile
from typing import Dict, List, Any, Optional


class ExecutablePackageBuilder:
    """
    Professional executable package builder for Windows deployment
    """
    
    def __init__(self, project_root: str = '.'):
        """Initialize package builder"""
        
        self.project_root = Path(project_root).resolve()
        self.build_dir = self.project_root / 'build'
        self.dist_dir = self.project_root / 'dist'
        self.package_dir = self.project_root / 'package'
        
        # Application metadata
        self.app_metadata = {
            'name': 'MagicBricks Property Scraper',
            'version': '1.0.0',
            'description': 'Professional property data extraction tool for MagicBricks',
            'author': 'MagicBricks Scraper Team',
            'company': 'Property Data Solutions',
            'copyright': f'© {datetime.now().year} Property Data Solutions',
            'executable_name': 'MagicBricksScraper.exe',
            'main_script': 'magicbricks_gui.py'
        }
        
        # Required files and dependencies
        self.required_files = [
            'magicbricks_gui.py',
            'integrated_magicbricks_scraper.py',
            'incremental_scraping_system.py',
            'user_mode_options.py',
            'date_parsing_system.py',
            'smart_stopping_logic.py',
            'url_tracking_system.py',
            'multi_city_system.py',
            'error_handling_system.py',
            'multi_city_parallel_processor.py',
            'requirements.txt'
        ]
        
        # Optional files to include if they exist
        self.optional_files = [
            'config.json',
            'cities.json',
            'README.md',
            'LICENSE'
        ]
        
        print("📦 Executable Package Builder Initialized")
        print(f"   📁 Project root: {self.project_root}")
        print(f"   🎯 Target: {self.app_metadata['executable_name']}")
        print(f"   📋 Version: {self.app_metadata['version']}")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        
        print("\n🔍 Checking build dependencies...")
        
        dependencies = {
            'pyinstaller': False,
            'nsis': False,  # For Windows installer
            'required_files': True
        }
        
        # Check PyInstaller
        try:
            import PyInstaller
            dependencies['pyinstaller'] = True
            print("   ✅ PyInstaller available")
        except ImportError:
            print("   ❌ PyInstaller not found")
            print("      Install with: pip install pyinstaller")
        
        # Check NSIS (optional for installer)
        nsis_path = shutil.which('makensis')
        if nsis_path:
            dependencies['nsis'] = True
            print("   ✅ NSIS available for installer creation")
        else:
            print("   ⚠️ NSIS not found (installer creation will be skipped)")
            print("      Download from: https://nsis.sourceforge.io/")
        
        # Check required files
        missing_files = []
        for file_path in self.required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                dependencies['required_files'] = False
        
        if missing_files:
            print(f"   ❌ Missing required files: {missing_files}")
        else:
            print("   ✅ All required files present")
        
        return dependencies
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        
        print("\n📥 Installing build dependencies...")
        
        try:
            # Install PyInstaller
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pyinstaller'
            ], check=True, capture_output=True)
            print("   ✅ PyInstaller installed successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
    
    def create_pyinstaller_spec(self) -> str:
        """Create PyInstaller spec file"""
        
        print("\n📝 Creating PyInstaller specification...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files to include
added_files = [
    ('cities.json', '.'),
    ('config.json', '.'),
]

# Hidden imports for dynamic imports
hidden_imports = [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'sqlite3',
    'pandas',
    'openpyxl',
    'psutil',
    'requests',
    'beautifulsoup4',
    'lxml'
]

a = Analysis(
    ['{self.app_metadata["main_script"]}'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_metadata["executable_name"].replace(".exe", "")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='icon.ico' if Path('icon.ico').exists() else None,
)
'''
        
        spec_path = self.project_root / 'magicbricks_scraper.spec'
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        print(f"   ✅ Spec file created: {spec_path}")
        return str(spec_path)
    
    def create_version_info(self) -> str:
        """Create version info file for Windows executable"""
        
        print("\n📋 Creating version information...")
        
        version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{self.app_metadata["company"]}'),
        StringStruct(u'FileDescription', u'{self.app_metadata["description"]}'),
        StringStruct(u'FileVersion', u'{self.app_metadata["version"]}'),
        StringStruct(u'InternalName', u'{self.app_metadata["name"]}'),
        StringStruct(u'LegalCopyright', u'{self.app_metadata["copyright"]}'),
        StringStruct(u'OriginalFilename', u'{self.app_metadata["executable_name"]}'),
        StringStruct(u'ProductName', u'{self.app_metadata["name"]}'),
        StringStruct(u'ProductVersion', u'{self.app_metadata["version"]}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_path = self.project_root / 'version_info.txt'
        with open(version_path, 'w') as f:
            f.write(version_info)
        
        print(f"   ✅ Version info created: {version_path}")
        return str(version_path)
    
    def build_executable(self, spec_path: str) -> bool:
        """Build executable using PyInstaller"""
        
        print("\n🔨 Building executable with PyInstaller...")
        
        try:
            # Clean previous builds
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
            
            # Run PyInstaller
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                spec_path
            ]
            
            print(f"   🚀 Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   ✅ Executable built successfully")
                
                # Check if executable exists
                exe_path = self.dist_dir / self.app_metadata['executable_name'].replace('.exe', '.exe')
                if exe_path.exists():
                    print(f"   📦 Executable location: {exe_path}")
                    return True
                else:
                    print("   ❌ Executable not found in expected location")
                    return False
            else:
                print(f"   ❌ Build failed with return code: {result.returncode}")
                print(f"   Error output: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Build error: {str(e)}")
            return False
    
    def create_installer_script(self) -> str:
        """Create NSIS installer script"""
        
        print("\n📦 Creating installer script...")
        
        installer_script = f'''!define APPNAME "{self.app_metadata['name']}"
!define COMPANYNAME "{self.app_metadata['company']}"
!define DESCRIPTION "{self.app_metadata['description']}"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/your-repo/magicbricks-scraper"
!define UPDATEURL "https://github.com/your-repo/magicbricks-scraper/releases"
!define ABOUTURL "https://github.com/your-repo/magicbricks-scraper"
!define INSTALLSIZE 150000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${{COMPANYNAME}}\\${{APPNAME}}"

Name "${{APPNAME}}"
Icon "icon.ico"
outFile "MagicBricksScraperInstaller.exe"

!include LogicLib.nsh

page components
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${{If}} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${{EndIf}}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    
    # Files to install
    file /r "dist\\*"
    
    # Create uninstaller
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    # Start Menu
    createDirectory "$SMPROGRAMS\\${{COMPANYNAME}}"
    createShortCut "$SMPROGRAMS\\${{COMPANYNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\{self.app_metadata['executable_name']}" "" "$INSTDIR\\{self.app_metadata['executable_name']}"
    
    # Desktop shortcut
    createShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\{self.app_metadata['executable_name']}" "" "$INSTDIR\\{self.app_metadata['executable_name']}"
    
    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayIcon" "$\\"$INSTDIR\\{self.app_metadata['executable_name']}$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "DisplayVersion" "${{VERSIONMAJOR}}.${{VERSIONMINOR}}.${{VERSIONBUILD}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}" "EstimatedSize" ${{INSTALLSIZE}}
sectionEnd

section "uninstall"
    # Remove Start Menu launcher
    delete "$SMPROGRAMS\\${{COMPANYNAME}}\\${{APPNAME}}.lnk"
    rmDir "$SMPROGRAMS\\${{COMPANYNAME}}"
    
    # Remove Desktop shortcut
    delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    # Remove files
    rmDir /r "$INSTDIR"
    
    # Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{COMPANYNAME}} ${{APPNAME}}"
sectionEnd
'''
        
        installer_path = self.project_root / 'installer.nsi'
        with open(installer_path, 'w') as f:
            f.write(installer_script)
        
        print(f"   ✅ Installer script created: {installer_path}")
        return str(installer_path)
    
    def build_installer(self, installer_script: str) -> bool:
        """Build Windows installer using NSIS"""
        
        print("\n🏗️ Building Windows installer...")
        
        try:
            # Check if NSIS is available
            if not shutil.which('makensis'):
                print("   ⚠️ NSIS not found - skipping installer creation")
                return False
            
            # Run NSIS
            cmd = ['makensis', installer_script]
            
            print(f"   🚀 Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   ✅ Installer built successfully")
                
                installer_exe = self.project_root / 'MagicBricksScraperInstaller.exe'
                if installer_exe.exists():
                    print(f"   📦 Installer location: {installer_exe}")
                    return True
                else:
                    print("   ❌ Installer not found in expected location")
                    return False
            else:
                print(f"   ❌ Installer build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Installer build error: {str(e)}")
            return False
    
    def create_portable_package(self) -> bool:
        """Create portable ZIP package"""
        
        print("\n📦 Creating portable package...")
        
        try:
            # Create package directory
            self.package_dir.mkdir(exist_ok=True)
            
            # Copy executable and dependencies
            if self.dist_dir.exists():
                portable_dir = self.package_dir / 'MagicBricksScraper_Portable'
                if portable_dir.exists():
                    shutil.rmtree(portable_dir)
                
                shutil.copytree(self.dist_dir, portable_dir)
                
                # Add README for portable version
                readme_content = f"""# {self.app_metadata['name']} - Portable Version

## Quick Start
1. Extract this folder to your desired location
2. Run {self.app_metadata['executable_name']} to start the application
3. No installation required!

## Features
- Professional property data extraction from MagicBricks
- Incremental scraping with 60-75% time savings
- Multi-city parallel processing
- User-friendly GUI interface
- Comprehensive error handling
- Multiple export formats (CSV, Excel, JSON)

## System Requirements
- Windows 10 or later
- Internet connection
- 4GB RAM recommended
- 500MB free disk space

## Support
For support and updates, visit: https://github.com/your-repo/magicbricks-scraper

Version: {self.app_metadata['version']}
Build Date: {datetime.now().strftime('%Y-%m-%d')}
"""
                
                readme_path = portable_dir / 'README.txt'
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                
                # Create ZIP archive
                zip_path = self.package_dir / f'MagicBricksScraper_v{self.app_metadata["version"]}_Portable.zip'
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(portable_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arc_path = file_path.relative_to(portable_dir.parent)
                            zipf.write(file_path, arc_path)
                
                print(f"   ✅ Portable package created: {zip_path}")
                return True
            else:
                print("   ❌ Distribution directory not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Portable package creation failed: {str(e)}")
            return False
    
    def generate_build_report(self, build_results: Dict[str, bool]) -> str:
        """Generate build report"""
        
        report = []
        report.append("📦 EXECUTABLE PACKAGE BUILD REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Application: {self.app_metadata['name']}")
        report.append(f"Version: {self.app_metadata['version']}")
        report.append("")
        
        # Build results
        report.append("🔨 BUILD RESULTS")
        report.append("-" * 40)
        
        for component, success in build_results.items():
            status = "✅ Success" if success else "❌ Failed"
            report.append(f"{component.replace('_', ' ').title()}: {status}")
        
        report.append("")
        
        # File locations
        report.append("📁 OUTPUT FILES")
        report.append("-" * 40)
        
        if build_results.get('executable', False):
            exe_path = self.dist_dir / self.app_metadata['executable_name'].replace('.exe', '.exe')
            if exe_path.exists():
                report.append(f"Executable: {exe_path}")
        
        if build_results.get('installer', False):
            installer_path = self.project_root / 'MagicBricksScraperInstaller.exe'
            if installer_path.exists():
                report.append(f"Installer: {installer_path}")
        
        if build_results.get('portable', False):
            zip_path = self.package_dir / f'MagicBricksScraper_v{self.app_metadata["version"]}_Portable.zip'
            if zip_path.exists():
                report.append(f"Portable: {zip_path}")
        
        # Deployment instructions
        report.append("")
        report.append("🚀 DEPLOYMENT INSTRUCTIONS")
        report.append("-" * 40)
        report.append("1. Test the executable on a clean Windows system")
        report.append("2. Verify all features work correctly")
        report.append("3. Test the installer on different Windows versions")
        report.append("4. Create release notes and documentation")
        report.append("5. Upload to distribution platform")
        
        return "\n".join(report)
    
    def build_complete_package(self) -> Dict[str, bool]:
        """Build complete deployment package"""
        
        print("📦 BUILDING COMPLETE DEPLOYMENT PACKAGE")
        print("="*60)
        
        build_results = {
            'dependencies': False,
            'spec_file': False,
            'version_info': False,
            'executable': False,
            'installer': False,
            'portable': False
        }
        
        # Check and install dependencies
        deps = self.check_dependencies()
        if not deps['pyinstaller']:
            if self.install_dependencies():
                build_results['dependencies'] = True
            else:
                print("❌ Failed to install dependencies")
                return build_results
        else:
            build_results['dependencies'] = True
        
        if not deps['required_files']:
            print("❌ Missing required files - cannot proceed")
            return build_results
        
        # Create build files
        try:
            spec_path = self.create_pyinstaller_spec()
            build_results['spec_file'] = True
            
            version_path = self.create_version_info()
            build_results['version_info'] = True
            
            # Build executable
            if self.build_executable(spec_path):
                build_results['executable'] = True
                
                # Create installer if NSIS is available
                if deps['nsis']:
                    installer_script = self.create_installer_script()
                    if self.build_installer(installer_script):
                        build_results['installer'] = True
                
                # Create portable package
                if self.create_portable_package():
                    build_results['portable'] = True
            
        except Exception as e:
            print(f"❌ Build process failed: {str(e)}")
        
        # Generate report
        report = self.generate_build_report(build_results)
        print("\n" + report)
        
        # Save report
        report_path = self.project_root / 'build_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Build report saved: {report_path}")
        
        return build_results


def main():
    """Main package building function"""
    
    try:
        print("📦 MAGICBRICKS SCRAPER PACKAGE BUILDER")
        print("="*60)
        
        # Initialize builder
        builder = ExecutablePackageBuilder()
        
        # Build complete package
        results = builder.build_complete_package()
        
        # Summary
        successful_builds = sum(1 for success in results.values() if success)
        total_builds = len(results)
        
        print(f"\n✅ Package building completed!")
        print(f"📊 Success rate: {successful_builds}/{total_builds} components")
        
        if results['executable']:
            print("🎉 Executable ready for distribution!")
        
        if results['installer']:
            print("🎉 Professional installer created!")
        
        if results['portable']:
            print("🎉 Portable package ready!")
        
        return successful_builds == total_builds
        
    except Exception as e:
        print(f"❌ Package building failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
