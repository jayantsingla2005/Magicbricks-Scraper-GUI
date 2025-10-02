#!/usr/bin/env python3
"""
URL Normalization Module
Provides URL processing utilities for the URL tracking system.
Handles URL normalization, hashing, and property ID extraction.
"""

import hashlib
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


class URLNormalizer:
    """
    URL normalization and processing utilities
    """
    
    def __init__(self, enable_normalization: bool = True):
        """
        Initialize URL normalizer
        
        Args:
            enable_normalization: Whether to enable URL normalization
        """
        self.enable_normalization = enable_normalization
        
        # Common tracking parameters to remove during normalization
        self.tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 
            'ref', 'source', 'fbclid', 'gclid'
        ]
        
        # MagicBricks URL patterns for property ID extraction
        self.property_id_patterns = [
            r'/propertydetail/([^/]+)',
            r'/property-([^/]+)',
            r'propid=([^&]+)',
            r'/([^/]+)\.html'
        ]
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent tracking
        
        Normalization steps:
        1. Parse URL components
        2. Remove tracking parameters
        3. Convert to lowercase
        4. Strip whitespace
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL string
        """
        try:
            if not self.enable_normalization:
                return url
            
            # Parse URL
            parsed = urlparse(url)
            
            # Parse query parameters
            query_params = parse_qs(parsed.query)
            
            # Filter out tracking parameters
            filtered_params = {
                k: v for k, v in query_params.items() 
                if k not in self.tracking_params
            }
            
            # Rebuild query string
            if filtered_params:
                query_string = '&'.join([
                    f"{k}={v[0]}" for k, v in filtered_params.items()
                ])
                normalized_url = (
                    f"{parsed.scheme}://{parsed.netloc}"
                    f"{parsed.path}?{query_string}"
                )
            else:
                normalized_url = (
                    f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                )
            
            return normalized_url.lower().strip()
            
        except Exception as e:
            print(f"[WARNING] Error normalizing URL {url}: {str(e)}")
            return url.lower().strip()
    
    def generate_url_hash(self, url: str) -> str:
        """
        Generate MD5 hash for URL for efficient storage and lookup
        
        Args:
            url: URL to hash
            
        Returns:
            MD5 hash string
        """
        normalized_url = self.normalize_url(url)
        return hashlib.md5(normalized_url.encode()).hexdigest()
    
    def extract_property_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract property ID from MagicBricks URL if possible
        
        Tries multiple URL patterns to extract property ID:
        - /propertydetail/[ID]
        - /property-[ID]
        - propid=[ID]
        - /[ID].html
        
        Args:
            url: MagicBricks property URL
            
        Returns:
            Property ID string if found, None otherwise
        """
        try:
            for pattern in self.property_id_patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            print(f"[WARNING] Error extracting property ID from {url}: {str(e)}")
            return None
    
    def validate_url_format(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    def is_magicbricks_url(self, url: str) -> bool:
        """
        Check if URL is a MagicBricks URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from magicbricks.com, False otherwise
        """
        try:
            parsed = urlparse(url)
            return 'magicbricks.com' in parsed.netloc.lower()
        except Exception:
            return False


def normalize_url(url: str, enable_normalization: bool = True) -> str:
    """
    Standalone function for URL normalization
    
    Args:
        url: URL to normalize
        enable_normalization: Whether to enable normalization
        
    Returns:
        Normalized URL string
    """
    normalizer = URLNormalizer(enable_normalization)
    return normalizer.normalize_url(url)


def generate_url_hash(url: str) -> str:
    """
    Standalone function for URL hash generation
    
    Args:
        url: URL to hash
        
    Returns:
        MD5 hash string
    """
    normalizer = URLNormalizer()
    return normalizer.generate_url_hash(url)


def extract_property_id(url: str) -> Optional[str]:
    """
    Standalone function for property ID extraction
    
    Args:
        url: MagicBricks property URL
        
    Returns:
        Property ID string if found, None otherwise
    """
    normalizer = URLNormalizer()
    return normalizer.extract_property_id_from_url(url)

