# GIS KML/KMZ Interactive Map Automation Engine

A Python and Leaflet.js automation tool designed to streamline the ingestion of Google Earth spatial boundaries (.kml/.kmz) directly into interactive web-based GIS dashboards.

## Key Features

*   **Automated Spatial Extraction:** Parses raw XML/KML geometry structures (polygons, lines, and center points) and translates them into clean GeoJSON feature layers.
*   **Duplicate Detection:** Features a two-pass validation system that verifies 5-digit ID naming conventions and evaluates coordinate geometries to prevent overlapping GIS boundary entries.
*   **Dynamic UI Builder:** Injects real-time spatial layers, updates Leaflet layer configurations, and syncs search filter chips without manual code edits.
*   **Enterprise-Safe Navigation:** Built-in clipboard integration that allows users to seamlessly copy network file directory paths directly to the native OS file explorer.
*   **Documentation Pipeline:** Automatically compiles clean, multi-page corporate PDF technical manuals using ReportLab.

## Tech Stack

*   **Language:** Python 3.x
*   **GUI:** Tkinter (Custom High-DPI layout)
*   **Web GIS:** JavaScript, HTML5, CSS3, Leaflet.js
*   **Geospatial / Data Parsing:** `zipfile`, `xml.etree.ElementTree`, `re`, `json`
*   **Build & PDF Tools:** PyInstaller, ReportLab

## Portfolio Demo Notice
*This repository contains sanitized mock data for demonstration purposes. No proprietary client geometries or confidential internal server paths are included.*
