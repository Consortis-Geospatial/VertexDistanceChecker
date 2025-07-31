from PyQt5.QtWidgets import QDockWidget, QListWidget, QVBoxLayout, QWidget, QProgressBar, QPushButton
from qgis.gui import QgsRubberBand
from qgis.core import QgsGeometry, QgsWkbTypes
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer

class VertexDockWidget(QDockWidget):
    def __init__(self, iface, canvas, vertices):
        super().__init__("Segments Below Minimum Length", iface.mainWindow())
        self.iface = iface
        self.canvas = canvas
        self.vertices = vertices

        content_widget = QWidget()
        self.layout = QVBoxLayout()

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)  # Initially hidden
        self.layout.addWidget(self.progress_bar)

        # Add list widget for vertices
        self.list_widget = QListWidget()
        self.update_vertex_list()
        self.list_widget.itemClicked.connect(self.zoom_to_vertex)
        self.layout.addWidget(self.list_widget)

        # Download Shapefile Button (created once, hidden initially)
        self.download_button = QPushButton("Export Shapefile")
        self.download_button.clicked.connect(lambda: self.iface.pluginManager().plugins['VertexDistanceChecker'].export_to_shapefile(self.vertices, self.iface.activeLayer()))
        self.download_button.setVisible(False)  # Initially hidden
        self.layout.addWidget(self.download_button)

        content_widget.setLayout(self.layout)
        self.setWidget(content_widget)

    def start_progress(self, total_features):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def end_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.reset()

    def update_vertices(self, vertices):
        self.vertices = vertices
        self.update_vertex_list()

    def update_vertex_list(self):
        self.list_widget.clear()
        for v in self.vertices:
            item_text = f"FID {v['fid']} - Length: {v['distance']:.2f}"
            self.list_widget.addItem(item_text)

    def zoom_to_vertex(self, item):
        index = self.list_widget.currentRow()
        vertex = self.vertices[index]
        p1 = vertex['point1']
        p2 = vertex['point2']

        center = p1.__class__((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
        self.canvas.setCenter(center)
        self.canvas.zoomScale(100)
        self.canvas.refresh()

        rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        rubber_band.setColor(QColor(255, 0, 0))
        rubber_band.setWidth(3)
        rubber_band.setToGeometry(QgsGeometry.fromPolylineXY([p1, p2]), None)
        QTimer.singleShot(1000, lambda: rubber_band.reset(QgsWkbTypes.LineGeometry))