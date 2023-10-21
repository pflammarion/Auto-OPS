import gdspy

from controllers.GDS_Object.label import Label
from controllers.GDS_Object.shape import Shape

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union


import matplotlib.pyplot as plt


# A shape could be created from multiple polygones. This method merge them to have only one shape
def mergePolygons(polygons):
    polygons = [Polygon(p) for p in polygons]

    # Create a list to hold merged polygons
    merged_polygons = []

    while len(polygons) > 0:
        current_polygon = polygons.pop(0)  # Take the first polygon in the list
        connected_polygons = [current_polygon]

        i = 0
        while i < len(connected_polygons):
            for other_polygon in polygons:
                if connected_polygons[i].intersects(other_polygon):
                    connected_polygons.append(other_polygon)
                    polygons.remove(other_polygon)
            i += 1

        # Merge connected polygons using unary_union
        merged_polygon = unary_union(connected_polygons)
        merged_polygons.append(merged_polygon)

    return merged_polygons


class NewGdsDrawing:

    def __init__(self, gds, gate_type, layer_list, positions,
                 truthtable, voltage, draw_inputs):

        ##### For debug
        self.is_debug = True

        self.gate_type = gate_type

        self.positions = positions
        self.truthtable = truthtable

        self.inputs = draw_inputs

        self.ground_pin_name = None
        self.power_pin_name = None
        self.element_list = []

        for volt in voltage:
            if "ground" in volt["type"]:
                self.ground_pin_name = volt["name"]
            elif "power" in volt["type"]:
                self.power_pin_name = volt["name"]

        self.element_extractor(gds, layer_list)
        self.main()


    def element_extractor(self, gds, layer_list):
        lib = gdspy.GdsLibrary()
        lib.read_gds(gds)
        cell = lib.cells[self.gate_type]

        # extract labels from GDS
        for label in cell.labels:
            if label.layer == layer_list[3]:
                founded_label = Label(label.text, label.position.tolist())
                self.element_list.append(founded_label)

        # extract polygons from GDS
        polygons = cell.get_polygons(by_spec=True)

        for layer in layer_list:
            extracted_polygons = polygons.get((layer, 0), [])
            merged_polygons = mergePolygons(extracted_polygons)
            for polygon in merged_polygons:
                shape = Shape(None, polygon.exterior.xy, layer)
                shape.set_shape_type(layer_list)
                self.element_list.append(shape)


    def main(self):
        self.print_elements()

    def print_elements(self):
        for element in self.element_list:
            x, y = element.coordinates
            if isinstance(element, Label):
                plt.scatter(x, y)
                plt.annotate(element.name, (x, y))

            else:
                plt.plot(x, y)

        plt.title(self.gate_type)
        plt.show()













