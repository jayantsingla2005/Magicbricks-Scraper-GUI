#!/usr/bin/env python3
"""
Modular MagicBricks GUI - Clean, maintainable, and user-friendly
Refactored from the original 3112-line monolithic GUI into modular components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
from datetime import datetime
from typing import Dict, Any

# Import modular components
from gui_components.style_manager import StyleManager
from gui_components.configuration_panel import ConfigurationPanel
from gui_components.monitoring_panel import MonitoringPanel

# Import scraper components
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


class ModularMagicBricksGUI:
    """
    Modern, modular GUI for MagicBricks scraper
    Clean architecture with separated concerns
    """
    
    def __init__(self):
        """Initialize the modular GUI"""
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("🏠 MagicBricks Property Scraper - Professional Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize components
        self.style_manager = StyleManager()
        self.style_manager.setup_styles(self.root)
        
        # Scraping state
        self.is_scraping = False
        self.scraper = None
        self.scraping_thread = None
        self.message_queue = queue.Queue()
        
        # Create interface
        self.create_interface()
        
        # Start message processing
        self.process_messages()
        
        print("🎮 Modular MagicBricks GUI v3.0 Initialized")
        print("   🧩 Modular architecture with separated components")
        print("   🎨 Modern, vibrant design for non-technical users")
        print("   📊 Real-time progress monitoring")
    
    def create_interface(self):
        """Create the main interface"""
        
        # Header section
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create header section"""
        
        header_frame = tk.Frame(self.root, bg=self.style_manager.get_color('bg_header'), height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.style_manager.get_color('bg_header'))
        header_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)
        
        # Title and subtitle
        title_label = ttk.Label(header_content, 
                               text="🏠 MagicBricks Property Scraper",
                               style='Header.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_content,
                                  text="Professional real estate data extraction - Simple, Fast, Reliable",
                                  style='Subheader.TLabel')
        subtitle_label.pack(anchor=tk.W)
    
    def create_main_content(self):
        """Create main content area with modular panels"""
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.style_manager.get_color('bg_main'))
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configuration panel (left side)
        self.config_panel = ConfigurationPanel(
            parent=main_container,
            style_manager=self.style_manager,
            config_callback=self.on_config_change
        )
        
        # Monitoring panel (right side)
        self.monitoring_panel = MonitoringPanel(
            parent=main_container,
            style_manager=self.style_manager
        )
    
    def create_footer(self):
        """Create footer section"""
        
        footer_frame = tk.Frame(self.root, bg=self.style_manager.get_color('bg_header'), height=50)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        # Footer content
        footer_content = tk.Frame(footer_frame, bg=self.style_manager.get_color('bg_header'))
        footer_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=15)
        
        # Status on left
        status_label = ttk.Label(footer_content, 
                               text="Ready for scraping",
                               font=self.style_manager.get_font('body'),
                               background=self.style_manager.get_color('bg_header'),
                               foreground=self.style_manager.get_color('text_white'))
        status_label.pack(side=tk.LEFT)
        
        # Version on right
        version_label = ttk.Label(footer_content, 
                                text="v3.0 Modular Edition",
                                font=self.style_manager.get_font('small'),
                                background=self.style_manager.get_color('bg_header'),
                                foreground=self.style_manager.get_color('primary_light'))
        version_label.pack(side=tk.RIGHT)
    
    def on_config_change(self, config: Dict[str, Any], action: str = None):
        """Handle configuration changes"""
        
        if action == 'start':
            self.start_scraping(config)
        elif action == 'stop':
            self.stop_scraping()
        else:
            # Configuration updated
            self.monitoring_panel.log_message(f"Configuration updated: {action or 'settings changed'}", "INFO")
    
    def start_scraping(self, config: Dict[str, Any]):
        """Start scraping with given configuration"""
        
        if self.is_scraping:
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
        
        try:
            # Validate configuration
            if not self.validate_config(config):
                return
            
            # Update UI state
            self.is_scraping = True
            self.config_panel.start_button.config(state='disabled')
            self.config_panel.stop_button.config(state='normal')
            
            # Reset monitoring
            self.monitoring_panel.reset_progress()
            self.monitoring_panel.set_scraping_state(True)
            
            # Start scraping thread
            self.scraping_thread = threading.Thread(
                target=self.run_scraping,
                args=(config,),
                daemon=True
            )
            self.scraping_thread.start()
            
        except Exception as e:
            self.monitoring_panel.show_error(f"Failed to start scraping: {str(e)}")
            self.reset_ui_state()
    
    def stop_scraping(self):
        """Stop scraping process"""
        
        if not self.is_scraping:
            return
        
        self.is_scraping = False
        self.monitoring_panel.set_scraping_state(False)
        self.reset_ui_state()
    
    def run_scraping(self, config: Dict[str, Any]):
        """Run scraping in background thread"""
        
        try:
            # Initialize scraper
            self.scraper = IntegratedMagicBricksScraper(
                headless=True,
                incremental_enabled=True
            )
            
            # Create progress callback
            def progress_callback(progress_data):
                """Handle progress updates"""
                try:
                    # Calculate progress percentage
                    current_page = progress_data.get('current_page', 0)
                    total_pages = progress_data.get('total_pages', 1)
                    progress_percentage = min((current_page / total_pages) * 100, 100)
                    
                    # Prepare statistics
                    stats = {
                        'pages_scraped': current_page,
                        'properties_found': progress_data.get('properties_found', 0),
                        'properties_saved': progress_data.get('properties_found', 0),
                        'current_phase': progress_data.get('phase', 'listing_extraction').replace('_', ' ').title(),
                        'duration': self.format_duration(time.time() - self.scraping_start_time),
                    }
                    
                    # Calculate speed
                    elapsed = time.time() - self.scraping_start_time
                    if elapsed > 0:
                        props_per_min = (stats['properties_found'] * 60) / elapsed
                        stats['speed'] = f"{props_per_min:.1f} props/min"
                    
                    # Estimate remaining time
                    if current_page > 0 and total_pages > current_page:
                        avg_time_per_page = elapsed / current_page
                        remaining_pages = total_pages - current_page
                        remaining_seconds = remaining_pages * avg_time_per_page
                        stats['estimated_remaining'] = self.format_duration(remaining_seconds)
                    
                    # Queue updates
                    self.message_queue.put(('progress', progress_percentage))
                    self.message_queue.put(('stats', stats))
                    self.message_queue.put(('status', f"Scraping page {current_page}/{total_pages}"))
                    
                except Exception as e:
                    self.message_queue.put(('log', f"Progress callback error: {str(e)}", 'ERROR'))
            
            # Store start time
            self.scraping_start_time = time.time()
            
            # Determine export formats
            export_formats = []
            if config.get('export_csv', True):
                export_formats.append('csv')
            if config.get('export_json', False):
                export_formats.append('json')
            if config.get('export_excel', False):
                export_formats.append('excel')
            if config.get('export_database', True):
                export_formats.append('database')
            
            # Start scraping
            result = self.scraper.scrape_properties_with_incremental(
                city=config.get('city', 'gurgaon'),
                mode=ScrapingMode.INCREMENTAL,
                max_pages=config.get('max_pages', 100),
                include_individual_pages=config.get('individual_pages', False),
                export_formats=export_formats,
                progress_callback=progress_callback,
                force_rescrape_individual=config.get('force_rescrape', False)
            )
            
            # Handle results
            if result.get('success', False):
                final_stats = result.get('session_stats', {})
                self.message_queue.put(('completion', final_stats))
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.message_queue.put(('error', error_msg))
                
        except Exception as e:
            self.message_queue.put(('error', f"Scraping failed: {str(e)}"))
        
        finally:
            # Clean up
            if self.scraper:
                self.scraper.close()
            self.message_queue.put(('finished', None))
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate scraping configuration"""
        
        # Check required fields
        if not config.get('city'):
            messagebox.showerror("Error", "Please select a city")
            return False
        
        # Check max pages
        max_pages = config.get('max_pages', 0)
        if max_pages <= 0 or max_pages > 1000:
            messagebox.showerror("Error", "Please enter a valid number of pages (1-1000)")
            return False
        
        # Check export formats
        export_any = any([
            config.get('export_csv', False),
            config.get('export_json', False),
            config.get('export_excel', False),
            config.get('export_database', False)
        ])
        
        if not export_any:
            messagebox.showerror("Error", "Please select at least one export format")
            return False
        
        return True
    
    def process_messages(self):
        """Process messages from scraping thread"""
        
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == 'progress':
                    self.monitoring_panel.update_progress(data)
                
                elif message_type == 'stats':
                    self.monitoring_panel.update_statistics(data)
                
                elif message_type == 'status':
                    self.monitoring_panel.update_status(data)
                
                elif message_type == 'log':
                    if isinstance(data, tuple):
                        message, level = data[0], data[1]
                    else:
                        message, level = data, 'INFO'
                    self.monitoring_panel.log_message(message, level)
                
                elif message_type == 'completion':
                    self.monitoring_panel.show_completion(data)
                    self.reset_ui_state()
                
                elif message_type == 'error':
                    self.monitoring_panel.show_error(data)
                    self.reset_ui_state()
                
                elif message_type == 'finished':
                    self.reset_ui_state()
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def reset_ui_state(self):
        """Reset UI to ready state"""
        
        self.is_scraping = False
        self.config_panel.start_button.config(state='normal')
        self.config_panel.stop_button.config(state='disabled')
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}:{secs:02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}:{minutes:02d}:00"
    
    def run(self):
        """Run the GUI application"""
        
        try:
            self.monitoring_panel.log_message("🎉 MagicBricks GUI v3.0 started successfully!", "SUCCESS")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.monitoring_panel.log_message("Application interrupted by user", "WARNING")
        except Exception as e:
            self.monitoring_panel.log_message(f"Application error: {str(e)}", "ERROR")
        finally:
            if self.scraper:
                self.scraper.close()


def main():
    """Main function to run the modular GUI"""
    
    try:
        app = ModularMagicBricksGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start GUI application: {str(e)}")


if __name__ == "__main__":
    main()
