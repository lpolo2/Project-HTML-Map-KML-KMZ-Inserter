"""
GIS Project HTML Map Pipeline Integration Utilities
Portfolio / Open-Source Edition

This module provides backend data-writing routines to inspect, inject, and remove
geospatial database objects directly within a static HTML application file using
multi-line regular expressions and JSON array manipulations.

:author: Lucas Polo
:date: 2026-07-02
:version: 1.5.0
"""

import json 
import re
import os

def inject_project_into_html(html_filepath, project_obj):
    """
    Parses the target HTML dashboard and appends a new project object if not present.
    
    :param html_filepath: Path to the target HTML map file
    :param project_obj: Dictionary containing project metadata and coordinate features
    """
    if not os.path.exists(html_filepath):
        print(f"Error: Target HTML file not found at path '{html_filepath}'.")
        return

    # Opening and Reading the html file
    with open(html_filepath, 'r', encoding='utf-8') as html_file_variable:
        html_contents = html_file_variable.read()
        
        # Locating the projects array on the html file using regular expressions
        match = re.search(r'(const\s+PROJECTS\s*=\s*)(\[.*?\]);', html_contents, re.DOTALL)
        
        if not match:
            print("Error: Could not find the PROJECTS array in the HTML file.")
            return
        
        # Parsing the raw javascript string array into a live Python list
        content_list = json.loads(match.group(2)) 
         
        # Checking if the id of the new project already exists in the list   
        if any(existing_project.get('id') == project_obj.get('id') for existing_project in content_list):
            print(f"Warning: Project ID '{project_obj.get('id')}' already exists in the map dataset.")
        else:
            content_list.append(project_obj)
            print(f"Successfully added '{project_obj.get('id')}' to the dataset.")
            
            # Reconstructing the html text array definition
            json_string = json.dumps(content_list, indent=4)
            js_text_line = f"const PROJECTS = {json_string};"
            updated_html_contents = html_contents.replace(match.group(0), js_text_line)
    
            # Overwriting the html file
            with open(html_filepath, 'w', encoding='utf-8') as html_file_to_overwrite:
                html_file_to_overwrite.write(updated_html_contents)
            print("HTML file successfully updated.")


def remove_project_from_html(html_filepath, project_id_to_remove):
    """
    Removes a target project entry from the PROJECTS array within the HTML file.
    
    :param html_filepath: Path to the target HTML map file
    :param project_id_to_remove: String ID of the project to remove
    """
    if not os.path.exists(html_filepath):
        print(f"Error: Target HTML file not found at path '{html_filepath}'.")
        return

    # Opening and Reading the html file
    with open(html_filepath, 'r', encoding='utf-8') as html_file_variable:
        html_contents = html_file_variable.read()
        
    # Locating the target array block
    match = re.search(r'(const\s+PROJECTS\s*=\s*)(\[.*?\]);', html_contents, re.DOTALL)
    
    if not match:
        print("Error: Could not find the PROJECTS array in the HTML file.")
        return
        
    # Loading the data into a live Python list
    content_list = json.loads(match.group(2)) 
    
    # Filtering the list to exclude the target project ID
    updated_list = [project for project in content_list if project.get('id') != project_id_to_remove]
    
    # Checking if anything was removed
    if len(updated_list) == len(content_list):
        print(f"Project ID '{project_id_to_remove}' was not found. Nothing deleted.")
    else:
        # Reconstructing the HTML string with the cleaned list
        json_string = json.dumps(updated_list, indent=4)
        js_text_line = f"const PROJECTS = {json_string};"
        updated_html_contents = html_contents.replace(match.group(0), js_text_line)
        
        # Overwriting the file with the updated contents
        with open(html_filepath, 'w', encoding='utf-8') as html_file_to_overwrite:
            html_file_to_overwrite.write(updated_html_contents)
            
        print(f"Successfully deleted Project '{project_id_to_remove}' from the HTML map.")
