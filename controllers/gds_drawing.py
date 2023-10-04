import gdspy
import matplotlib.pyplot as plt
import numpy as np
import json

from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union


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


def sortPointsClockwise(coordinates):
    cx, cy = np.mean(coordinates, axis=0)

    polar_angles = [np.arctan2(yi - cy, xi - cx) for xi, yi in coordinates]

    polar_angles = [angle + 2 * np.pi if angle < 0 else angle for angle in polar_angles]

    sorted_points = [point for _, point in sorted(zip(polar_angles, coordinates))]

    return [sorted_points]


def separate_to_rectangles(coordinates):
    x_coords = sorted(list(set(point[0] for point in coordinates)))

    mid_x = x_coords[1]
    min_x = x_coords[0]
    max_x = x_coords[2]

    min_y_when_min_x = None
    max_y_when_min_x = None
    for point in coordinates:
        x, y = point
        if x == min_x:
            if min_y_when_min_x is None or y <= min_y_when_min_x:
                min_y_when_min_x = y
            if max_y_when_min_x is None or y >= max_y_when_min_x:
                max_y_when_min_x = y

    max_y_when_max_x = None
    min_y_when_max_x = None
    for point in coordinates:
        x, y = point
        if x == max_x:
            if min_y_when_max_x is None or y <= min_y_when_max_x:
                min_y_when_max_x = y
            if max_y_when_max_x is None or y >= max_y_when_max_x:
                max_y_when_max_x = y

    left_rectangle = [(min_x, min_y_when_min_x), (min_x, max_y_when_min_x), (mid_x, max_y_when_min_x),
                      (mid_x, min_y_when_min_x)]
    right_rectangle = [(mid_x, min_y_when_max_x), (mid_x, max_y_when_max_x), (max_x, max_y_when_max_x),
                       (max_x, min_y_when_max_x)]

    return [left_rectangle, right_rectangle]


def plotShape(data, state, title):
    fig, ax = plt.subplots()

    point_number = 1
    counter = 0
    debug_color = ['black', 'white']

    # Iterate through the sub-dictionaries ('top' and 'bottom')
    for key, sub_dict in data.items():
        # Iterate through the sub-dictionary items ('diff_1', 'diff_2', 'poly')
        for sub_key, coordinates in sub_dict.items():

            if len(coordinates) > 4:
                sorted_points_list = separate_to_rectangles(coordinates)
            else:
                sorted_points_list = sortPointsClockwise(coordinates)
            for sorted_points in sorted_points_list:

                x, y = zip(*sorted_points)

                ax.scatter(x, y, label=f'{key} - {sub_key}', marker='o')

                for xi, yi in zip(x, y):
                    # ax.annotate(str(point_number), (xi, yi), textcoords="offset points", xytext=(0, 10), ha='center')
                    point_number += 1

                color = debug_color[0]
                # if counter < len(state):
                #   color = 'white' if state[counter] else 'black'
                if counter % 2 == 0:
                    color = debug_color[1]

                ax.fill(x, y, facecolor=color, alpha=0.2, edgecolor='black', linewidth=1)

            counter += 1

    ax.set_xlabel('X-coordinate')
    ax.set_ylabel('Y-coordinate')
    # ax.legend()
    plt.title(title)

    plt.show()


def find_extreme_points(points):
    sorted_points = sorted(points, key=lambda point: point[0])

    extreme_left = sorted_points[:2]
    extreme_right = sorted_points[-2:]

    return extreme_left, extreme_right


# This function will sort the keys in alternating order, first "diff_0", then "poly_0", "diff_1", "poly_1", and so on.
def sort_dict_alternating_keys(input_dict):
    sorted_dict = {}
    for key, value in input_dict.items():
        # Extract the keys starting with "diff_" and "poly_"
        diff_keys = [k for k in value if k.startswith("diff_")]
        poly_keys = [k for k in value if k.startswith("poly_")]

        # Sort the keys in alternating order
        sorted_keys = []
        for i in range(max(len(diff_keys), len(poly_keys))):
            if i < len(diff_keys):
                sorted_keys.append(diff_keys[i])
            if i < len(poly_keys):
                sorted_keys.append(poly_keys[i])

        # Create a new sub-dictionary with the sorted keys
        sorted_dict[key] = {sub_key: value[sub_key] for sub_key in sorted_keys}

    return sorted_dict


class GdsDrawing:
    """
    Represents a drawing element in a GDS (Graphics Data System) layout.

    Args:
        gds (str): The GDS file path or name.
        gate_type (str): The name of the gate in the gds file in the Cells' list.
        diffusion_layer (int): The number affiliated to the layer of the n and p diffusion.
        polysilicon_layer (int): The number affiliated to the layer of the polysilicon.
        positions (list): A list containing the X and Y coordinates of the drawing's position.
        truthtable (dict): The truthtable is a list containing the information the output based on the input for a gate.
        connection_layer (int): The number affiliated to the layer of the conections.
        label_layer(int): The number affiliated to the layer of labels.

    Attributes:
        gds (str): The GDS file path or name.
        gate_type (str): The name of the gate in the gds file in the Cells' list.
        diffusion_layer (int): The number affiliated to the layer of the n and p diffusion.
        polysilicon_layer (int): The number affiliated to the layer of the polysilicon.
        positions (list): A list containing the X and Y coordinates of the drawing's position.
        truthtable (dict): The truthtable is a list containing the information the output based on the input for a gate.
        connection_layer (int): The number affiliated to the layer of the conections.
        label_layer(int): The number affiliated to the layer of labels.

    Example:
        To create a GdsDrawing instance:

        >>> drawing = GdsDrawing("example.gds", "INV_X1", 1, 9, 10, 11, [10, 20], [({'A': True}, {'ZN': False}), ({'A': False}, {'ZN': True})])

    This class draw over a GDS input the optical state of each gate depending on the position and gates states.
    """

    def __init__(self, gds, gate_type, diffusion_layer, polysilicon_layer, connection_layer, label_layer, positions, truthtable):
        self.gds = gds
        self.gate_type = gate_type
        self.diffusion_layer = diffusion_layer
        self.polysilicon_layer = polysilicon_layer
        self.positions = positions
        self.truthtable = truthtable
        self.connection_layer = connection_layer
        self.label_layer = label_layer
        self.label_list = []

        self.main()

    def main(self):
        lib = gdspy.GdsLibrary()
        lib.read_gds(self.gds)
        cell = lib.cells[self.gate_type]

        for label in cell.labels:
            if label.layer == self.label_layer:
                self.label_list.append(label)
                print("Label:")
                print("Text:", label.text)
                print("Position:", label.position)
                print("-----------")

        polygons = cell.get_polygons(by_spec=True)

        # TODO check about the polygons (layers) selection for gds files (idem for diff)
        polysilicon_polygon = polygons.get((self.polysilicon_layer, 0), [])

        # find the rectangle
        merged_polysilicon_polygons = mergePolygons(polysilicon_polygon)
        sorted_polysilicon_polygons = sorted(merged_polysilicon_polygons,
                                             key=lambda polygon: min(polygon.exterior.xy[0]))

        min_y_coords = [min(polygon.exterior.xy[1]) for polygon in merged_polysilicon_polygons]
        max_y_coords = [max(polygon.exterior.xy[1]) for polygon in merged_polysilicon_polygons]

        min_y_poly = min(min_y_coords)
        max_y_poly = max(max_y_coords)

        diffusion_polygons = polygons.get((self.diffusion_layer, 0), [])

        filtered_diffusion_polygons = [polygon for polygon in diffusion_polygons if
                                       all(min_y_poly <= y <= max_y_poly for _, y in polygon)]
        merged_diffusion_polygons = mergePolygons(filtered_diffusion_polygons)
        sorted_diffusion_polygons = sorted(merged_diffusion_polygons, key=lambda polygon: min(polygon.exterior.xy[1]),
                                 reverse=True)

        connection_polygons = polygons.get((self.connection_layer, 0), [])
        merged_connection_polygons = mergePolygons(connection_polygons)

        label_polygons = polygons.get((self.label_layer, 0), [])
        merged_label_polygons = mergePolygons(label_polygons)

        for label in self.label_list:
            x, y = label.position
            plt.scatter(x, y)
            plt.annotate(label.text, (x, y))

        for merged_polygon in merged_label_polygons:
            x, y = merged_polygon.exterior.xy
            plt.plot(x, y)

        for merged_polygon in merged_connection_polygons:
            x, y = merged_polygon.exterior.xy
            plt.plot(x, y)

       # for merged_polygon in sorted_diffusion_polygons:
        #    x, y = merged_polygon.exterior.xy
         #   plt.plot(x, y)

        for merged_polysilicon_polygon in sorted_polysilicon_polygons:
            x, y = merged_polysilicon_polygon.exterior.xy
            plt.plot(x, y)

        plt.title(self.gate_type)

        plt.show()

        final_shape = {}

        ### new code

        linked_list = []
        check_label_list = self.label_list
        # first loop to check if a poly is an input
        for polysilicon in merged_polysilicon_polygons:
            for connection in merged_connection_polygons:
                for metal in merged_label_polygons:
                    for label in check_label_list:
                        label_position = Point(label.position.tolist())
                        if polysilicon.intersects(connection) and metal.intersects(connection) and polysilicon.intersects(metal) and metal.contains(label_position):
                            linked_list.append(['polysilicon', polysilicon, label])
                            check_label_list.remove(label)

        # first loop to check if a metal is an output
        for metal in merged_label_polygons:
            for label in check_label_list:
                label_position = Point(label.position.tolist())
                if metal.contains(label_position):
                    linked_list.append(["metal", metal, label])
                    check_label_list.remove(label)

        # find vdd and vss

        for metal in merged_label_polygons:
            _, metal_y = metal.exterior.xy
            for y in metal_y:
                for label in check_label_list:
                    _, point_y = label.position
                    if y == point_y:
                        linked_list.append(["metal", metal, label])
                        print(label)
                        check_label_list.remove(label)


        for poly in linked_list:
            x, y = poly[1].exterior.xy
            plt.plot(x, y)
            x, y = poly[2].position
            plt.scatter(x, y)
            plt.annotate(poly[2].text, (x, y))


        plt.title("in and out")
        plt.show()





           # for poly in sorted_polysilicon_polygons:
            #    for label in self.label_list:
             #       for merged_label_polygon in merged_label_polygons:
              #          label_position = Point(label.position.tolist())
               #         if merged_label_polygon.contains(label_position):


        ## old code

        for i in range(len(sorted_diffusion_polygons)):
            key = "element_" + str(i)
            final_shape[key] = {}
            intersection_counter = 0

            for merged_polysilicon_polygon in sorted_polysilicon_polygons:
                if sorted_diffusion_polygons[i].intersects(merged_polysilicon_polygon):
                    intersection_polygons = sorted_diffusion_polygons[i].intersection(merged_polysilicon_polygon)

                    # init var to handle error
                    if hasattr(intersection_polygons, "geoms"):
                        for index, intersection_polygon in enumerate(intersection_polygons.geoms):
                            x, y = intersection_polygon.exterior.xy
                            ploysilicon_key = "poly_" + str(intersection_counter)
                            unique_coordinates = list(set(zip(x, y)))
                            final_shape[key][ploysilicon_key] = unique_coordinates
                            intersection_counter += 1
                    else:
                        x, y = intersection_polygons.exterior.xy
                        ploysilicon_key = "poly_" + str(intersection_counter)
                        unique_coordinates = list(set(zip(x, y)))
                        final_shape[key][ploysilicon_key] = unique_coordinates
                        intersection_counter += 1

            diff_coordinates_x, diff_coordinates_y = sorted_diffusion_polygons[i].exterior.xy
            diff_coordinates_list = list(set(zip(diff_coordinates_x, diff_coordinates_y)))
            extreme_left_diff, extreme_right_diff = find_extreme_points(diff_coordinates_list)

            poly_key_list = list(final_shape[key].keys())

            for j in range(len(poly_key_list) + 1):
                diffusion_key = "diff_" + str(j)
                if j == 0:
                    poly_left, poly_right = find_extreme_points(final_shape[key][poly_key_list[j]])
                    combined_points = extreme_left_diff + poly_left
                elif j == len(poly_key_list):
                    poly_left, poly_right = find_extreme_points(final_shape[key][poly_key_list[j - 1]])
                    combined_points = poly_right + extreme_right_diff
                else:
                    poly_left, poly_right = find_extreme_points(final_shape[key][poly_key_list[j]])
                    poly_left_before, poly_right_before = find_extreme_points(
                        final_shape[key][poly_key_list[j - 1]])
                    combined_points = poly_right_before + poly_left

                unique_y_values = set(point[1] for point in combined_points)
                num_unique_y = len(unique_y_values)

                if num_unique_y > 2:
                    min_x = min(point[0] for point in combined_points)
                    max_x = max(point[0] for point in combined_points)
                    min_y = min(point[1] for point in combined_points)
                    max_y = max(point[1] for point in combined_points)

                    filtered_points = [
                        point for point in diff_coordinates_list
                        if min_x <= point[0] <= max_x and min_y <= point[1] <= max_y
                    ]
                    existing_y_coords_combined = set(point[1] for point in combined_points)
                    existing_y_coords_filtered = set(point[1] for point in filtered_points)
                    missing_y = existing_y_coords_combined - existing_y_coords_filtered

                    if missing_y:
                        missing_x = set(point[0] for point in filtered_points)
                        new_point = list(set(zip(missing_x, missing_y)))
                        combined_points = combined_points + new_point

                    combined_points = combined_points + filtered_points

                final_shape[key][diffusion_key] = combined_points

        sorted_dict = sort_dict_alternating_keys(final_shape)

        with open('resources/data.json', 'w') as json_file:
            json.dump(sorted_dict, json_file, indent=4)

        state = self.convertTruthtableToStates()

        #plotShape(sorted_dict, state, self.gate_type)

    def convertTruthtableToStates(self):
        print(self.truthtable)
        return [1, 0, 1, 0, 1, 0, 1]
