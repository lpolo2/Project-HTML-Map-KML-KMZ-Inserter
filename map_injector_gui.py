"""
GIS Project Map KML Inserter Application Controller
Portfolio / Open-Source Edition

This script coordinates the layout presentation windows, automates form entry fields, 
and dispatches data event streams for the GIS map insertion utility tools.

:author: Lucas Polo
:date: 2026-07-14
:version: 7.0.0
"""

import os
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox

# Activating modern Windows high-DPI scaling checks before drawing interface frames
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Importing the visual view layer and backend operational pipeline modules
from injector_panel import InjectorPanel
import folder_locator
import kml_reader
import html_injector
import string_utils

# Relative default path targeting the map dashboard template in the workspace
HTML_MAP_PATH = r"./map_dashboard.html"

class MapInjectorApp:
    def __init__(self, root_window):
        """Initializes application window framework parameters and layout geometry."""
        self.root = root_window
        self.root.title("Project HTML Map KML/KMZ Inserter")
        self.root.resizable(False, False)
        
        # Establishing a persistent fallback tracking directory for the file browser
        self.last_opened_dir = r"./"
        
        # Static agency mapping dictionary establishing palette layer keys
        self.agency_mapping = {
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
        
        # Instantiating the visual form panel and passing static agency keys
        self.panel = InjectorPanel(self.root, self, list(self.agency_mapping.keys()))
        
        # Force Tkinter layout evaluation to calculate initial dimensions
        self.root.update_idletasks()
        
        # Centering the window geometry higher on the monitor
        center_x = int((self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 2)
        center_y = max(0, int((self.root.winfo_screenheight() - self.root.winfo_reqheight()) / 2) - 140)
        self.root.geometry(f"{self.root.winfo_reqwidth()}x{self.root.winfo_reqheight()}+{center_x}+{center_y}")

    def handle_browse_file(self):
        """Opens native file dialog and populates form fields using parsed metadata guesses."""
        # Clearing historical entry strings out of fields
        self.panel.fields["file"].delete(0, tk.END)
        self.panel.fields["id"].delete(0, tk.END)
        self.panel.fields["client"].delete(0, tk.END)
        self.panel.fields["type"].delete(0, tk.END)
        self.panel.fields["year"].delete(0, tk.END)
        self.panel.fields["agency"].set("")
        
        # Triggering native file explorer filter dialog window
        file_path = filedialog.askopenfilename(
            parent=self.root,
            initialdir=self.last_opened_dir,
            title="Select KML or KMZ Project File",
            filetypes=[("Geospatial Files", "*.kml *.kmz")]
        )
        
        # Updating text entry box and running identity parsing routines upon selection
        if file_path:
            self.last_opened_dir = os.path.dirname(file_path)
            self.panel.fields["file"].insert(0, file_path)
            
            # Step A: Parsing filename to check for numerical prefix index codes
            guessed_id = string_utils.guess_project_id_from_name(os.path.basename(file_path))
            
            # Step B: Parsing inner XML data tags to discover metadata properties
            features, center, xml_agency, xml_client, xml_type, xml_year, final_id = kml_reader.parse_kml_geometries(file_path, guessed_id)
            
            # Populating fields with automated metadata matches
            if final_id:
                self.panel.fields["id"].insert(0, final_id)
            if xml_agency:
                clean_agency = string_utils.clean_agency_string(xml_agency)
                if clean_agency in self.agency_mapping:
                    self.panel.fields["agency"].set(clean_agency)
            if xml_client:
                self.panel.fields["client"].insert(0, xml_client.strip())
            if xml_type:
                self.panel.fields["type"].insert(0, xml_type.strip())
            if xml_year:
                self.panel.fields["year"].insert(0, xml_year.strip())

    def handle_inject_action(self):
        """Validates inputs, extracts geometries, and executes HTML injection sequence."""
        kml_file = self.panel.fields["file"].get().strip()
        project_id = self.panel.fields["id"].get().strip()
        agency = string_utils.clean_agency_string(self.panel.fields["agency"].get())
        client = self.panel.fields["client"].get().strip()
        proj_type = self.panel.fields["type"].get().strip()
        year = self.panel.fields["year"].get().strip()
        
        # Halting execution if mandatory form fields are unpopulated
        if not kml_file or not project_id:
            messagebox.showerror("Missing Data", "Project ID and KML/KMZ File paths are required fields.")
            return

        # Parsing file geometries to verify coordinate requirements
        features, master_center, xml_agency, xml_client, xml_type, xml_year, final_id = kml_reader.parse_kml_geometries(kml_file, project_id)
        if not features:
            messagebox.showerror("Geometry Error", "No valid coordinate shapes could be extracted from this file.")
            return

        # Applying KML metadata fallbacks if inputs were left blank
        if not agency and xml_agency:
            agency = string_utils.clean_agency_string(xml_agency)
            if agency in self.agency_mapping:
                self.panel.fields["agency"].set(agency)
        if not client and xml_client:
            client = xml_client.strip()
            self.panel.fields["client"].insert(0, client)
        if not proj_type and xml_type:
            proj_type = xml_type.strip()
            self.panel.fields["type"].insert(0, proj_type)
        if not year and xml_year:
            year = xml_year.strip()
            self.panel.fields["year"].insert(0, year)
            
        # Stopping execution if mandatory inputs remain unassigned
        if not agency:
            messagebox.showerror("Missing Agency", "Agency field is empty and could not be detected inside the KML file.")
            return
        if not client:
            messagebox.showerror("Missing Client", "Client field is required. Please type or select the project client.")
            return

        # Evaluating selected agency against tracking keys
        if agency in self.agency_mapping:
            assigned_letter = self.agency_mapping[agency]
        else:
            messagebox.showerror("Invalid Agency", f"Agency '{agency}' is not supported by the current map layout configuration.")
            return

        # Locating project directory path
        folder_path = folder_locator.get_folder_path(project_id) or ""

        # Compiling fields into standardized database object schema
        new_project_obj = {
            "id": project_id, "name": project_id, "agency": agency, "client": client,
            "projType": proj_type if proj_type else "Unknown Project Type",
            "year": year if year else "Ongoing",
            "line": assigned_letter, "center": master_center, "features": features,
            "folder_path": folder_path
        }

        # Executing database injection into target map file
        injection_result = html_injector.inject_project_to_html(HTML_MAP_PATH, new_project_obj)
        
        # Intercepting operational validation codes to fire user messages
        if injection_result == "INVALID_ID":
            messagebox.showerror(
                "Invalid Project ID Format",
                f"The ID '{project_id}' does not match standard 5-digit conventions.\n\n"
                "It must start with a 5-digit number (e.g., 11504) and can optionally be followed by a decimal extension."
            )
        elif injection_result == "DUPLICATE_ID":
            messagebox.showwarning(
                "Project Already Exists", 
                f"Project '{project_id}' is already logged in the map layout!\n\nThis insertion has been blocked to prevent data duplication."
            )
        elif injection_result == "DUPLICATE_GEOMETRY":
            messagebox.showwarning(
                "Duplicate Map Boundaries Detected", 
                "These exact geospatial project limits and coordinates are already mapped under another Project ID!\n\n"
                "Insertion stopped to prevent duplicate overlapping graphics on the Leaflet dashboard."
            )
        elif injection_result:
            messagebox.showinfo("Insertion Successful", f"Project '{project_id}' inserted successfully into the map!")
        else:
            messagebox.showerror("Write Error", "Failed to insert project record into the HTML map file.")

if __name__ == "__main__":
    # Booting GUI engine framework
    main_window = tk.Tk()
    app = MapInjectorApp(main_window)
    main_window.mainloop()
