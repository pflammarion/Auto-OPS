import json

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

def init_diffusion_zones(diffusion):
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
            coords = diffusion.get_zone_by_index(index).get_right_points_coords() + diffusion.get_zone_by_index(
                index + 1).get_left_points_coords()

        new_zone = Zone(ShapeType.DIFFUSION)
        new_zone.set_coordinates_from_list(coords)
        temp_zone_to_add.append(new_zone)

        # To handle non square polygones shapes
        unique_y_values = set(point[1] for point in coords)

        if len(unique_y_values) > 2:
            min_x = new_zone.get_min_x_coord()
            max_x = new_zone.get_max_x_coord()

            for x, y in zip(*diffusion.polygon.exterior.xy):
                if min_x < x < max_x:
                    coords.append((x, y))

            new_zone.set_coordinates_from_list(coords)

    for zone in temp_zone_to_add:
        diffusion.set_zone(zone)


class GdsDrawing:

    def __init__(self, gds_cell, gate_type, layer_list, positions, truthtable, voltage, draw_inputs):

        # For debug
        self.is_debug = False

        self.gate_type = gate_type

        self.positions = positions
        self.truthtable = truthtable

        self.inputs = draw_inputs

        self.element_list = []
        self.reflection_list = []

        self.gds_cell = gds_cell

        for volt in voltage:
            if "ground" in volt["type"]:
                self.ground_pin_name = volt["name"]
            elif "power" in volt["type"]:
                self.power_pin_name = volt["name"]

        self.element_extractor(layer_list)
        self.main()

    def element_extractor(self, layer_list):

        for label in self.gds_cell.labels:
            if label.layer == layer_list[4]:
                founded_label = Label(label.text, label.position.tolist())
                self.element_list.append(founded_label)

        # extract polygons from GDS
        polygons = self.gds_cell.get_polygons(by_spec=True)

        for layer in layer_list:
            extracted_polygons = polygons.get((layer, 0), [])
            merged_polygons = mergePolygons(extracted_polygons)
            for polygon in merged_polygons:
                shape = Shape(None, polygon, polygon.exterior.xy, layer)
                shape.set_shape_type(layer_list)
                self.element_list.append(shape)

    def main(self):
        self.element_sorting()

        elements_to_keep = []
        for element in self.element_list:
            if not (isinstance(element, Shape) and element.shape_type == ShapeType.VIA):
                elements_to_keep.append(element)

        self.element_list = elements_to_keep

        for diffusion in self.reflection_list:
            self.connect_diffusion_to_polygon(diffusion)

        for diffusion in self.reflection_list:
            init_diffusion_zones(diffusion)

        for diffusion in self.reflection_list:
            self.connect_diffusion_to_metal(diffusion)

        self.set_zone_states()

        # self.plot_elements()
        # self.plot_reflection()
        # self.export_reflection_to_json()

        # self.export_reflection_to_png()

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

    def plot_reflection(self):
        color_list = ['black', 'white']
        fig, ax = plt.subplots()
        for reflection in self.reflection_list:
            x, y = reflection.polygon.exterior.xy
            plt.plot(x, y)

            for zone in reflection.zone_list:
                x, y = zone.coordinates
                ax.scatter(x, y, marker='o')
                state = zone.state
                if reflection.shape_type == ShapeType.PMOS:
                    if bool(state):
                        state = 0
                    else:
                        state = 1

                if state is None:
                    raise Exception("The RCV calculation cannot be performed on this shape " + str(self.gate_type) + ". Please try again")
                else:
                    ax.fill(x, y, facecolor=color_list[state], alpha=0.2, edgecolor='black', linewidth=1)

        plt.title(self.gate_type)
        plt.show()

    def export_reflection_to_png(self):
        color_list = ['white', 'black']
        fig, ax = plt.subplots()
        for reflection in self.reflection_list:
            for zone in reflection.zone_list:
                x, y = zone.coordinates
                state = zone.state
                if reflection.shape_type == ShapeType.PMOS:
                    if bool(state):
                        state = 0
                    else:
                        state = 1

                if state is None:
                    raise Exception("The RCV calculation cannot be performed on this shape " + str(self.gate_type) + ". Please try again")
                else:
                    ax.fill(x, y, facecolor=color_list[state], alpha=1, edgecolor='grey', linewidth=1)

        string_list = [f"{key}_{value}" for key, value in sorted(self.inputs.items())]
        result_string = "_".join(string_list)
        file_name = str(self.gate_type) + "__" + result_string
        path_name = "tmp/" + file_name
        plt.title(file_name)
        plt.savefig(path_name)
        plt.close()

    def export_reflection_to_json(self):
        data = {'cell_name': self.gate_type, 'inputs': self.inputs, 'reflection': []}
        for diffusion in self.reflection_list:

            ref_type = str(diffusion.shape_type)
            zone_list = []

            for zone in diffusion.zone_list:
                coordinates = [(x, y) for x, y in zip(*zone.coordinates)]
                state = zone.state
                zone_type = str(zone.shape_type)
                zone_list.append({'type': zone_type, 'state': state, 'coordinates': coordinates})

            data['reflection'].append({'type': ref_type, 'zone_list': zone_list})

        string_list = [f"{key}_{value}" for key, value in sorted(self.inputs.items())]
        result_string = "_".join(string_list)
        file_name = str(self.gate_type) + "__" + result_string + ".json"
        path_name = "test/output_samples_v2/" + file_name

        with open(path_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def element_sorting(self):
        for element in self.element_list:
            if isinstance(element, Shape) and element.shape_type != ShapeType.VIA:
                for via in self.element_list:
                    if isinstance(via, Shape) and via.shape_type == ShapeType.VIA and element.polygon.intersects(
                            via.polygon):
                        element.add_via(via)

        for element in self.element_list:
            if isinstance(element, Shape):
                self.is_connected(element)

        for element in self.element_list:
            # To set up diffusion number if connected to at least one metal
            if isinstance(element, Shape) and element.shape_type == ShapeType.DIFFUSION and isinstance(
                    element.attribute, Shape):
                diffusion = Diffusion(element.polygon)

                is_pmos = False
                for item in self.element_list:
                    if isinstance(element, Shape) and isinstance(item, Shape) and item.shape_type == ShapeType.NWELL and item.polygon.intersects(element.polygon):
                        diffusion.set_type(ShapeType.PMOS)
                        is_pmos = True
                        break

                if not is_pmos:
                    diffusion.set_type(ShapeType.NMOS)

                self.reflection_list.append(diffusion)

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
                                    if label.name in output:
                                        if inputs == self.inputs:
                                            element.set_attribute(
                                                Attribute(ShapeType.OUTPUT, label.name, output[label.name])
                                            )
                                    else:
                                        raise Exception("Missing inputs: " + str(inputs))

                            break
                        else:
                            raise Exception("Missing label: " + str(label.name))
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
            if isinstance(element, Shape) and element.shape_type == ShapeType.POLYSILICON and \
                    element.polygon.intersects(diffusion.polygon):

                intersections = diffusion.polygon.intersection(element.polygon)
                if hasattr(intersections, "geoms"):
                    for index, inter in enumerate(intersections.geoms):
                        diffusion.set_zone(Zone(ShapeType.POLYSILICON, inter.exterior.xy, element))
                else:
                    diffusion.set_zone(Zone(ShapeType.POLYSILICON, intersections.exterior.xy, element))

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
        for diffusion in self.reflection_list:

            if diffusion.shape_type is None:
                Exception("Error diffusion shape type none")

            diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

            # known state loop
            for zone in diffusion.zone_list:
                if zone.connected_to is not None:
                    if isinstance(zone.connected_to.attribute, Attribute):
                        if zone.connected_to.attribute.shape_type == ShapeType.VDD:
                            zone.set_state(1)
                        elif zone.connected_to.attribute.shape_type == ShapeType.VSS:
                            zone.set_state(0)

                        elif zone.connected_to.attribute.shape_type == ShapeType.OUTPUT:
                            zone.set_state(zone.connected_to.attribute.state)

                        elif zone.connected_to.attribute.shape_type == ShapeType.INPUT and zone.connected_to.attribute.label == "GCK":
                            raise AttributeError("Clock gates not working " + str(zone.connected_to.attribute.label))

                        else:
                            raise AttributeError("Wrong attribut in " + str(zone.connected_to.shape_type))

                    elif isinstance(zone.connected_to.attribute, Shape) and isinstance(
                            zone.connected_to.attribute.attribute,
                            Attribute) and zone.connected_to.attribute.attribute.shape_type == ShapeType.INPUT:
                        zone.set_state(zone.connected_to.attribute.attribute.state)

            # Wire unknown loop
            for zone in diffusion.zone_list:
                if isinstance(zone.connected_to, Shape) and zone.connected_to.shape_type == ShapeType.METAL \
                        and not zone.wire and zone.connected_to.attribute is None:

                    found_state = None
                    for index, zone_to_find in enumerate(diffusion.zone_list):
                        if zone_to_find.connected_to == zone.connected_to:
                            if zone_to_find.state is not None:
                                found_state = zone_to_find.state
                            elif zone_to_find.connected_to.shape_type is not ShapeType.POLYSILICON:
                                found_state = self.find_neighbor_state(diffusion, index)
                            if found_state is not None:
                                break

                    if found_state is not None:
                        for diffusion_loop in self.reflection_list:
                            # Find other zone connected to this wire branch
                            for index, zone_to_apply in enumerate(diffusion_loop.zone_list):
                                if zone_to_apply.connected_to == zone.connected_to or (
                                        isinstance(zone_to_apply.connected_to, Shape) and
                                        zone_to_apply.connected_to.attribute == zone.connected_to):
                                    if zone_to_apply.state is None:

                                        zone_to_apply.set_state(found_state)
                                        zone_to_apply.wire = True


            # Unknown loop
            for index, zone in enumerate(diffusion.zone_list):
                if zone.connected_to is None:
                    found_state = self.find_neighbor_state(diffusion, index)
                    if found_state is not None:

                        zone.set_state(found_state)
                    else:
                        zone.set_state(0)

    def find_neighbor_state(self, diffusion, zone_index) -> bool:
        diffusion_type = diffusion.shape_type
        zone_list = diffusion.zone_list
        neighbor_index = [zone_index - 1, zone_index + 1]
        stop_loop = False
        found_state = None

        while not stop_loop:
            for index in range(len(neighbor_index)):
                if neighbor_index[index] is not None and 0 <= neighbor_index[index] < len(zone_list):

                    if index == 0:
                        next_index = neighbor_index[index] - 1
                    else:
                        next_index = neighbor_index[index] + 1

                    zone = zone_list[neighbor_index[index]]

                    if zone.shape_type == ShapeType.POLYSILICON:
                        if diffusion_type == ShapeType.PMOS and zone.state == 0:
                            neighbor_index[index] = next_index
                            continue

                        elif diffusion_type == ShapeType.NMOS and zone.state == 1:
                            neighbor_index[index] = next_index
                            continue
                        else:
                            neighbor_index[index] = None
                            continue

                    elif (zone.connected_to is not None and zone.connected_to.shape_type == ShapeType.METAL and zone.state is not None) or zone.state is not None:
                        found_state = zone.state
                        stop_loop = True
                        break

                    else:
                        neighbor_index[index] = next_index
                        continue
                else:
                    neighbor_index[index] = None
                    continue

            # If the zone is between two un passing zones, not reflecting state applied
            if all(x is None for x in neighbor_index):

                if diffusion_type == ShapeType.PMOS:
                    found_state = 1

                else:
                    found_state = 0

                if self.is_debug is True:
                    print("State not found for " + str(zone_index) + " in zone list in " + str(diffusion.shape_type))
                break

        return found_state
