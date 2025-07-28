from qgis.core import QgsPointXY

def find_close_vertices(layer, distance_threshold=1.25):
    close_vertices = []
    for feature in layer.getFeatures():
        geom = feature.geometry()
        if not geom:
            continue
        if geom.isMultipart():
            lines = geom.asMultiPolyline()
        else:
            lines = [geom.asPolyline()]

        for line in lines:
            for i in range(len(line) - 1):
                p1 = line[i]
                p2 = line[i + 1]
                dist = QgsPointXY(p1).distance(QgsPointXY(p2))
                if dist < distance_threshold:
                    close_vertices.append({
                        'fid': feature.id(),
                        'vertex_index': i,
                        'point1': p1,
                        'point2': p2,
                        'distance': dist
                    })
    return close_vertices
