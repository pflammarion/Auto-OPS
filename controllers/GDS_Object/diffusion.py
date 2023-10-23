from controllers.GDS_Object.zone import Zone


class Diffusion:
    def __init__(self, polygon):
        self.name = ""
        self.polygon = polygon
        self.zone_list = []
        self.shape_type = None

    def set_zone(self, zone):
        self.zone_list.append(zone)

    def get_right_points_coords(self):
        x_coords = [point[0] for point in self.polygon.exterior.coords]
        max_x = max(x_coords)
        right_points = [(x, y) for x, y in self.polygon.exterior.coords if x == max_x]
        return right_points

    def get_left_points_coords(self):
        x_coords = [point[0] for point in self.polygon.exterior.coords]
        min_x = min(x_coords)
        left_points = [(x, y) for x, y in self.polygon.exterior.coords if x == min_x]
        return left_points

    def get_zone_by_index(self, index) -> Zone:
        if 0 <= index < len(self.zone_list):
            return self.zone_list[index]
        else:
            raise IndexError("Index out of range.")

    def set_type(self, shape_type):
        self.shape_type = shape_type
