"""
GIS Text and Identification Parsing Utilities
Portfolio / Open-Source Edition

This module provides string formatting tools to clean text parameters and auto-extract 
contract identification indices from local geospatial asset filenames.

:author: Lucas Polo
:date: 2026-07-09
:version: 1.0.0
"""

import re

def clean_agency_string(raw_agency: str) -> str:
    """
    Normalizes whitespace and converts the agency identifier string to uppercase.
    
    :param raw_agency: Raw input agency string
    :return: Sanitized uppercase agency string
    """
    if not raw_agency:
        return ""
    return re.sub(r'\s+', ' ', raw_agency).strip().upper()

def guess_project_id_from_name(filename: str) -> str:
    """
    Attempts to parse a standard project ID prefix from a given filename string.
    
    :param filename: Base filename string (e.g., '11504.01_Project_Limits.kml')
    :return: Extracted project ID string or empty string if unverified
    """
    if not filename:
        return ""
        
    id_guess = filename.split()[0].split('_')[0].replace('.kml', '').replace('.kmz', '')
    if id_guess.split('.')[0].isdigit():
        return id_guess
    return ""
