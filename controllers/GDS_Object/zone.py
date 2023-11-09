import math
from typing import Tuple


class Zone:
    """
    To create a reflection diffusion instance.

    Attributes:
        shape_type (ShapeType): The type of shape associated with the Zone object.
        coordinates (list[tuple(float), tuple(float)]): A polygone shape associated with the diffusion.
        connected_to (Shape): A list that holds the zones object associated with the diffusion.

    Methods:
        __init__(shape_type, coordinates: optional, connected_to: optional):
            Initializes a new instance of the Zone class with the provided:
                - type (ShapeType),
                - coordinates (list[tuple(float), tuple(float)]),
                - connected element (Shape).

        set_state(state):
            Append a founded state to the zone.

        set_connected_to(shape):
            Append the connected element(Shape) to this zone instance

        get_min_x_coord():
            Get the x minimum (float) of the coordinates of this instance.

        get_max_x_coord():
            Get the x maximum (float) of the coordinates of this instance.

        get_right_points_coords():
             Get the x maximum coordinates (list[(float, float)]) of the coordinates of this instance.

        get_left_points_coords():
            Get the x minimum coordinates (list[(float, float)]) of the coordinates of this instance.

        set_coordinates_from_list(coords):
            Set the zone coordinates from the coords (list[(float, float)]).
            Sort the coordinates clockwise to store them for the reflection output.

    Usage:
        # Creating an instance of the Diffusion class
        my_zone = Zone(ShapeType.POLYSILICON, inter.exterior.xy, element))
    """
    def __init__(self, shape_type, coordinates=None, connected_to=None):
        self.name = ""
        self.shape_type = shape_type
        self.coordinates = coordinates
        self.state = None
        self.connected_to = connected_to
        self.wire = False
        self.diffusion = None
        self.next_zone_list = set()
        self.previous_zone_list = set()

    def set_state(self, state) -> None:
        if state is True or state == 1:
            self.state = 1
        elif state is False or state == 0:
            self.state = 0
        else:
            raise ValueError("Invalid state input. Please provide a boolean or 0/1.")

    def set_diffusion(self, diffusion) -> None:
        self.diffusion = diffusion

    def add_next_zone(self, zone):
        self.next_zone_list.add(zone)

    def add_previous_zone(self, zone):
        self.previous_zone_list.add(zone)


    def set_connected_to(self, shape) -> None:
        self.connected_to = shape

    def get_min_x_coord(self) -> float:
        x_values = self.coordinates[0]
        min_x = min(x_values)
        return min_x

    def get_max_x_coord(self) -> float:
        x_values = self.coordinates[0]
        max_x = max(x_values)
        return max_x

    def get_right_points_coords(self) -> list[(float, float)]:
        x_coords = list(self.coordinates[0])
        y_coords = list(self.coordinates[1])
        max_x = max(x_coords)
        right_points = [(x, y) for x, y in zip(x_coords, y_coords) if x == max_x]
        return right_points

    def get_left_points_coords(self) -> list[(float, float)]:
        x_coords = list(self.coordinates[0])
        y_coords = list(self.coordinates[1])
        min_x = min(x_coords)
        left_points = [(x, y) for x, y in zip(x_coords, y_coords) if x == min_x]
        return left_points

    def set_coordinates_from_list(self, coords) -> None:
        unique_coords = list(set(coords))
        if len(unique_coords) > 4 and self.coordinates is not None:
            def sort_points_L_shape(points) -> list[[float, float]]:
                sorted_points = []
                start_point = points[0]
                sorted_points.append(start_point)
                previous_way = "x"
                while len(sorted_points) != len(points):
                    start_point, sorted_points, previous_way = find_next_point(start_point, points, sorted_points,
                                                                               previous_way)
                return sorted_points

            def find_closest_point(start_point, next_point_list, previous_way) -> [float, float]:
                min_distance = float('inf')
                new_start_point = None
                for point in next_point_list:
                    if previous_way == "x":
                        distance = abs(point[0] - start_point[0])
                    else:
                        distance = abs(point[1] - start_point[1])

                    if distance < min_distance:
                        min_distance = distance
                        new_start_point = point
                if new_start_point is None:
                    Exception("This program is no working for this diffusion shape")

                return new_start_point

            def find_next_point(start_point, point_list, sorted_points, previous_way) \
                    -> Tuple[list[float, float], list, str]:

                next_point_list = []
                for point in point_list:
                    if ((point[0] == start_point[0] and previous_way == "y") or
                        (point[1] == start_point[1]) and previous_way == "x") \
                            and point not in sorted_points:
                        next_point_list.append(point)

                if len(next_point_list) == 1:
                    new_start_point = next_point_list[0]
                else:
                    new_start_point = find_closest_point(start_point, next_point_list, previous_way)

                if new_start_point is not None:
                    sorted_points.append(new_start_point)

                if previous_way == "x":
                    previous_way = "y"
                else:
                    previous_way = "x"

                if new_start_point is None:
                    raise Exception("Error while sorting coordinates in reflection zone" + str(point_list))

                return new_start_point, sorted_points, previous_way

            # Coordinates sorting in y position before performing L shape algo
            sorted_coords = sorted(unique_coords, key=lambda p: p[1])

            sorted_coords = sort_points_L_shape(sorted_coords)

        else:
            # Sort them clockwise and remove duplicated points
            center_x = sum(x for x, y in unique_coords) / len(unique_coords)
            center_y = sum(y for x, y in unique_coords) / len(unique_coords)

            def calculate_angle(point):
                x, y = point
                return math.atan2(y - center_y, x - center_x)

            sorted_coords = sorted(unique_coords, key=calculate_angle)

        zip_unique_coords = zip(*sorted_coords)
        self.coordinates = list(zip_unique_coords)
