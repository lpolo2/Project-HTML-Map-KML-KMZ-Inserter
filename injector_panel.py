"""
GIS Project Injector Form Panel Layout
Portfolio / Open-Source Edition

This module constructs the user interface grid panel using Tkinter. It handles 
the rendering of form frames, entry widgets, comboboxes, and action buttons, 
exposing input elements to a controller class to separate visual presentation 
from event processing.

:author: Lucas Polo
:date: 2026-07-09
:version: 1.1.2
"""

import tkinter as tk
from tkinter import ttk

class InjectorPanel:
    def __init__(self, parent_frame, controller, agency_list):
        """
        Initializes the panel layout and draws form elements.
        
        :param parent_frame: Parent Tkinter widget or window container
        :param controller: Controller instance managing event callback handlers
        :param agency_list: List of agency strings to populate the dropdown selection
        """
        self.parent = parent_frame
        self.controller = controller
        
        # Dictionary holding references to interactive entry fields
        self.fields = {}
        
        # Construct visual interface components
        self.draw_form_fields(agency_list)

    def draw_form_fields(self, agency_list):
        """Constructs and grids form labels, entries, and execution buttons."""
        pad_opts = {'padx': 15, 'pady': 8}
        
        # Master frame container
        form_frame = tk.Frame(self.parent)
        form_frame.pack(fill="x", **pad_opts)
        
        # Row 1: File Selection Field
        tk.Label(form_frame, text="Select KML/KMZ File:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        file_entry = tk.Entry(form_frame, width=40)
        file_entry.grid(row=1, column=0, sticky="we", padx=(0, 5))
        self.fields["file"] = file_entry
        
        browse_btn = tk.Button(form_frame, text="Browse...", command=self.controller.handle_browse_file)
        browse_btn.grid(row=1, column=1, sticky="w")
        
        # Row 2: Required Identity Inputs (Project ID & Agency)
        tk.Label(form_frame, text="Project ID (Required):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        id_entry = tk.Entry(form_frame, width=25)
        id_entry.grid(row=3, column=0, sticky="w")
        self.fields["id"] = id_entry
        
        # Agency Dropdown
        tk.Label(form_frame, text="Agency (Select):", font=("Arial", 10, "bold")).grid(row=2, column=1, sticky="w", pady=(10, 5))
        agency_combobox = ttk.Combobox(form_frame, values=sorted(agency_list), width=18, state="readonly")
        agency_combobox.grid(row=3, column=1, sticky="w")
        agency_combobox.bind("<<ComboboxSelected>>", lambda e: [agency_combobox.selection_clear(), form_frame.focus()])  
        self.fields["agency"] = agency_combobox
        
        # Row 3: Client & Project Type
        tk.Label(form_frame, text="Client (Required):", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 5))
        
        client_entry = tk.Entry(form_frame, width=30)
        client_entry.grid(row=5, column=0, sticky="w")
        self.fields["client"] = client_entry
        
        tk.Label(form_frame, text="Project Type (Optional):", font=("Arial", 10)).grid(row=4, column=1, sticky="w", pady=(10, 5))
        
        type_entry = tk.Entry(form_frame, width=20)
        type_entry.grid(row=5, column=1, sticky="w")
        self.fields["type"] = type_entry
        
        # Row 4: Timeline Tracker Field
        tk.Label(form_frame, text="Project Year (Optional):", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=(10, 5))
        
        year_entry = tk.Entry(form_frame, width=15)
        year_entry.grid(row=7, column=0, sticky="w")
        self.fields["year"] = year_entry
        
        # Row 5: Action Button
        inject_btn = tk.Button(
            self.parent, text="INSERT PROJECT INTO MAP", font=("Arial", 11, "bold"),
            bg="#00ADD0", fg="white", height=2, command=self.controller.handle_inject_action
        )
        inject_btn.pack(fill="x", padx=15, pady=25)
