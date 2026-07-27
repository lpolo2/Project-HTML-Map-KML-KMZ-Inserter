"""
Project Network Folder Location Scout
Portfolio / Open-Source Edition

This module provides directory scouting routines to find physical project folders 
within a target directory based on a unique project ID string. It employs strict regular 
expression boundaries to guarantee exact matches across project directory structures.

:author: Lucas Polo
:date: 2026-07-03
:version: 1.0.0
"""

import os
import re

def get_folder_path(project_id, base_directory=r"./mock_projects_dir"):
    """
    Scans a target directory to locate a physical project folder matching the given project ID.
    
    :param project_id: Unique project identifier string (e.g., '11504', '11504.01')
    :param base_directory: Path to the root directory containing project folders
    :return: Absolute string path to the matched folder, or an empty string if not found
    """
    # Checking if the master directory exists before scanning
    if not os.path.exists(base_directory):
        print(f"Error: Base directory '{base_directory}' cannot be reached.")
        return ""
        
    # Escaping the project ID so special characters like dots are treated literally
    escaped_id = re.escape(project_id)
    
    # Regular Expression: The folder name MUST start with the exact project ID, 
    # followed immediately by a space separator, an underscore, or the end of the string.
    # This prevents '11504' from matching '11504.01' or '11504A'
    search_pattern = re.compile(rf"^{escaped_id}(\s|$|_)")
    
    try:
        # Scanning all item names sitting inside the root directory folder
        for folder_name in os.listdir(base_directory):
            full_folder_path = os.path.join(base_directory, folder_name)
            
            # Filtering out standalone files, checking directory elements only
            if os.path.isdir(full_folder_path):
                if search_pattern.match(folder_name):
                    # Returning the normalized system path matching the target ID
                    return os.path.abspath(full_folder_path)
    except Exception as e:
        print(f"Error scanning directory '{base_directory}': {str(e)}")
        return ""
                
    # Returning an empty string if the loop executes completely without finding a directory match
    return ""

if __name__ == "__main__":
    # Example usage for testing and portfolio demonstration
    test_id = "11504.01"
    matched_path = get_folder_path(test_id)
    if matched_path:
        print(f"Found match for ID '{test_id}': {matched_path}")
    else:
        print(f"No matching directory found for ID '{test_id}'.")
