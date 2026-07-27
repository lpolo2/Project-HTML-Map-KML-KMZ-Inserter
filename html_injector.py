"""
GIS Project HTML Map Injection Engine
Portfolio / Open-Source Edition

This module provides data-writing pipelines to safely insert newly compiled 
geospatial database objects directly into a JavaScript projects data array inside
an HTML file, while dynamically updating Leaflet styling rules, legend dictionaries, 
and filter chips.

:author: Lucas Polo
:date: 2026-07-14
:version: 7.0.0
"""

import os
import json
import re

# Static tracking schema mapping agencies to color coding rules
HARDCODED_AGENCY_MAPPING = {
    "DEP": "A",
    "DDC": "B",
    "NYSDOT": "C",
    "MTA": "D",
    "NYCDOT": "E",
    "PANYNJ": "F",
    "NJDOT": "G",
    "NJTRANSIT": "H",
    "GSP": "I",
    "NJTP": "J",
    "EDC": "K",
    "DPR": "L"
}

def generate_static_js_lines_array():
    """Generates the synchronized Leaflet LINES configuration block using fixed high-contrast palette rules."""
    base_style_palette = {
        "A": "#0039A6", "B": "#FF6319", "C": "#6CBE45", "D": "#B933AD", "E": "#00ADD0",
        "F": "#EE352E", "G": "#00933C", "H": "#B35100", "I": "#FFD500", "J": "#A7A9AC",
        "K": "#4A90E2", "L": "#9013FE"
    }
    js_lines = []
    for agency_name, letter_code in HARDCODED_AGENCY_MAPPING.items():
        js_lines.append({
            "id": letter_code,
            "label": letter_code,
            "color": base_style_palette.get(letter_code, "#00ADD0"),
            "name": agency_name,
            "desc": f"Agency Layer: {agency_name}"
        })
    return js_lines

def extract_raw_coordinates_from_text(text_block):
    """Isolates and rounds coordinate decimal float structures found within target text blocks to 5 decimal points (~1m precision)."""
    if not text_block:
        return []
    found_numbers = re.findall(r"[-+]?\d+\.\d+", text_block)
    return [round(float(num), 5) for num in found_numbers]

def inject_project_to_html(html_path, new_project_obj):
    """
    Validates and injects a new project data object into the target HTML file.
    
    :param html_path: Path to the target HTML map dashboard
    :param new_project_obj: Dictionary containing project metadata and feature geometries
    :return: True on success, error code string on validation failure, or False on exception
    """
    if not os.path.exists(html_path):
        print(f"Error: Target HTML file not found at path: {html_path}")
        return False

    target_id = new_project_obj["id"].strip()

    # -------------------------------------------------------------------------
    # VALIDATION A: Strict 5-Digit Corporate Naming Convention Regex Check
    # Matches: 11504, 11504.01, 11504.04 Biosolids, 11506.01A, etc.
    # -------------------------------------------------------------------------
    id_pattern = re.compile(r"^\d{5}(\.\d{2}[A-Za-z]?)?(\s.*)?$")
    if not id_pattern.match(target_id):
        print(f"Validation Failure: Project ID '{target_id}' does not match standard 5-digit format.")
        return "INVALID_ID"

    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # -------------------------------------------------------------------------
        # VALIDATION B: Check for Duplicate Project ID
        # -------------------------------------------------------------------------
        id_search_string = f'"id": "{target_id}"'
        if id_search_string in html_content:
            print(f"Validation Failure: Project ID {target_id} already exists in the map.")
            return "DUPLICATE_ID"

        # -------------------------------------------------------------------------
        # VALIDATION C: Check for Duplicate Coordinates / Project Limits
        # -------------------------------------------------------------------------
        new_coords = extract_raw_coordinates_from_text(json.dumps(new_project_obj.get("features", [])))
        
        if new_coords:
            # Isolating the global PROJECTS data declaration block from code content
            projects_match = re.search(r"const PROJECTS\s*=\s*\[(.*?)\]\s*;", html_content, re.DOTALL)
            if projects_match:
                projects_content = projects_match.group(1)
                
                # Sifting out explicit features arrays via regular expressions to bypass json.loads restrictions
                features_matches = re.findall(r'"features"\s*:\s*(\[.*?\])\s*,\s*"\w+"', projects_content, re.DOTALL)
                if not features_matches:
                    features_matches = re.findall(r'"features"\s*:\s*(\[.*?\])\s*\}', projects_content, re.DOTALL)

                for feat_text in features_matches:
                    existing_coords = extract_raw_coordinates_from_text(feat_text)
                    
                    # Aborting the insertion sequence if raw spatial geometries match coordinates perfectly
                    if existing_coords and new_coords == existing_coords:
                        print("Validation Failure: Map coordinates identical to an existing project area.")
                        return "DUPLICATE_GEOMETRY"

        # -------------------------------------------------------------------------
        # PROCEED WITH INJECTION
        # -------------------------------------------------------------------------
        array_declaration = "const PROJECTS = ["
        if array_declaration not in html_content:
            print("Error: Could not locate the 'const PROJECTS = [' array inside the HTML file.")
            return False

        placemark_count = len(new_project_obj.get("features", []))
        project_data_block = {
            "id": new_project_obj["id"],
            "name": new_project_obj["name"],
            "agency": new_project_obj["agency"],
            "client": new_project_obj["client"],
            "projType": new_project_obj["projType"],
            "year": new_project_obj["year"],
            "line": new_project_obj["line"],
            "center": new_project_obj["center"],
            "features": new_project_obj["features"],
            "placemark_count": placemark_count,
            "folder_path": new_project_obj["folder_path"]
        }
        
        raw_json_string = json.dumps(project_data_block, indent=4)
        indented_lines = ["    " + line for line in raw_json_string.splitlines()]
        formatted_js_object = "\n".join(indented_lines).strip()
        
        insertion_string = f"{array_declaration}\n    {formatted_js_object},"
        html_content = html_content.replace(array_declaration, insertion_string, 1)

        # Recompiling the structural JavaScript LINES configuration layer block
        js_lines_data = generate_static_js_lines_array()
        compiled_lines_string = f"const LINES = {json.dumps(js_lines_data, indent=4)};"
        html_content = re.sub(r"const LINES\s*=\s*\[.*?\]\s*;", compiled_lines_string, html_content, flags=re.DOTALL)

        # Recompiling filter array configuration elements
        unique_agencies = ["All"] + [item["name"] for item in js_lines_data]
        compiled_chips_string = f"['" + "', '".join(unique_agencies) + "']"
        html_content = re.sub(r"\['All'\s*,\s*'DEP'.*?\]", compiled_chips_string, html_content)

        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
            
        return True

    except Exception as e:
        print(f"Error: Map dataset workflow automation injection failed.\n{str(e)}")
        return False
