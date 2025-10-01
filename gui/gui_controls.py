#!/usr/bin/env python3
"""
GUI Controls Module
Handles all input controls, buttons, checkboxes, and user input elements.
Extracted from magicbricks_gui.py for better maintainability.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, Any, Callable, Optional
from pathlib import Path


class GUIControls:
    """
    Manages all GUI input controls and user interaction elements
    """
    
    def __init__(self, parent, config: Dict[str, Any], styles):
        """
        Initialize GUI controls
        
        Args:
            parent: Parent widget
            config: Configuration dictionary
            styles: GUIStyles instance for styling
        """
        self.parent = parent
        self.config = config
        self.styles = styles
        
        # Control variables
        self.control_vars = {}
        
        # Widget references
        self.widgets = {}
    
    def create_basic_controls(self, parent_frame) -> Dict[str, tk.Variable]:
        """
        Create basic scraping controls (city, mode, max pages)
        
        Args:
            parent_frame: Parent frame for controls
            
        Returns:
            Dictionary of control variables
        """
        vars_dict = {}
        
        # City selection
        ttk.Label(parent_frame, text="City:", style='Heading.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        city_var = tk.StringVar(value=self.config.get('city', 'gurgaon'))
        city_combo = ttk.Combobox(
            parent_frame, 
            textvariable=city_var,
            values=['gurgaon', 'delhi', 'noida', 'mumbai', 'bangalore'],
            width=25,
            state='readonly',
            style='Modern.TCombobox'
        )
        city_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 15))
        vars_dict['city'] = city_var
        self.widgets['city_combo'] = city_combo
        
        # Scraping mode
        ttk.Label(parent_frame, text="Mode:", style='Heading.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        mode_var = tk.StringVar(value=self.config.get('mode', 'incremental'))
        mode_combo = ttk.Combobox(
            parent_frame,
            textvariable=mode_var,
            values=['incremental', 'full', 'conservative'],
            width=25,
            state='readonly',
            style='Modern.TCombobox'
        )
        mode_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 15))
        vars_dict['mode'] = mode_var
        self.widgets['mode_combo'] = mode_combo
        
        # Max pages
        ttk.Label(parent_frame, text="Max Pages:", style='Heading.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        max_pages_var = tk.StringVar(value=str(self.config.get('max_pages', 5)))
        max_pages_entry = ttk.Entry(
            parent_frame,
            textvariable=max_pages_var,
            width=15,
            style='Modern.TEntry'
        )
        max_pages_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 15))
        vars_dict['max_pages'] = max_pages_var
        self.widgets['max_pages_entry'] = max_pages_entry
        
        return vars_dict
    
    def create_output_controls(self, parent_frame, browse_callback: Optional[Callable] = None) -> Dict[str, tk.Variable]:
        """
        Create output directory controls
        
        Args:
            parent_frame: Parent frame for controls
            browse_callback: Callback for browse button
            
        Returns:
            Dictionary of control variables
        """
        vars_dict = {}
        
        ttk.Label(parent_frame, text="Output Directory:", style='Heading.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        output_frame = ttk.Frame(parent_frame)
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(0, weight=1)
        
        output_dir_var = tk.StringVar(value=self.config.get('output_directory', '.'))
        output_entry = ttk.Entry(
            output_frame,
            textvariable=output_dir_var,
            style='Modern.TEntry'
        )
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        vars_dict['output_directory'] = output_dir_var
        self.widgets['output_entry'] = output_entry
        
        if browse_callback:
            browse_btn = ttk.Button(
                output_frame,
                text="📁 Browse",
                command=browse_callback,
                style='Secondary.TButton'
            )
            browse_btn.grid(row=0, column=1)
            self.widgets['browse_btn'] = browse_btn
        
        return vars_dict
    
    def create_checkbox_controls(self, parent_frame) -> Dict[str, tk.BooleanVar]:
        """
        Create checkbox controls (headless, incremental, individual pages)
        
        Args:
            parent_frame: Parent frame for controls
            
        Returns:
            Dictionary of boolean variables
        """
        vars_dict = {}
        
        # Headless mode
        headless_var = tk.BooleanVar(value=self.config.get('headless', True))
        headless_check = ttk.Checkbutton(
            parent_frame,
            text="🚀 Headless Mode (faster)",
            variable=headless_var
        )
        headless_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        vars_dict['headless'] = headless_var
        self.widgets['headless_check'] = headless_check
        
        # Incremental scraping
        incremental_var = tk.BooleanVar(value=self.config.get('incremental_enabled', True))
        incremental_check = ttk.Checkbutton(
            parent_frame,
            text="⚡ Incremental Scraping (60-75% faster)",
            variable=incremental_var
        )
        incremental_check.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        vars_dict['incremental'] = incremental_var
        self.widgets['incremental_check'] = incremental_check
        
        # Individual pages
        individual_var = tk.BooleanVar(value=self.config.get('individual_pages', False))
        individual_check = ttk.Checkbutton(
            parent_frame,
            text="📄 Individual Property Details (⚠️ 10x slower)",
            variable=individual_var
        )
        individual_check.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        vars_dict['individual_pages'] = individual_var
        self.widgets['individual_check'] = individual_check
        
        return vars_dict
    
    def create_export_controls(self, parent_frame) -> Dict[str, tk.BooleanVar]:
        """
        Create export format controls
        
        Args:
            parent_frame: Parent frame for controls
            
        Returns:
            Dictionary of boolean variables
        """
        vars_dict = {}
        
        # Mandatory formats label
        ttk.Label(
            parent_frame,
            text="✅ Mandatory: CSV + Database",
            style='Success.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Optional formats label
        ttk.Label(
            parent_frame,
            text="Optional Formats:",
            style='Heading.TLabel'
        ).grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        
        # JSON export
        json_var = tk.BooleanVar(value=self.config.get('export_json', False))
        json_check = ttk.Checkbutton(
            parent_frame,
            text="📋 JSON (structured data)",
            variable=json_var
        )
        json_check.grid(row=2, column=0, sticky=tk.W, pady=(2, 5))
        vars_dict['export_json'] = json_var
        self.widgets['json_check'] = json_check
        
        # Excel export
        excel_var = tk.BooleanVar(value=self.config.get('export_excel', False))
        excel_check = ttk.Checkbutton(
            parent_frame,
            text="📊 Excel (multi-sheet with summary)",
            variable=excel_var
        )
        excel_check.grid(row=3, column=0, sticky=tk.W, pady=(2, 0))
        vars_dict['export_excel'] = excel_var
        self.widgets['excel_check'] = excel_check
        
        return vars_dict
    
    def create_timing_controls(self, parent_frame) -> Dict[str, tk.StringVar]:
        """
        Create timing/delay controls
        
        Args:
            parent_frame: Parent frame for controls
            
        Returns:
            Dictionary of string variables
        """
        vars_dict = {}
        
        # Page delay min
        ttk.Label(parent_frame, text="Page Delay Min (s):", style='Info.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        page_delay_min_var = tk.StringVar(value="2")
        ttk.Entry(parent_frame, textvariable=page_delay_min_var, width=10).grid(
            row=0, column=1, sticky=tk.W, pady=(0, 10)
        )
        vars_dict['page_delay_min'] = page_delay_min_var
        
        # Page delay max
        ttk.Label(parent_frame, text="Page Delay Max (s):", style='Info.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=(0, 10)
        )
        page_delay_max_var = tk.StringVar(value="5")
        ttk.Entry(parent_frame, textvariable=page_delay_max_var, width=10).grid(
            row=1, column=1, sticky=tk.W, pady=(0, 10)
        )
        vars_dict['page_delay_max'] = page_delay_max_var
        
        # Individual delay min
        ttk.Label(parent_frame, text="Individual Delay Min (s):", style='Info.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(0, 10)
        )
        individual_delay_min_var = tk.StringVar(value="3")
        ttk.Entry(parent_frame, textvariable=individual_delay_min_var, width=10).grid(
            row=2, column=1, sticky=tk.W, pady=(0, 10)
        )
        vars_dict['individual_delay_min'] = individual_delay_min_var
        
        # Individual delay max
        ttk.Label(parent_frame, text="Individual Delay Max (s):", style='Info.TLabel').grid(
            row=3, column=0, sticky=tk.W, pady=(0, 10)
        )
        individual_delay_max_var = tk.StringVar(value="7")
        ttk.Entry(parent_frame, textvariable=individual_delay_max_var, width=10).grid(
            row=3, column=1, sticky=tk.W, pady=(0, 10)
        )
        vars_dict['individual_delay_max'] = individual_delay_max_var
        
        return vars_dict
    
    def create_action_buttons(self, parent_frame, start_callback: Callable, stop_callback: Callable) -> Dict[str, ttk.Button]:
        """
        Create action buttons (Start, Stop, Export)
        
        Args:
            parent_frame: Parent frame for buttons
            start_callback: Callback for start button
            stop_callback: Callback for stop button
            
        Returns:
            Dictionary of button widgets
        """
        buttons = {}
        
        # Start button
        start_btn = ttk.Button(
            parent_frame,
            text="▶️ Start Scraping",
            command=start_callback,
            style='Primary.TButton'
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 15))
        buttons['start'] = start_btn
        self.widgets['start_btn'] = start_btn
        
        # Stop button
        stop_btn = ttk.Button(
            parent_frame,
            text="⏹️ Stop",
            command=stop_callback,
            style='Danger.TButton',
            state='disabled'
        )
        stop_btn.pack(side=tk.LEFT)
        buttons['stop'] = stop_btn
        self.widgets['stop_btn'] = stop_btn
        
        return buttons
    
    def get_all_values(self) -> Dict[str, Any]:
        """
        Get all control values
        
        Returns:
            Dictionary of all control values
        """
        values = {}
        for key, var in self.control_vars.items():
            if isinstance(var, tk.BooleanVar):
                values[key] = var.get()
            elif isinstance(var, (tk.StringVar, tk.IntVar, tk.DoubleVar)):
                values[key] = var.get()
        return values
    
    def set_state(self, state: str):
        """
        Set state of all controls
        
        Args:
            state: 'normal' or 'disabled'
        """
        for widget in self.widgets.values():
            if hasattr(widget, 'config'):
                try:
                    widget.config(state=state)
                except:
                    pass

