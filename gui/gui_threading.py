#!/usr/bin/env python3
"""
GUI Threading Module
Handles all threading operations, message queue, and thread-safe GUI updates.
Extracted from magicbricks_gui.py for better maintainability.
"""

import threading
import queue
from typing import Callable, Dict, Any, Optional
from datetime import datetime


class GUIThreadManager:
    """
    Manages threading operations for GUI scraping
    Handles message queue for thread-safe GUI updates
    """
    
    def __init__(self, gui_callbacks: Dict[str, Callable]):
        """
        Initialize thread manager
        
        Args:
            gui_callbacks: Dictionary of callback functions for GUI updates
                - 'log': Callback for log messages
                - 'stats': Callback for statistics updates
                - 'progress': Callback for progress updates
                - 'status': Callback for status updates
                - 'error': Callback for error handling
        """
        self.gui_callbacks = gui_callbacks
        
        # Threading state
        self.scraping_thread = None
        self.is_scraping = False
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Progress tracking
        self.scraping_start_time = None
        self.progress_history = []
    
    def start_scraping_thread(self, scraping_function: Callable, *args, **kwargs):
        """
        Start scraping in a separate thread
        
        Args:
            scraping_function: Function to run in thread
            *args: Positional arguments for scraping function
            **kwargs: Keyword arguments for scraping function
        """
        if self.is_scraping:
            raise RuntimeError("Scraping is already in progress")
        
        # Update state
        self.is_scraping = True
        self.scraping_start_time = datetime.now()
        self.progress_history = []
        
        # Create and start thread
        self.scraping_thread = threading.Thread(
            target=self._thread_wrapper,
            args=(scraping_function, args, kwargs),
            daemon=True
        )
        self.scraping_thread.start()
    
    def _thread_wrapper(self, scraping_function: Callable, args: tuple, kwargs: dict):
        """
        Wrapper for scraping function to handle errors
        
        Args:
            scraping_function: Function to run
            args: Positional arguments
            kwargs: Keyword arguments
        """
        try:
            scraping_function(*args, **kwargs)
        except Exception as e:
            # Send error to GUI
            self.message_queue.put(('error', {
                'exception': e,
                'message': f"Scraping thread error: {str(e)}"
            }))
        finally:
            # Always reset state when thread completes
            self.is_scraping = False
    
    def stop_scraping(self):
        """
        Stop the scraping process
        Note: This sets the flag but doesn't forcefully kill the thread
        """
        if not self.is_scraping:
            return False
        
        self.is_scraping = False
        self.send_log_message("Stopping scraping...", 'WARNING')
        self.send_status_update("Stopping scraping...")
        
        return True
    
    def send_log_message(self, message: str, level: str = 'INFO'):
        """
        Send log message to GUI (thread-safe)
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        self.message_queue.put(('log', formatted_message))
    
    def send_statistics_update(self, stats: Dict[str, Any]):
        """
        Send statistics update to GUI (thread-safe)
        
        Args:
            stats: Statistics dictionary
        """
        self.message_queue.put(('stats', stats))
    
    def send_progress_update(self, progress: float):
        """
        Send progress update to GUI (thread-safe)
        
        Args:
            progress: Progress percentage (0-100)
        """
        self.message_queue.put(('progress', progress))
    
    def send_status_update(self, status: str):
        """
        Send status update to GUI (thread-safe)
        
        Args:
            status: Status message
        """
        self.message_queue.put(('status', status))
    
    def send_error(self, error_info: Any):
        """
        Send error to GUI (thread-safe)
        
        Args:
            error_info: Error information
        """
        self.message_queue.put(('error', error_info))
    
    def process_messages(self):
        """
        Process messages from the queue (thread-safe GUI updates)
        Should be called periodically from GUI main thread
        """
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                # Route message to appropriate callback
                if message_type == 'log' and 'log' in self.gui_callbacks:
                    self.gui_callbacks['log'](data)
                
                elif message_type == 'stats' and 'stats' in self.gui_callbacks:
                    self.gui_callbacks['stats'](data)
                
                elif message_type == 'progress' and 'progress' in self.gui_callbacks:
                    self.gui_callbacks['progress'](data)
                
                elif message_type == 'status' and 'status' in self.gui_callbacks:
                    self.gui_callbacks['status'](data)
                
                elif message_type == 'error' and 'error' in self.gui_callbacks:
                    self.gui_callbacks['error'](data)
                
        except queue.Empty:
            pass
    
    def create_progress_callback(self, config: Dict[str, Any]) -> Callable:
        """
        Create a progress callback function for scraper
        
        Args:
            config: Configuration dictionary with mode and other settings
            
        Returns:
            Progress callback function
        """
        def progress_callback(progress_data: Dict[str, Any]):
            """Callback function to update GUI with scraping progress"""
            try:
                # Calculate progress percentage
                current_page = progress_data.get('current_page', 0)
                total_pages = progress_data.get('total_pages', 1)
                progress_percentage = min((current_page / total_pages) * 100, 100)
                
                # Update statistics with proper calculations
                phase = progress_data.get('phase', 'listing_extraction')
                phase_display = {
                    'listing_extraction': 'Extracting Listings',
                    'individual_scraping': 'Scraping Properties',
                    'processing': 'Processing Data'
                }.get(phase, 'Processing')

                stats = {
                    'session_id': progress_data.get('session_id', 'N/A'),
                    'mode': config.get('mode', 'unknown'),
                    'current_phase': phase_display,
                    'pages_scraped': current_page,
                    'properties_found': progress_data.get('properties_found', 0),
                    'properties_saved': progress_data.get('properties_found', 0),
                    'status': f"Scraping page {current_page}/{total_pages}"
                }

                # Send updates to GUI
                self.send_statistics_update(stats)
                self.send_progress_update(progress_percentage)

                # Update status with phase information
                if phase == 'listing_extraction':
                    status_msg = f"Extracting listings - Page {current_page}/{total_pages}"
                elif phase == 'individual_scraping':
                    status_msg = f"Scraping individual properties - {current_page}/{total_pages}"
                else:
                    status_msg = f"Processing - {current_page}/{total_pages}"

                self.send_status_update(status_msg)
                
            except Exception as e:
                self.send_log_message(f"Progress callback error: {str(e)}", 'ERROR')
        
        return progress_callback
    
    def is_thread_alive(self) -> bool:
        """
        Check if scraping thread is still alive
        
        Returns:
            True if thread is alive, False otherwise
        """
        if self.scraping_thread is None:
            return False
        return self.scraping_thread.is_alive()
    
    def get_scraping_duration(self) -> Optional[float]:
        """
        Get duration of current scraping session in seconds
        
        Returns:
            Duration in seconds or None if not scraping
        """
        if self.scraping_start_time is None:
            return None
        
        duration = (datetime.now() - self.scraping_start_time).total_seconds()
        return duration
    
    def get_scraping_duration_formatted(self) -> str:
        """
        Get formatted duration of current scraping session
        
        Returns:
            Formatted duration string (e.g., "5m 30s")
        """
        duration = self.get_scraping_duration()
        if duration is None:
            return "N/A"
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def add_progress_history(self, progress: float):
        """
        Add progress point to history
        
        Args:
            progress: Progress percentage
        """
        self.progress_history.append({
            'timestamp': datetime.now(),
            'progress': progress
        })
        
        # Keep only last 20 entries
        if len(self.progress_history) > 20:
            self.progress_history = self.progress_history[-20:]
    
    def get_progress_history(self) -> list:
        """
        Get progress history
        
        Returns:
            List of progress history entries
        """
        return self.progress_history.copy()
    
    def reset_state(self):
        """Reset threading state"""
        self.is_scraping = False
        self.scraping_thread = None
        self.scraping_start_time = None
        self.progress_history = []
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except queue.Empty:
                break

