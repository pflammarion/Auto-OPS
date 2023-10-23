import math


class Zone:
    def __init__(self, shape_type, coordinates=None, connected_to=None):
        self.shape_type = shape_type
        self.coordinates = coordinates
        self.state = 0
        self.connected_to = connected_to
        self.wire = False

    def set_state(self, state):
        if state == True or state == 1:
            self.state = 1
        elif state == False or state == 0:
            self.state = 0
        else:
            raise ValueError("Invalid state input. Please provide a boolean or 0/1.")

    def set_connected_to(self, shape):
        self.connected_to = shape

    def get_min_x_coord(self):
        x_values = self.coordinates[0]
        min_x = min(x_values)
        return min_x

    def get_max_x_coord(self):
        x_values = self.coordinates[0]
        max_x = max(x_values)
        return max_x

    def get_right_points_coords(self):
        x_coords = list(self.coordinates[0])
        y_coords = list(self.coordinates[1])
        max_x = max(x_coords)
        right_points = [(x, y) for x, y in zip(x_coords, y_coords) if x == max_x]
        return right_points

    def get_left_points_coords(self):
        x_coords = list(self.coordinates[0])
        y_coords = list(self.coordinates[1])
        min_x = min(x_coords)
        left_points = [(x, y) for x, y in zip(x_coords, y_coords) if x == min_x]
        return left_points

    def set_coordinates_from_list(self, coords):
        unique_coords = list(set(coords))
        if len(unique_coords) > 4 and self.coordinates is not None:
            def sort_points_L_shape(points):
                sorted_points = []
                start_point = points[0]
                sorted_points.append(start_point)
                while len(sorted_points) != len(points):
                    start_point, sorted_points = find_next_point(start_point, points, sorted_points)
                return sorted_points

            def find_next_point(start_point, point_list, sorted_points):
                for point in point_list:
                    if (point[0] == start_point[0] or point[1] == start_point[1]) and point not in sorted_points:
                        new_start_point = point
                        sorted_points.append(point)
                        return new_start_point, sorted_points

            sorted_coords = sort_points_L_shape(unique_coords)

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
