import gdspy
import matplotlib.pyplot as plt
import numpy as np
import json

from shapely.geometry import Polygon
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
    x, y = zip(*coordinates)

    centroid_x = sum(x) / len(x)
    centroid_y = sum(y) / len(y)

    polar_angles = [np.arctan2(yi - centroid_y, xi - centroid_x) for xi, yi in coordinates]

    sorted_points = [point for _, point in sorted(zip(polar_angles, coordinates))]

    return sorted_points


def plotShape(data, state):
    fig, ax = plt.subplots()

    point_number = 1
    counter = 0

    # Iterate through the sub-dictionaries ('top' and 'bottom')
    for key, sub_dict in data.items():
        # Iterate through the sub-dictionary items ('diff_1', 'diff_2', 'poly')
        for sub_key, coordinates in sub_dict.items():
            sorted_points = sortPointsClockwise(coordinates)
            x, y = zip(*sorted_points)

            ax.scatter(x, y, label=f'{key} - {sub_key}', marker='o')

            for xi, yi in zip(x, y):
                ax.annotate(str(point_number), (xi, yi), textcoords="offset points", xytext=(0, 10), ha='center')
                point_number += 1

            color = 0
            if counter < len(state):
                color = state[counter]

            if color == 1:
                ax.fill_between(x, y, facecolor='white', alpha=0.2)
            elif color == 0:
                ax.fill_between(x, y, facecolor='black', alpha=0.2)

            counter += 1

    ax.set_xlabel('X-coordinate')
    ax.set_ylabel('Y-coordinate')
    # ax.legend()

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
        state (list): The state of each part of the gate of diffusion and polysilicon from
        left to right and then from top to bottom.

    Attributes:
        gds (str): The GDS file path or name.
        gate_type (str): The name of the gate in the gds file in the Cells' list.
        diffusion_layer (int): The number affiliated to the layer of the n and p diffusion.
        polysilicon_layer (int): The number affiliated to the layer of the polysilicon.
        positions (list): A list containing the X and Y coordinates of the drawing's position.
        state (list): The state or status of the drawing.

    Example:
        To create a GdsDrawing instance:

        >>> drawing = GdsDrawing("example.gds", "INV_X1", 1, 9, [10, 20], [0, 1, 0, 1, 0, 1])

    This class draw over a GDS input the optical state of each gate depending on the position and gates states.
    """

    def __init__(self, gds, gate_type, diffusion_layer, polysilicon_layer, positions, state):
        self.gds = gds
        self.gate_type = gate_type
        self.diffusion_layer = diffusion_layer
        self.polysilicon_layer = polysilicon_layer
        self.positions = positions
        self.state = state

        self.main()

    def main(self):
        lib = gdspy.GdsLibrary()
        lib.read_gds(self.gds)
        cell = lib.cells[self.gate_type]

        polygons = cell.get_polygons(by_spec=True)

        # TODO check about the polygons (layers) selection for gds files (idem for diff)
        polysilicon_polygon = polygons.get((self.polysilicon_layer, 0), [])

        # find the rectangle
        merged_polysilicon_polygon = mergePolygons(polysilicon_polygon)[0]

        x_poly, y_poly = merged_polysilicon_polygon.exterior.xy

        min_y_poly = min(y_poly)
        max_y_poly = max(y_poly)

        diffusion_polygons = polygons.get((self.diffusion_layer, 0), [])

        filtered_diffusion_polygons = [polygon for polygon in diffusion_polygons if
                                       all(min_y_poly <= y <= max_y_poly for _, y in polygon)]
        merged_diffusion_polygons = mergePolygons(filtered_diffusion_polygons)
        sorted_polygons = sorted(merged_diffusion_polygons, key=lambda polygon: min(polygon.exterior.xy[1]),
                                 reverse=True)

        for merged_polygon in sorted_polygons:
            x, y = merged_polygon.exterior.xy
            plt.plot(x, y)

        plt.plot(x_poly, y_poly)

        plt.show()

        final_shape = {}

        for i in range(len(sorted_polygons)):
            key = "element_" + str(i)
            final_shape[key] = {}

            if sorted_polygons[i].intersects(merged_polysilicon_polygon):
                intersection_polygons = sorted_polygons[i].intersection(merged_polysilicon_polygon)

                # init var to handle error
                if hasattr(intersection_polygons, "geoms"):
                    for index, intersection_polygon in enumerate(intersection_polygons.geoms):
                        x, y = intersection_polygon.exterior.xy
                        ploysilicon_key = "poly_" + str(index)
                        unique_coordinates = list(set(zip(x, y)))
                        final_shape[key][ploysilicon_key] = unique_coordinates
                else:
                    x, y = intersection_polygons.exterior.xy
                    ploysilicon_key = "poly_0"
                    unique_coordinates = list(set(zip(x, y)))
                    final_shape[key][ploysilicon_key] = unique_coordinates




                diff_coordinates_x, diff_coordinates_y = sorted_polygons[i].exterior.xy
                extreme_left_diff, extreme_right_diff = find_extreme_points(
                    list(set(zip(diff_coordinates_x, diff_coordinates_y))))

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

                    final_shape[key][diffusion_key] = combined_points

        sorted_dict = sort_dict_alternating_keys(final_shape)

        with open('resources/data.json', 'w') as json_file:
            json.dump(sorted_dict, json_file, indent=4)

        plotShape(sorted_dict, self.state)
