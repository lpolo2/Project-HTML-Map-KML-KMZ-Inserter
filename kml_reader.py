"""
KML and KMZ GIS Data Geometry and Metadata Extraction Engine
Portfolio / Open-Source Edition

This module parses geospatial KML and compressed binary KMZ files to extract geometry 
coordination features, tracking boundaries, and descriptive metadata attributes. 
It structures extracted shapes into feature objects, isolates potential agency name strings, 
client tags, timeline years, and project identification keys across filename rules, folder names, 
and text descriptions to assist form automation, and calculates dynamic center coordinates.

:author: Lucas Polo
:date: 2026-07-13
:version: 2.6.0
"""

import xml.etree.ElementTree as ET
import re
import zipfile
import os

def parse_kml_geometries(filepath, filename_guessed_id=None):
    """
    Parses a KML or KMZ file to extract coordinates, features, center points, and metadata tags.
    
    :param filepath: Local file path to the .kml or .kmz file
    :param filename_guessed_id: Optional ID string extracted from the filename
    :return: Tuple containing (features, master_center, guessed_agency, guessed_client, 
             guessed_type, guessed_year, final_id)
    """
    # Standard geospatial markup language XML namespace dictionary
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # Selecting the file stream reading strategy based on file extension
    try:
        if filepath.lower().endswith('.kmz'):
            with zipfile.ZipFile(filepath, 'r') as archive:
                kml_files = [f for f in archive.namelist() if f.lower().endswith('.kml')]
                if not kml_files:
                    print("Error: Could not locate a valid internal .kml document inside the KMZ archive.")
                    return None, None, None, None, None, None, None
                with archive.open(kml_files[0]) as extracted_file:
                    root = ET.fromstring(extracted_file.read())
        else:
            tree = ET.parse(filepath)
            root = tree.getroot()
    except Exception as e:
        print(f"Error: Failed to parse XML structure inside geometry file.\n{str(e)}")
        return None, None, None, None, None, None, None

    features = []
    all_center_points = []
    guessed_agency = None
    guessed_client = None
    guessed_type = None
    guessed_year = None
    xml_project_id = None
    folder_guessed_id = None
    
    # Strategy 1: Scanning internal Folder names for a potential Project ID
    for folder in root.findall('.//kml:Folder', namespace):
        folder_name_node = folder.find('kml:name', namespace)
        if folder_name_node is not None and folder_name_node.text:
            f_text = folder_name_node.text.strip()
            
            # Extracting the first continuous group of numbers or standard decimal indices
            id_match = re.search(r'^\d+(?:\.\d+)?', f_text)
            if id_match:
                folder_guessed_id = id_match.group(0)
                break  # Stopping loop once an ID is found in a top-level folder
    
    # Looping through every standalone geospatial placemark node found in the file
    for placemark in root.findall('.//kml:Placemark', namespace):
        description_node = placemark.find('kml:description', namespace)
        
        # Pulling the description tag text block to scan for background metadata strings
        if description_node is not None and description_node.text:
            desc_text = description_node.text.strip()
            
            # Scanning for agency key name strings if not already extracted
            if guessed_agency is None:
                agency_match = re.search(r'Agency:\s*([^<\n]+)', desc_text, re.IGNORECASE)
                if agency_match:
                    guessed_agency = agency_match.group(1).strip()
            
            # Scanning for client or customer names if not already extracted
            if guessed_client is None:
                client_match = re.search(r'(?:Client|Customer):\s*([^<\n]+)', desc_text, re.IGNORECASE)
                if client_match:
                    guessed_client = client_match.group(1).strip()

            # Scanning for project type or scope fields if not already extracted
            if guessed_type is None:
                type_match = re.search(r'(?:Project\s*Type|Type|Scope):\s*([^<\n]+)', desc_text, re.IGNORECASE)
                if type_match:
                    guessed_type = type_match.group(1).strip()

            # Scanning for project tracking years if not already extracted
            if guessed_year is None:
                year_match = re.search(r'(?:Project\s*Year|Year|Date):\s*(\d{4})', desc_text, re.IGNORECASE)
                if year_match:
                    guessed_year = year_match.group(1).strip()
            
            # Scanning for project identifier indexing variations inside descriptions
            if xml_project_id is None:
                id_match = re.search(r'(?:Project\s*ID|Project\s*No|Project\s*Number|Job\s*No|Job\s*Number):\s*([^<\n]+)', desc_text, re.IGNORECASE)
                if id_match:
                    xml_project_id = id_match.group(1).strip()

        coordinate_node = placemark.find('.//kml:coordinates', namespace)
        
        # Validating and isolating coordinate string blocks from the active node
        if coordinate_node is not None and coordinate_node.text:
            local_points = []
            raw_coordinates = coordinate_node.text.strip().split()
            
            for point in raw_coordinates:
                parts = point.split(',')
                if len(parts) >= 2:
                    longitude = float(parts[0])
                    latitude = float(parts[1])
                    local_points.append([latitude, longitude])
            
            if local_points:
                is_point = placemark.find('.//kml:Point', namespace) is not None
                if is_point:
                    features.append({"name": "TEMP", "type": "point", "center": local_points[0]})
                    all_center_points.append(local_points[0])
                else:
                    features.append({"name": "TEMP", "type": "area", "coords": local_points})
                    all_center_points.append(local_points[0])
                    
    if not features:
        return None, None, guessed_agency, guessed_client, guessed_type, guessed_year, xml_project_id
        
    avg_lat = sum(p[0] for p in all_center_points) / len(all_center_points)
    avg_lon = sum(p[1] for p in all_center_points) / len(all_center_points)
    master_center = [round(avg_lat, 6), round(avg_lon, 6)]
    
    # Resolving final project identity designation using hierarchical fallback checks
    if filename_guessed_id:
        final_id = filename_guessed_id
    elif folder_guessed_id:
        final_id = folder_guessed_id
    else:
        final_id = xml_project_id
    
    # Updating feature name tags retroactively
    if final_id:
        for f in features:
            f["name"] = final_id
            
    return features, master_center, guessed_agency, guessed_client, guessed_type, guessed_year, final_id
