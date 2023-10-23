import gdspy

from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.diffusion import Diffusion
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.shape import Shape

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

import matplotlib.pyplot as plt

from controllers.GDS_Object.type import ShapeType
from controllers.GDS_Object.zone import Zone


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

        self.element_list = []
        self.reflexion_list = []

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
                shape = Shape(None, polygon, polygon.exterior.xy, layer)
                shape.set_shape_type(layer_list)
                self.element_list.append(shape)

    def main(self):
        self.element_sorting()

        for diffusion in self.reflexion_list:
            self.connect_diffusion_to_polygon(diffusion)

        for diffusion in self.reflexion_list:
            self.init_diffusion_zones(diffusion)

        for diffusion in self.reflexion_list:
            self.connect_diffusion_to_metal(diffusion)

        self.set_zone_states()

        self.plot_reflexion()

    def plot_elements(self):
        for element in self.element_list:
            x, y = element.coordinates
            if isinstance(element, Label):
                plt.scatter(x, y)
                plt.annotate(element.name, (x, y))

            else:
                plt.plot(x, y)

        plt.title(self.gate_type)
        plt.show()

    def plot_reflexion(self):
        color_list = ['black', 'white']
        fig, ax = plt.subplots()
        for reflexion in self.reflexion_list:
            x, y = reflexion.polygon.exterior.xy
            plt.plot(x, y)

            for zone in reflexion.zone_list:
                x, y = zone.coordinates
                ax.scatter(x, y, marker='o')
                state = zone.state
                if reflexion.shape_type == ShapeType.PMOS:
                    if bool(state):
                        state = 0
                    else:
                        state = 1

                ax.fill(x, y, facecolor=color_list[state], alpha=0.2, edgecolor='black', linewidth=1)

        plt.title(self.gate_type)
        plt.show()

    def element_sorting(self):
        for element in self.element_list:
            if isinstance(element, Shape) and element.shape_type != ShapeType.VIA:
                for via in self.element_list:
                    if isinstance(via, Shape) and via.shape_type == ShapeType.VIA and element.polygon.intersects(via.polygon):
                        element.add_via(via)

        for element in self.element_list:
            if isinstance(element, Shape):
                self.is_connected(element)

        for element in self.element_list:
            # To set up diffusion number if connected to at least one metal
            if isinstance(element, Shape) and element.shape_type == ShapeType.DIFFUSION and isinstance(element.attribute, Shape):
                self.reflexion_list.append(Diffusion(element.polygon))

    def is_connected(self, element):
        if element.shape_type == ShapeType.POLYSILICON or element.shape_type == ShapeType.DIFFUSION:
            for item in self.element_list:
                if isinstance(item, Shape) and item.shape_type == ShapeType.METAL:
                    for element_connection in element.connection_list:
                        if element_connection in item.connection_list:
                            element.set_attribute(item)

        elif element.shape_type == ShapeType.METAL:
            for label in self.element_list:
                if isinstance(label, Label):
                    if element.polygon.contains(Point(label.coordinates)):
                        if label.name in self.inputs.keys():
                            element.set_attribute(Attribute(ShapeType.INPUT, label.name, self.inputs[label.name]))
                            break

                        elif label.name in self.truthtable.keys():
                            for outputs in self.truthtable:
                                for inputs, output in self.truthtable[outputs]:
                                    if (inputs == self.inputs) & (label.name in output):
                                        element.set_attribute(Attribute(ShapeType.OUTPUT, label.name, output[label.name]))
                            break
                    else:
                        _, point_y = label.coordinates
                        _, metal_y = element.coordinates
                        set_metal_y = set(metal_y)
                        is_label_found = False
                        for y in set_metal_y:
                            if y == point_y:
                                is_label_found = True
                                break

                        if label.name.lower() == self.ground_pin_name.lower() and is_label_found:
                            element.set_attribute(Attribute(ShapeType.VSS))
                            break

                        elif label.name.lower() == self.power_pin_name.lower() and is_label_found:
                            element.set_attribute(Attribute(ShapeType.VDD))
                            break

    def connect_diffusion_to_polygon(self, diffusion):
        """
            To set up the poly silicon overlapping to the diffusion parts
        """
        for element in self.element_list:
            if isinstance(element, Shape) and element.shape_type == ShapeType.POLYSILICON and element.polygon.intersects(diffusion.polygon):
                intersections = diffusion.polygon.intersection(element.polygon)
                if hasattr(intersections, "geoms"):
                    for index, inter in enumerate(intersections.geoms):
                        diffusion.set_zone(Zone(ShapeType.POLYSILICON, inter.exterior.xy, element))
                else:
                    diffusion.set_zone(Zone(ShapeType.POLYSILICON, intersections.exterior.xy, element))

    def init_diffusion_zones(self, diffusion):
        temp_zone_to_add = []
        diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

        coords = diffusion.get_left_points_coords() + diffusion.get_zone_by_index(0).get_left_points_coords()
        new_zone = Zone(ShapeType.DIFFUSION)
        new_zone.set_coordinates_from_list(coords)
        temp_zone_to_add.append(new_zone)

        for index, zone in enumerate(diffusion.zone_list):
            if index == len(diffusion.zone_list) - 1:
                coords = diffusion.get_right_points_coords() + diffusion.get_zone_by_index(index).get_right_points_coords()

            else:
                coords = diffusion.get_zone_by_index(index).get_right_points_coords() + diffusion.get_zone_by_index(index + 1).get_left_points_coords()

            new_zone = Zone(ShapeType.DIFFUSION)
            new_zone.set_coordinates_from_list(coords)
            temp_zone_to_add.append(new_zone)

        for zone in temp_zone_to_add:
            diffusion.set_zone(zone)

    def connect_diffusion_to_metal(self, diffusion):
        """
            To set up the metal connected to the diffusion parts
        """
        for zone in diffusion.zone_list:
            if zone.shape_type == ShapeType.DIFFUSION:
                for element in self.element_list:
                    if isinstance(element, Shape) and element.shape_type == ShapeType.METAL:
                        zone_polygon = Polygon(Polygon(list(zip(zone.coordinates[0], zone.coordinates[1]))))
                        for connection_polygons in element.connection_list:
                            if zone_polygon.intersects(connection_polygons):
                                zone.set_connected_to(element)

                                break

    def set_zone_states(self):
        for diffusion in self.reflexion_list:

            diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

            for zone in diffusion.zone_list:
                if zone.connected_to is not None:
                    if isinstance(zone.connected_to.attribute, Attribute):
                        if zone.connected_to.attribute.shape_type == ShapeType.VDD:
                            zone.set_state(1)
                            diffusion.set_type(ShapeType.PMOS)
                        elif zone.connected_to.attribute.shape_type == ShapeType.VSS:
                            zone.set_state(0)
                            diffusion.set_type(ShapeType.NMOS)

                        elif zone.connected_to.attribute.shape_type == ShapeType.OUTPUT:
                            zone.set_state(zone.connected_to.attribute.state)
                        else:
                            raise AttributeError("Wrong attribut in " + zone.connected_to.shape_type)

                    elif isinstance(zone.connected_to.attribute, Shape) and zone.connected_to.attribute.attribute.shape_type == ShapeType.INPUT:
                        zone.set_state(zone.connected_to.attribute.attribute.state)

                    else:
                        print("find my state")

            for index, zone in enumerate(diffusion.zone_list):
                if zone.connected_to is None:
                    self.find_neighbor_state(diffusion, index)

    def find_neighbor_state(self, diffusion, zone_index):
        diffusion_type = diffusion.shape_type
        zone_list = diffusion.zone_list
        neighbor_index = [zone_index - 1, zone_index + 1]
        is_state = False

        while not is_state:
            for index in range(len(neighbor_index)):

                if index == 0:
                    next_index = neighbor_index[index] - 1
                else:
                    next_index = neighbor_index[index] + 1

                print(neighbor_index[index], next_index)

                if neighbor_index[index] is not None and 0 <= neighbor_index[index] < len(zone_list):
                    zone = zone_list[neighbor_index[index]]
                    if zone.shape_type == ShapeType.POLYSILICON:
                        if diffusion_type == ShapeType.PMOS and zone.state == 0:
                            neighbor_index[index] = next_index
                        elif diffusion_type == ShapeType.NMOS and zone.state == 1:
                            neighbor_index[index] = next_index
                        else:
                            neighbor_index[index] = None

                    elif zone.connected_to.shape_type == ShapeType.METAL:
                        zone_list[zone_index].set_state = zone.state
                        is_state = True
                        break

                    else:
                        neighbor_index[index] = None
                else:
                    neighbor_index[index] = None

            if neighbor_index[0] is None and neighbor_index[1] is None:
                raise Exception("State not found for " + str(zone_index) + " in zone list in " + str(diffusion.shape_type))


