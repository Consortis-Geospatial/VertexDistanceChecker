from PyQt5.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QFileDialog
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorFileWriter
from qgis.utils import iface
from PyQt5.QtCore import Qt
from .vertex_dock import VertexDockWidget
from .vertex_logic import find_close_vertices
import os

class ThresholdDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Minimum Segment Length")
        self.layout = QVBoxLayout()

        # Label and input for threshold
        self.layout.addWidget(QLabel("Minimum allowed segment length (in meters):"))
        self.threshold_input = QLineEdit("1.25")
        self.layout.addWidget(self.threshold_input)

        # Checkbox for selected features
        self.check_selected = QCheckBox("Check only selected features")
        self.layout.addWidget(self.check_selected)

        # OK and Cancel buttons
        button_layout = QVBoxLayout()
        ok_button = QPushButton("Run Check")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_threshold(self):
        return float(self.threshold_input.text()), self.check_selected.isChecked()

class VertexDistanceChecker:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.dock = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action = QAction(QIcon(icon_path), "Vertex Distance Check", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Vertex Distance Check", self.action)

    def unload(self):
        self.iface.removePluginMenu("Vertex Distance Check", self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dock:
            self.iface.removeDockWidget(self.dock)

    def run(self):
        layer = self.iface.activeLayer()
        if not layer or layer.geometryType() != QgsWkbTypes.LineGeometry:
            self.iface.messageBar().pushWarning("Vertex Distance Check |Warning|", "Please select a line layer to continue.")
            return

        # Show custom dialog
        dialog = ThresholdDialog(self.iface.mainWindow())
        if not dialog.exec_():
            return

        threshold, check_only_selected = dialog.get_threshold()

        # Create dock widget early to show progress bar
        if self.dock:
            self.iface.removeDockWidget(self.dock)
        self.dock = VertexDockWidget(self.iface, self.canvas, [])
        self.iface.addDockWidget(0x1, self.dock)
        self.dock.show()

        # Check if "Check only selected features" is checked but no selections exist
        if check_only_selected and layer.selectedFeatureCount() == 0:
            self.dock.close()
            self.iface.messageBar().pushMessage("Vertex Distance Check |Warning|", "No features selected.", level=0)
            return

        # Check features based on checkbox
        if check_only_selected and layer.selectedFeatureCount() > 0:
            features = layer.selectedFeatures()
            total_features = layer.selectedFeatureCount()
        else:
            features = layer.getFeatures()
            total_features = layer.featureCount()

        vertices = []
        self.dock.start_progress(total_features)
        for i, feature in enumerate(features):
            geom = feature.geometry()
            if geom:
                if geom.isMultipart():
                    lines = geom.asMultiPolyline()
                else:
                    lines = [geom.asPolyline()]
                for line in lines:
                    for j in range(len(line) - 1):
                        p1 = line[j]
                        p2 = line[j + 1]
                        dist = QgsPointXY(p1).distance(QgsPointXY(p2))
                        if dist < threshold:
                            vertices.append({
                                'fid': feature.id(),
                                'vertex_index': j,
                                'point1': p1,
                                'point2': p2,
                                'distance': dist
                            })
            self.dock.update_progress((i + 1) * 100 // total_features)

        self.dock.end_progress()

        if vertices:
            # Update dock widget with vertices
            self.dock.update_vertices(vertices)
            # Show the download button
            self.dock.download_button.setVisible(True)
        else:
            self.dock.close()
            self.iface.messageBar().pushMessage("Vertex Distance Check |Check Complete|", "No short segments found.", level=0)

    def export_to_shapefile(self, vertices, source_layer):
        if not vertices:
            return

        # Create a new point layer for midpoints with EPSG:2100
        vl = QgsVectorLayer("Point?crs=epsg:2100", "short_segment_midpoints", "memory")
        pr = vl.dataProvider()
        vl.startEditing()

        for v in vertices:
            center = QgsPointXY((v['point1'].x() + v['point2'].x()) / 2, (v['point1'].y() + v['point2'].y()) / 2)
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPointXY(center))
            fet.setAttributes([v['fid'], v['distance']])
            pr.addFeature(fet)

        vl.commitChanges()
        vl.updateExtents()

        # Save to shapefile
        save_path, _ = QFileDialog.getSaveFileName(None, "Export Shapefile", "", "Shapefile (*.shp)")
        if save_path:
            error = QgsVectorFileWriter.writeAsVectorFormat(vl, save_path, "UTF-8", vl.crs(), "ESRI Shapefile")
            if error[0] == QgsVectorFileWriter.NoError:
                self.iface.messageBar().pushSuccess("Vertex Distance Check |Export Complete|", "Shapefile was successfully saved.")
            else:
                self.iface.messageBar().pushCritical("Vertex Distance Check |Export Failed|", "Failed to save the shapefile.")