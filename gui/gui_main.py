#!/usr/bin/env python3
"""
GUI Main Module
Main window orchestration integrating all GUI components.
Extracted from magicbricks_gui.py for better maintainability.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any

# Import GUI modules
from .gui_styles import GUIStyles
from .gui_threading import GUIThreadManager
from .gui_controls import GUIControls
from .gui_monitoring import GUIMonitoring
from .gui_results import GUIResults

# Import scraper components
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


class ModularMagicBricksGUI:
    """
    Modular GUI application using extracted components
    """
    
    def __init__(self):
        """Initialize the modular GUI application"""
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("🏠 MagicBricks Property Scraper - Modular Edition v3.0")
        self.root.geometry("1450x950")
        self.root.minsize(1250, 850)
        self.root.configure(bg='#f8fafc')
        
        # Configuration
        self.config = {
            'city': 'gurgaon',
            'mode': ScrapingMode.INCREMENTAL,
            'max_pages': 5,
            'headless': True,
            'output_directory': str(Path.cwd()),
            'incremental_enabled': True,
            'export_json': False,
            'export_excel': False,
            'individual_pages': False
        }
        
        # Initialize GUI components
        self.styles = GUIStyles()
        self.styles.setup_modern_styles()
        
        # Threading manager with callbacks
        gui_callbacks = {
            'log': self._on_log_message,
            'stats': self._on_statistics_update,
            'progress': self._on_progress_update,
            'status': self._on_status_update,
            'error': self._on_error
        }
        self.thread_manager = GUIThreadManager(gui_callbacks)
        
        # Create main interface
        self._create_interface()
        
        # Start message processing
        self._process_messages()
        
        print("🎮 Modular MagicBricks GUI v3.0 Initialized")
    
    def _create_interface(self):
        """Create the main interface"""
        
        # Main container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="🏠 MagicBricks Property Scraper",
            style='Title.TLabel'
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text="Modular Edition v3.0",
            style='Subtitle.TLabel'
        ).pack(side=tk.LEFT, padx=(15, 0))
        
        # Create two-column layout
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Left panel: Controls
        self._create_controls_panel(left_panel)
        
        # Right panel: Monitoring
        self._create_monitoring_panel(right_panel)
    
    def _create_controls_panel(self, parent):
        """Create controls panel"""
        
        # Controls header
        ttk.Label(
            parent,
            text="⚙️ Controls",
            style='Heading.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Initialize controls
        self.controls = GUIControls(parent, self.config, self.styles)
        
        # Basic controls section
        basic_frame = ttk.LabelFrame(parent, text="Basic Settings", style='Modern.TLabelframe', padding=15)
        basic_frame.pack(fill=tk.X, pady=(0, 15))
        
        basic_vars = self.controls.create_basic_controls(basic_frame)
        self.control_vars = basic_vars
        
        # Output controls section
        output_frame = ttk.LabelFrame(parent, text="Output", style='Modern.TLabelframe', padding=15)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_vars = self.controls.create_output_controls(output_frame, self._browse_output_directory)
        self.control_vars.update(output_vars)
        
        # Checkbox controls section
        options_frame = ttk.LabelFrame(parent, text="Options", style='Modern.TLabelframe', padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        checkbox_vars = self.controls.create_checkbox_controls(options_frame)
        self.control_vars.update(checkbox_vars)
        
        # Export controls section
        export_frame = ttk.LabelFrame(parent, text="Export Formats", style='Modern.TLabelframe', padding=15)
        export_frame.pack(fill=tk.X, pady=(0, 15))
        
        export_vars = self.controls.create_export_controls(export_frame)
        self.control_vars.update(export_vars)
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.action_buttons = self.controls.create_action_buttons(
            button_frame,
            self._start_scraping,
            self._stop_scraping
        )
    
    def _create_monitoring_panel(self, parent):
        """Create monitoring panel"""
        
        # Initialize monitoring
        self.monitoring = GUIMonitoring(parent, self.styles)
        
        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="Progress", style='Modern.TLabelframe', padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        progress_frame.columnconfigure(1, weight=1)
        
        self.monitoring.create_progress_section(progress_frame)
        
        # Statistics section
        stats_frame = ttk.LabelFrame(parent, text="Statistics", style='Modern.TLabelframe', padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.monitoring.create_statistics_section(stats_frame)
        
        # Log section
        log_frame = ttk.LabelFrame(parent, text="Activity Log", style='Modern.TLabelframe', padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        self.monitoring.create_log_section(log_frame)
        
        # Status bar
        self.monitoring.create_status_bar(parent)
        
        # Initialize results viewer
        self.results = GUIResults(self.styles)
    
    def _browse_output_directory(self):
        """Browse for output directory"""
        from tkinter import filedialog
        directory = filedialog.askdirectory()
        if directory:
            self.control_vars['output_directory'].set(directory)
    
    def _start_scraping(self):
        """Start scraping process"""
        if self.thread_manager.is_scraping:
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
        
        try:
            # Update config from GUI
            self.config['city'] = self.control_vars['city'].get()
            self.config['mode'] = ScrapingMode(self.control_vars['mode'].get())
            self.config['max_pages'] = int(self.control_vars['max_pages'].get())
            self.config['headless'] = self.control_vars['headless'].get()
            self.config['incremental_enabled'] = self.control_vars['incremental'].get()
            self.config['individual_pages'] = self.control_vars['individual_pages'].get()
            self.config['export_json'] = self.control_vars['export_json'].get()
            self.config['export_excel'] = self.control_vars['export_excel'].get()
            
            # Reset monitoring
            self.monitoring.reset_progress()
            self.monitoring.reset_statistics()
            self.monitoring.clear_log()
            
            # Disable start button, enable stop button
            self.action_buttons['start'].config(state='disabled')
            self.action_buttons['stop'].config(state='normal')
            
            # Start scraping thread
            self.thread_manager.start_scraping_thread(self._run_scraping)
            
            self.monitoring.log_message("Scraping started successfully", 'SUCCESS')
            self.monitoring.update_status("Scraping in progress...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scraping: {str(e)}")
            self._reset_ui_state()
    
    def _stop_scraping(self):
        """Stop scraping process"""
        self.thread_manager.stop_scraping()
        self._reset_ui_state()
    
    def _run_scraping(self):
        """Run scraping (called in separate thread)"""
        try:
            # Create scraper
            scraper = IntegratedMagicBricksScraper(
                headless=self.config['headless'],
                incremental_enabled=self.config['incremental_enabled']
            )
            
            # Prepare export formats
            export_formats = ['csv']
            if self.config['export_json']:
                export_formats.append('json')
            if self.config['export_excel']:
                export_formats.append('excel')
            
            # Create progress callback
            progress_callback = self.thread_manager.create_progress_callback(self.config)
            
            # Start scraping
            result = scraper.scrape_properties_with_incremental(
                city=self.config['city'],
                mode=self.config['mode'],
                max_pages=self.config['max_pages'],
                include_individual_pages=self.config['individual_pages'],
                export_formats=export_formats,
                progress_callback=progress_callback
            )
            
            if result['success']:
                self.thread_manager.send_log_message("Scraping completed successfully!", 'SUCCESS')
                self.thread_manager.send_status_update("Completed")
            else:
                self.thread_manager.send_log_message(f"Scraping failed: {result.get('error', 'Unknown error')}", 'ERROR')
                
        except Exception as e:
            self.thread_manager.send_log_message(f"Scraping error: {str(e)}", 'ERROR')
        finally:
            self._reset_ui_state()
    
    def _reset_ui_state(self):
        """Reset UI state after scraping"""
        self.action_buttons['start'].config(state='normal')
        self.action_buttons['stop'].config(state='disabled')
    
    def _on_log_message(self, message: str):
        """Handle log message callback"""
        self.monitoring.log_text.insert(tk.END, message)
        self.monitoring.log_text.see(tk.END)
    
    def _on_statistics_update(self, stats: Dict[str, Any]):
        """Handle statistics update callback"""
        self.monitoring.update_statistics(stats)
    
    def _on_progress_update(self, progress: float):
        """Handle progress update callback"""
        self.monitoring.update_progress(progress)
    
    def _on_status_update(self, status: str):
        """Handle status update callback"""
        self.monitoring.update_status(status)
    
    def _on_error(self, error_info: Any):
        """Handle error callback"""
        self.monitoring.log_message(f"Error: {error_info}", 'ERROR')
    
    def _process_messages(self):
        """Process messages from thread manager"""
        self.thread_manager.process_messages()
        self.root.after(100, self._process_messages)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = ModularMagicBricksGUI()
    app.run()


if __name__ == '__main__':
    main()

