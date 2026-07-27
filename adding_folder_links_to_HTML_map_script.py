"""
GIS Project HTML Map Directory Synchronizer
Portfolio / Open-Source Edition

This script automates the retrofitting and synchronization of project local directory 
paths with a master GIS project map HTML database. It scans a designated project 
storage directory using regular expressions to match folder names against 
valid project IDs (e.g., 5-digit structures, sub-contract decimals, and suffix letters). 

Once matched, it parses the database array from the static HTML dashboard file,
injects the corresponding local system paths into the data structure, and updates 
the deployment mapping file.

:author: Lucas Polo
:date: 2026-07-27
:version: 1.0.0
"""

import os
import re
import json

def get_folder_path(project_id, base_directory=r"./mock_projects_dir"):
    """
    Scans the designated root directory to locate the folder matching the project ID.
    """
    # Checking if the target directory exists before scanning
    if not os.path.exists(base_directory):
        print(f"Error: Target directory '{base_directory}' cannot be reached.")
        return None
        
    # Escaping the project ID so special characters like decimals are treated literally
    escaped_id = re.escape(project_id)
    
    # Regular Expression: The folder name MUST start with the exact project ID, 
    # followed immediately by a space separator, an underscore, or the end of the string.
    # This prevents '10808' from accidentally matching '10808.01' or '10808A'
    search_pattern = re.compile(rf"^{escaped_id}(\s|$|_)")
    
    # Scanning all item names sitting inside the root directory folder
    for folder_name in os.listdir(base_directory):
        full_folder_path = os.path.join(base_directory, folder_name)
        
        # Filtering out standalone files, checking directory elements only
        if os.path.isdir(full_folder_path):
            if search_pattern.match(folder_name):
                # Returning the full system directory path matching the target ID
                return full_folder_path
                
    # Returning None if the loop executes completely without finding a directory match
    return None

def add_folder_path_to_html_map(html_map_path=r"./map_dashboard.html", projects_dir=r"./mock_projects_dir"):
    """
    Locates the JS PROJECTS array in the HTML map file and injects matched directory paths.
    """
    if not os.path.exists(html_map_path):
        print(f"Error: Map HTML file not found at path '{html_map_path}'.")
        return

    # Opening and Reading the html file
    with open(html_map_path, 'r', encoding='utf-8') as html_file_variable:
        html_contents = html_file_variable.read()
        
    # Locating the projects array on the html file using regular expressions
    match = re.search(r'(const\s+PROJECTS\s*=\s*)(\[.*?\]);', html_contents, re.DOTALL)
    if not match:
        print("Error: Could not find the 'const PROJECTS' array inside the HTML map file.")
        return
        
    prefix = match.group(1) # Holds 'const PROJECTS = '
    raw_json_array = match.group(2) # Holds the actual data string '[{...}, {...}]'
    
    try:
        # Parsing the raw string array into editable Python dictionaries
        projects_list = json.loads(raw_json_array)
    except json.JSONDecodeError:
        print("Error: Failed to parse the HTML map's PROJECTS data array into valid JSON.")
        return
        
    print(f"Scanning '{projects_dir}' folder paths for {len(projects_list)} projects...")
    matched_count = 0
        
    # Looping through every single project found inside the database array
    for project in projects_list:
        # Grabbing the unique project ID
        project_id = project.get("id")
        if project_id:
            # Finding the native system directory location path
            system_path = get_folder_path(project_id, projects_dir)
            if system_path:
                # Normalizing paths for cross-platform compatibility
                normalized_path = os.path.abspath(system_path)
                project["folder_path"] = normalized_path
                matched_count += 1
            else:
                # Setting it to an empty string if no folder was discovered
                project["folder_path"] = ""

    # Converting the updated list of dictionaries back into a formatted JSON string layout
    updated_json_string = json.dumps(projects_list, indent=4)
    
    # Replacing the old array with the freshly updated data block structure
    old_array_string = prefix + raw_json_array + ";"
    new_array_string = prefix + updated_json_string + ";"
    updated_html_contents = html_contents.replace(old_array_string, new_array_string)
    
    # Overwriting the updated contents back into the HTML file
    with open(html_map_path, 'w', encoding='utf-8') as html_write_file:
        html_write_file.write(updated_html_contents)
        
    print(f"Success: The HTML map database has been successfully updated with project folder paths.")
    print(f"Linked {matched_count} out of {len(projects_list)} folders successfully.")

if __name__ == "__main__":
    # Demonstration execution using relative mock directory paths
    add_folder_path_to_html_map()
