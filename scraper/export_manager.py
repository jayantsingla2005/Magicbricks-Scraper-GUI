#!/usr/bin/env python3
"""
Export Manager Module
Handles data export in multiple formats (CSV, JSON, Excel).
Extracted from integrated_magicbricks_scraper.py for better maintainability.
"""

import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any


class ExportManager:
    """
    Manages data export in multiple formats with comprehensive metadata
    """
    
    def __init__(self, logger=None):
        """
        Initialize export manager
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def save_to_csv(self, properties: List[Dict[str, Any]], session_stats: Dict[str, Any], 
                    filename: str = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Save scraped properties to CSV
        
        Args:
            properties: List of property dictionaries
            session_stats: Session statistics dictionary
            filename: Output filename (optional)
            
        Returns:
            tuple: (DataFrame, filename) or (None, None) if failed
        """
        
        if not properties:
            print("[WARNING] No properties to save")
            return None, None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(properties)
            df.to_csv(filename, index=False)
            
            print(f"[SAVE] Saved {len(properties)} properties to {filename}")
            return df, filename
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            return None, None
    
    def save_to_json(self, properties: List[Dict[str, Any]], session_stats: Dict[str, Any],
                     filename: str = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Save scraped properties to JSON with comprehensive metadata
        
        Args:
            properties: List of property dictionaries
            session_stats: Session statistics dictionary
            filename: Output filename (optional)
            
        Returns:
            tuple: (data, filename) or (None, None) if failed
        """
        
        if not properties:
            print("⚠️ No properties to save")
            return None, None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.json"
        
        try:
            # Create comprehensive JSON structure
            json_data = {
                'metadata': {
                    'scrape_timestamp': datetime.now().isoformat(),
                    'total_properties': len(properties),
                    'session_stats': session_stats,
                    'scraper_version': '2.0',
                    'export_format': 'json'
                },
                'properties': properties
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[SAVE] Saved {len(properties)} properties to {filename}")
            return json_data, filename
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return None, None
    
    def save_to_excel(self, properties: List[Dict[str, Any]], session_stats: Dict[str, Any],
                      filename: str = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Save scraped properties to Excel with multiple sheets
        
        Args:
            properties: List of property dictionaries
            session_stats: Session statistics dictionary
            filename: Output filename (optional)
            
        Returns:
            tuple: (DataFrame, filename) or (None, None) if failed
        """
        
        if not properties:
            print("⚠️ No properties to save")
            return None, None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.xlsx"
        
        try:
            df = pd.DataFrame(properties)
            
            # Create Excel writer with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main properties sheet
                df.to_excel(writer, sheet_name='Properties', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Properties',
                        'Scrape Date',
                        'Mode',
                        'Pages Scraped',
                        'Duration',
                        'Success Rate'
                    ],
                    'Value': [
                        len(properties),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        session_stats.get('mode', 'unknown'),
                        session_stats.get('pages_scraped', 0),
                        session_stats.get('duration_formatted', 'N/A'),
                        f"{session_stats.get('success_rate', 0):.1f}%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # City breakdown if available
                if 'city_stats' in session_stats:
                    city_df = pd.DataFrame(session_stats['city_stats'])
                    city_df.to_excel(writer, sheet_name='City_Stats', index=False)
            
            print(f"[SAVE] Saved {len(properties)} properties to {filename}")
            return df, filename
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {str(e)}")
            return None, None
    
    def export_data(self, properties: List[Dict[str, Any]], session_stats: Dict[str, Any],
                    formats: List[str] = ['csv'], base_filename: str = None) -> Dict[str, str]:
        """
        Export data in multiple formats
        
        Args:
            properties: List of property dictionaries
            session_stats: Session statistics dictionary
            formats: List of formats to export ('csv', 'json', 'excel')
            base_filename: Base filename without extension
            
        Returns:
            Dict mapping format to filename
        """
        
        if not properties:
            print("⚠️ No properties to export")
            return {}
        
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = session_stats.get('mode', 'unknown')
            base_filename = f"magicbricks_{mode}_scrape_{timestamp}"
        
        exported_files = {}
        
        for format_type in formats:
            try:
                if format_type.lower() == 'csv':
                    filename = f"{base_filename}.csv"
                    _, saved_filename = self.save_to_csv(properties, session_stats, filename)
                    if saved_filename:
                        exported_files['csv'] = saved_filename
                
                elif format_type.lower() == 'json':
                    filename = f"{base_filename}.json"
                    _, saved_filename = self.save_to_json(properties, session_stats, filename)
                    if saved_filename:
                        exported_files['json'] = saved_filename
                
                elif format_type.lower() == 'excel':
                    filename = f"{base_filename}.xlsx"
                    _, saved_filename = self.save_to_excel(properties, session_stats, filename)
                    if saved_filename:
                        exported_files['excel'] = saved_filename
                
                else:
                    print(f"⚠️ Unsupported format: {format_type}")
                    
            except Exception as e:
                self.logger.error(f"Error exporting {format_type}: {str(e)}")
        
        return exported_files
    
    def create_export_summary(self, exported_files: Dict[str, str], properties_count: int) -> str:
        """
        Create a summary of exported files
        
        Args:
            exported_files: Dictionary mapping format to filename
            properties_count: Number of properties exported
            
        Returns:
            Summary string
        """
        if not exported_files:
            return "No files exported"
        
        summary_lines = [
            f"\n{'='*60}",
            f"EXPORT SUMMARY",
            f"{'='*60}",
            f"Properties Exported: {properties_count}",
            f"Formats: {len(exported_files)}",
            ""
        ]
        
        for format_type, filename in exported_files.items():
            summary_lines.append(f"  [{format_type.upper()}] {filename}")
        
        summary_lines.append(f"{'='*60}\n")
        
        return "\n".join(summary_lines)

