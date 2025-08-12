#!/usr/bin/env python3
"""
Monitoring Panel - Real-time scraping progress and statistics
Displays progress, statistics, and logs in an intuitive way
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from typing import Dict, Any


class MonitoringPanel:
    """
    Real-time monitoring panel for scraping progress
    Designed for clear, intuitive progress tracking
    """
    
    def __init__(self, parent, style_manager):
        """
        Initialize monitoring panel
        
        Args:
            parent: Parent widget
            style_manager: StyleManager instance
        """
        
        self.parent = parent
        self.style_manager = style_manager
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to start scraping")
        self.progress_text_var = tk.StringVar(value="0%")
        
        # Statistics variables
        self.stats_vars = {
            'pages_scraped': tk.StringVar(value='0'),
            'properties_found': tk.StringVar(value='0'),
            'properties_saved': tk.StringVar(value='0'),
            'duration': tk.StringVar(value='0:00'),
            'speed': tk.StringVar(value='0 props/min'),
            'estimated_remaining': tk.StringVar(value='--'),
            'success_rate': tk.StringVar(value='100%'),
            'current_phase': tk.StringVar(value='Ready')
        }
        
        # Create the panel
        self.create_panel()
    
    def create_panel(self):
        """Create the monitoring panel"""
        
        # Main container
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_progress_section()
        self.create_statistics_section()
        self.create_log_section()
    
    def create_progress_section(self):
        """Create progress monitoring section"""
        
        # Progress container
        progress_container = ttk.LabelFrame(self.frame, text="📊 Scraping Progress", style='Card.TLabelframe')
        progress_container.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Progress content
        progress_content = tk.Frame(progress_container, bg=self.style_manager.get_color('bg_card'))
        progress_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Status display
        status_frame = tk.Frame(progress_content, bg=self.style_manager.get_color('bg_card'))
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(status_frame, text="Status:", style='Subtitle.TLabel').pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel')
        status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar section
        progress_bar_frame = tk.Frame(progress_content, bg=self.style_manager.get_color('bg_card'))
        progress_bar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress label
        ttk.Label(progress_bar_frame, text="Progress:", style='Body.TLabel').pack(anchor=tk.W)
        
        # Progress bar with percentage
        bar_container = tk.Frame(progress_bar_frame, bg=self.style_manager.get_color('bg_card'))
        bar_container.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(bar_container,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=400,
                                          style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Percentage display
        percentage_label = ttk.Label(bar_container, textvariable=self.progress_text_var, 
                                   style='Success.TLabel',
                                   font=self.style_manager.get_font('button'))
        percentage_label.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Phase indicator
        phase_frame = tk.Frame(progress_content, bg=self.style_manager.get_color('bg_card'))
        phase_frame.pack(fill=tk.X)
        
        ttk.Label(phase_frame, text="Current Phase:", style='Small.TLabel').pack(side=tk.LEFT)
        phase_label = ttk.Label(phase_frame, textvariable=self.stats_vars['current_phase'], style='Body.TLabel')
        phase_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_statistics_section(self):
        """Create statistics display section"""
        
        # Statistics container
        stats_container = ttk.LabelFrame(self.frame, text="📈 Statistics", style='Card.TLabelframe')
        stats_container.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Statistics grid
        stats_content = tk.Frame(stats_container, bg=self.style_manager.get_color('bg_card'))
        stats_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Configure grid
        for i in range(4):
            stats_content.columnconfigure(i, weight=1)
        
        # Statistics items
        stats_items = [
            ('pages_scraped', 'Pages Scraped', '📄', 0, 0),
            ('properties_found', 'Properties Found', '🏠', 0, 1),
            ('properties_saved', 'Properties Saved', '💾', 0, 2),
            ('duration', 'Duration', '⏱️', 0, 3),
            ('speed', 'Speed', '⚡', 1, 0),
            ('estimated_remaining', 'Time Remaining', '⏳', 1, 1),
            ('success_rate', 'Success Rate', '✅', 1, 2),
            ('current_phase', 'Phase', '🔄', 1, 3)
        ]
        
        self.stat_labels = {}
        
        for key, label, icon, row, col in stats_items:
            # Stat card
            stat_card = tk.Frame(stats_content, 
                               bg=self.style_manager.get_color('bg_main'),
                               relief='flat',
                               bd=1)
            stat_card.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # Icon and label
            header_frame = tk.Frame(stat_card, bg=self.style_manager.get_color('bg_main'))
            header_frame.pack(fill=tk.X, padx=10, pady=(8, 2))
            
            ttk.Label(header_frame, text=f"{icon} {label}", style='Small.TLabel').pack()
            
            # Value
            value_frame = tk.Frame(stat_card, bg=self.style_manager.get_color('bg_main'))
            value_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
            
            value_label = ttk.Label(value_frame, textvariable=self.stats_vars[key], 
                                  style='Title.TLabel')
            value_label.pack()
            
            self.stat_labels[key] = value_label
    
    def create_log_section(self):
        """Create log display section"""
        
        # Log container
        log_container = ttk.LabelFrame(self.frame, text="📋 Activity Log", style='Card.TLabelframe')
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Log content
        log_content = tk.Frame(log_container, bg=self.style_manager.get_color('bg_card'))
        log_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        log_content.columnconfigure(0, weight=1)
        log_content.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_content,
                                                 font=self.style_manager.get_font('code'),
                                                 bg=self.style_manager.get_color('bg_main'),
                                                 fg=self.style_manager.get_color('text_primary'),
                                                 relief='flat',
                                                 wrap=tk.WORD,
                                                 height=12)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls
        log_controls = tk.Frame(log_content, bg=self.style_manager.get_color('bg_card'))
        log_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Clear log button
        clear_button = ttk.Button(log_controls,
                                text="🗑️ Clear Log",
                                style='Secondary.TButton',
                                command=self.clear_log)
        clear_button.pack(side=tk.LEFT)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(log_controls,
                                         text="Auto-scroll",
                                         variable=self.auto_scroll_var,
                                         bg=self.style_manager.get_color('bg_card'),
                                         fg=self.style_manager.get_color('text_secondary'),
                                         font=self.style_manager.get_font('small'),
                                         activebackground=self.style_manager.get_color('bg_card'))
        auto_scroll_check.pack(side=tk.RIGHT)
        
        # Add initial welcome message
        self.log_message("🎉 MagicBricks Scraper ready! Configure settings and click 'Start Scraping' to begin.", "INFO")
    
    def update_progress(self, percentage: float):
        """Update progress bar"""
        self.progress_var.set(min(max(percentage, 0), 100))
        self.progress_text_var.set(f"{percentage:.1f}%")
    
    def update_status(self, status: str):
        """Update status text"""
        self.status_var.set(status)
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display"""
        
        for key, value in stats.items():
            if key in self.stats_vars:
                self.stats_vars[key].set(str(value))
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message with color coding
        level_colors = {
            "INFO": "blue",
            "SUCCESS": "green", 
            "WARNING": "orange",
            "ERROR": "red",
            "DEBUG": "gray"
        }
        
        color = level_colors.get(level, "black")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Insert message
        self.log_text.insert(tk.END, formatted_message)
        
        # Color the level part
        start_line = self.log_text.index(tk.END + "-2l")
        level_start = f"{start_line.split('.')[0]}.{len(f'[{timestamp}] ')}"
        level_end = f"{start_line.split('.')[0]}.{len(f'[{timestamp}] {level}')}"
        
        # Configure tags for colors
        if not hasattr(self, '_tags_configured'):
            for tag_level, tag_color in level_colors.items():
                self.log_text.tag_configure(tag_level.lower(), foreground=tag_color)
            self._tags_configured = True
        
        self.log_text.tag_add(level.lower(), level_start, level_end)
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        # Limit log size (keep last 1000 lines)
        lines = self.log_text.get("1.0", tk.END).count('\n')
        if lines > 1000:
            self.log_text.delete("1.0", "100.0")
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete("1.0", tk.END)
        self.log_message("Log cleared", "INFO")
    
    def reset_progress(self):
        """Reset progress to initial state"""
        self.update_progress(0)
        self.update_status("Ready to start scraping")
        
        # Reset statistics
        reset_stats = {
            'pages_scraped': '0',
            'properties_found': '0', 
            'properties_saved': '0',
            'duration': '0:00',
            'speed': '0 props/min',
            'estimated_remaining': '--',
            'success_rate': '100%',
            'current_phase': 'Ready'
        }
        
        self.update_statistics(reset_stats)
    
    def set_scraping_state(self, is_scraping: bool):
        """Update UI for scraping state"""
        
        if is_scraping:
            self.update_status("Scraping in progress...")
            self.log_message("🚀 Scraping started", "SUCCESS")
        else:
            self.update_status("Scraping stopped")
            self.log_message("⏹️ Scraping stopped", "WARNING")
    
    def show_completion(self, stats: Dict[str, Any]):
        """Show scraping completion"""
        
        self.update_progress(100)
        self.update_status("Scraping completed successfully!")
        
        # Log completion summary
        pages = stats.get('pages_scraped', 0)
        properties = stats.get('properties_saved', 0)
        duration = stats.get('duration', '0:00')
        
        self.log_message(f"🎉 Scraping completed! Pages: {pages}, Properties: {properties}, Duration: {duration}", "SUCCESS")
    
    def show_error(self, error_message: str):
        """Show error state"""
        
        self.update_status("Error occurred during scraping")
        self.log_message(f"❌ Error: {error_message}", "ERROR")
