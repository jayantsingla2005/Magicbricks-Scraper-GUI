#!/usr/bin/env python3
"""
GUI Results Module
Handles results viewing, data tables, and export functionality.
Extracted from magicbricks_gui.py for better maintainability.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Any, Optional, Callable
import json
from pathlib import Path


class GUIResults:
    """
    Manages results viewing, data display, and export operations
    """
    
    def __init__(self, styles):
        """
        Initialize results manager
        
        Args:
            styles: GUIStyles instance for styling
        """
        self.styles = styles
        self.current_properties = []
    
    def show_results_viewer(self, properties: List[Dict[str, Any]], title_suffix: str = "", parent=None):
        """
        Show results viewer window with data table
        
        Args:
            properties: List of property dictionaries
            title_suffix: Additional text for window title
            parent: Parent window
        """
        if not properties:
            messagebox.showinfo("No Results", "No properties to display")
            return
        
        self.current_properties = properties
        
        # Create results window
        results_window = tk.Toplevel(parent) if parent else tk.Tk()
        results_window.title(f"Results Viewer {title_suffix}")
        results_window.geometry("1200x700")
        
        # Main container
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text=f"📊 Results: {len(properties)} Properties",
            style='Title.TLabel'
        ).pack(side=tk.LEFT)
        
        # Search/filter frame
        filter_frame = ttk.Frame(header_frame)
        filter_frame.pack(side=tk.RIGHT)
        
        ttk.Label(filter_frame, text="🔍 Search:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        columns = list(properties[0].keys())[:8] if properties else ['title', 'price', 'area']
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Populate treeview
        def populate_tree(filtered_properties=None):
            tree.delete(*tree.get_children())
            props_to_show = filtered_properties if filtered_properties is not None else properties
            
            for prop in props_to_show:
                values = [str(prop.get(col, 'N/A'))[:100] for col in columns]
                tree.insert('', tk.END, values=values)
        
        populate_tree()
        
        # Search functionality
        def on_search(*args):
            search_term = search_var.get().lower()
            if not search_term:
                populate_tree()
                return
            
            filtered = [
                prop for prop in properties
                if any(search_term in str(v).lower() for v in prop.values())
            ]
            populate_tree(filtered)
        
        search_var.trace('w', on_search)
        
        # Export buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(pady=(15, 0))
        
        ttk.Button(
            export_frame,
            text="📄 Export CSV",
            command=lambda: self.export_csv(properties),
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            export_frame,
            text="📊 Export Excel",
            command=lambda: self.export_excel(properties),
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            export_frame,
            text="📋 Export JSON",
            command=lambda: self.export_json(properties),
            style='Secondary.TButton'
        ).pack(side=tk.LEFT)
    
    def export_csv(self, properties: List[Dict[str, Any]]):
        """
        Export properties to CSV
        
        Args:
            properties: List of property dictionaries
        """
        try:
            import pandas as pd
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                df = pd.DataFrame(properties)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Exported {len(properties)} properties to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_excel(self, properties: List[Dict[str, Any]]):
        """
        Export properties to Excel
        
        Args:
            properties: List of property dictionaries
        """
        try:
            import pandas as pd
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                df = pd.DataFrame(properties)
                df.to_excel(filename, index=False, sheet_name='Properties')
                messagebox.showinfo("Success", f"Exported {len(properties)} properties to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_json(self, properties: List[Dict[str, Any]]):
        """
        Export properties to JSON
        
        Args:
            properties: List of property dictionaries
        """
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(properties, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Exported {len(properties)} properties to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def create_summary_display(self, parent_frame, properties: List[Dict[str, Any]]) -> ttk.Frame:
        """
        Create summary statistics display
        
        Args:
            parent_frame: Parent frame
            properties: List of property dictionaries
            
        Returns:
            Summary frame
        """
        summary_frame = ttk.Frame(parent_frame, style='Card.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Calculate summary statistics
        total_properties = len(properties)
        
        # Price statistics
        prices = []
        for prop in properties:
            price_str = str(prop.get('price', ''))
            # Try to extract numeric value
            try:
                import re
                numbers = re.findall(r'[\d.]+', price_str)
                if numbers:
                    prices.append(float(numbers[0]))
            except:
                pass
        
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Display summary
        ttk.Label(
            summary_frame,
            text="📈 Summary Statistics",
            style='Heading.TLabel'
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        stats_text = f"""
        Total Properties: {total_properties}
        Average Price: ₹ {avg_price:.2f} Lakh
        Min Price: ₹ {min_price:.2f} Lakh
        Max Price: ₹ {max_price:.2f} Lakh
        """
        
        ttk.Label(
            summary_frame,
            text=stats_text,
            style='Info.TLabel',
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        return summary_frame
    
    def load_csv_file(self, callback: Optional[Callable] = None):
        """
        Load properties from CSV file
        
        Args:
            callback: Optional callback function to call with loaded properties
        """
        try:
            import pandas as pd
            
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                df = pd.DataFrame(pd.read_csv(filename))
                properties = df.to_dict('records')
                
                if callback:
                    callback(properties)
                else:
                    self.show_results_viewer(properties, f"- {Path(filename).name}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")

