# VertexDistanceChecker
**VertexDistanceChecker** is a QGIS plugin that identifies line segments between consecutive vertices shorter than a user-defined threshold, helping detect oversampled geometry or digitization noise in line features.

---

## Features

- Analyze any line layer in your QGIS project.
- User-defined minimum length threshold.
- Option to check only selected features.
- Visual feedback of flagged segments via rubber bands.
- List and zoom to flagged segments in a dockable panel.
- Export flagged segments' midpoints to a Shapefile for reporting or further analysis.

---

## How It Works

1. Activate the plugin via the toolbar or plugin menu.
2. Choose a line layer to analyze.
3. Enter the minimum allowed segment length.
4. (Optional) Restrict analysis to selected features only.
5. View results in a dockable panel, with distance values and zoom capabilities.
6. Export results to a point Shapefile if needed.

---

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/Consortis-Geospatial/VertexDistanceChecker.git
2. Copy the folder to your QGIS plugin directory:
- Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
- Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
3. Open QGIS and enable the plugin via Plugins > Manage and Install Plugins.

---

## Screenshot
Coming Soon...

---

## Developer Notes

- Written in Python using the QGIS PyQt and PyQGIS.

- Uses a custom dock widget to display flagged vertex pairs.

- Midpoint geometry exported in EPSG:2100 (can be modified as needed).

---

## Support and Contributions

- **Homepage**: [https://github.com/Consortis-Geospatial](https://github.com/Consortis-Geospatial)
- **Issue Tracker**: [https://github.com/Consortis-Geospatial/VertexDistanceChecker/issues](https://github.com/Consortis-Geospatial/VertexDistanceChecker/issues)
- **Author**: Gkaravelis Andreas - Consortis Geospatial
- **Email**: gkaravelis@consortis.gr
- **Repository**: [https://github.com/Consortis-Geospatial/VertexDistanceChecker](https://github.com/Consortis-Geospatial/VertexDistanceChecker)

---

## License
This plugin is released under the GPL-3.0 license
