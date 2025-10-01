#!/usr/bin/env python3
"""
GUI Monitoring Module
Handles progress bars, statistics display, and real-time monitoring.
Extracted from magicbricks_gui.py for better maintainability.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, Optional
from datetime import datetime


class GUIMonitoring:
    """
    Manages progress monitoring, statistics display, and logging
    """
    
    def __init__(self, parent, styles):
        """
        Initialize monitoring components
        
        Args:
            parent: Parent widget
            styles: GUIStyles instance for styling
        """
        self.parent = parent
        self.styles = styles
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.progress_text_var = tk.StringVar(value="0%")
        self.progress_bar = None
        
        # Statistics labels
        self.stats_labels = {}
        
        # Log text widget
        self.log_text = None
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
    
    def create_progress_section(self, parent_frame) -> ttk.Progressbar:
        """
        Create progress bar section
        
        Args:
            parent_frame: Parent frame for progress section
            
        Returns:
            Progress bar widget
        """
        # Progress label
        ttk.Label(
            parent_frame,
            text="⚡ Progress:",
            style='Heading.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            parent_frame,
            variable=self.progress_var,
            maximum=100,
            length=350,
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(15, 0), pady=(0, 8))
        
        # Progress percentage label
        progress_label = ttk.Label(
            parent_frame,
            textvariable=self.progress_text_var,
            style='Success.TLabel',
            font=self.styles.get_font('body_bold')
        )
        progress_label.grid(row=0, column=2, padx=(15, 0))
        
        return self.progress_bar
    
    def create_statistics_section(self, parent_frame) -> Dict[str, ttk.Label]:
        """
        Create statistics display section
        
        Args:
            parent_frame: Parent frame for statistics
            
        Returns:
            Dictionary of statistic label widgets
        """
        # Statistics header
        ttk.Label(
            parent_frame,
            text="📊 Statistics:",
            style='Heading.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Statistics grid
        stats_grid = ttk.Frame(parent_frame)
        stats_grid.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        
        # Define statistics to display
        stats_info = [
            ('session_id', '🆔 Session ID:', 'N/A'),
            ('mode', '⚙️ Mode:', 'N/A'),
            ('current_phase', '📍 Phase:', 'N/A'),
            ('pages_scraped', '📄 Pages:', '0'),
            ('properties_found', '🏠 Properties Found:', '0'),
            ('properties_saved', '💾 Properties Saved:', '0'),
            ('duration', '⏱️ Duration:', '0s'),
            ('status', '📊 Status:', 'Ready')
        ]
        
        # Create statistic cards
        row = 0
        col = 0
        for key, label_text, default_value in stats_info:
            # Create card frame
            stat_frame = ttk.Frame(stats_grid, style='Card.TFrame', relief='solid', borderwidth=1)
            stat_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=8, pady=8)
            
            # Label
            ttk.Label(
                stat_frame,
                text=label_text,
                style='Muted.TLabel'
            ).pack(anchor=tk.W, padx=12, pady=(12, 5))
            
            # Value label
            value_label = ttk.Label(
                stat_frame,
                text=default_value,
                style='Info.TLabel',
                font=self.styles.get_font('body_bold')
            )
            value_label.pack(anchor=tk.W, padx=12, pady=(0, 12))
            self.stats_labels[key] = value_label
            
            # Move to next position
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1
        
        return self.stats_labels
    
    def create_log_section(self, parent_frame) -> scrolledtext.ScrolledText:
        """
        Create log display section
        
        Args:
            parent_frame: Parent frame for log section
            
        Returns:
            ScrolledText widget for logs
        """
        # Log header
        ttk.Label(
            parent_frame,
            text="📝 Activity Log:",
            style='Heading.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            parent_frame,
            height=12,
            wrap=tk.WORD,
            font=self.styles.get_font('monospace'),
            bg='#f8f9fa',
            relief='flat',
            borderwidth=1
        )
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Configure log text tags for colored output
        self.log_text.tag_config('INFO', foreground='#0066cc')
        self.log_text.tag_config('SUCCESS', foreground='#10b981')
        self.log_text.tag_config('WARNING', foreground='#f59e0b')
        self.log_text.tag_config('ERROR', foreground='#ef4444')
        
        return self.log_text
    
    def create_status_bar(self, parent_frame) -> ttk.Label:
        """
        Create status bar
        
        Args:
            parent_frame: Parent frame for status bar
            
        Returns:
            Status label widget
        """
        status_label = ttk.Label(
            parent_frame,
            textvariable=self.status_var,
            style='Info.TLabel',
            relief='sunken',
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        return status_label
    
    def update_progress(self, progress: float):
        """
        Update progress bar
        
        Args:
            progress: Progress percentage (0-100)
        """
        self.progress_var.set(progress)
        self.progress_text_var.set(f"{progress:.1f}%")
    
    def update_statistics(self, stats: Dict[str, Any]):
        """
        Update statistics display
        
        Args:
            stats: Dictionary of statistics to update
        """
        for key, value in stats.items():
            if key in self.stats_labels:
                # Format the value
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                self.stats_labels[key].config(text=formatted_value)
    
    def update_status(self, status: str):
        """
        Update status bar
        
        Args:
            status: Status message
        """
        self.status_var.set(status)
    
    def log_message(self, message: str, level: str = 'INFO'):
        """
        Add message to log
        
        Args:
            message: Log message
            level: Log level (INFO, SUCCESS, WARNING, ERROR)
        """
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {level}: {message}\n"
            
            self.log_text.insert(tk.END, formatted_message, level)
            self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear log text"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
    
    def reset_progress(self):
        """Reset progress bar to 0"""
        self.progress_var.set(0)
        self.progress_text_var.set("0%")
    
    def reset_statistics(self):
        """Reset all statistics to default values"""
        default_stats = {
            'session_id': 'N/A',
            'mode': 'N/A',
            'current_phase': 'N/A',
            'pages_scraped': '0',
            'properties_found': '0',
            'properties_saved': '0',
            'duration': '0s',
            'status': 'Ready'
        }
        self.update_statistics(default_stats)
    
    def get_log_content(self) -> str:
        """
        Get all log content
        
        Returns:
            Log text content
        """
        if self.log_text:
            return self.log_text.get(1.0, tk.END)
        return ""
    
    def save_log_to_file(self, filename: str):
        """
        Save log content to file
        
        Args:
            filename: File path to save log
        """
        content = self.get_log_content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

