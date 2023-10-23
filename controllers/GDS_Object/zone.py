import math


class Zone:
    def __init__(self, shape_type, coordinates=None, connected_to=None):
        self.shape_type = shape_type
        self.coordinates = coordinates
        self.state = 0
        self.connected_to = connected_to

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
        # Sort them clockwise and remove duplicated points
        center_x = sum(x for x, y in coords) / len(coords)
        center_y = sum(y for x, y in coords) / len(coords)

        def calculate_angle(point):
            x, y = point
            return math.atan2(y - center_y, x - center_x)

        sorted_coords = sorted(coords, key=calculate_angle)
        zip_unique_coords = zip(*sorted_coords)
        self.coordinates = list(zip_unique_coords)


