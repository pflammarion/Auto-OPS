from controllers.GDS_Object.zone import Zone


class Diffusion:

    """
    To create a reflection diffusion instance.

    Attributes:
        name (str): The name associated with the diffusion.
        polygon (Polygon): A polygone shape associated with the diffusion.
        zone_list (list[Zone]): A list that holds the zones object associated with the diffusion.
        shape_type (ShapeType): The type of shape associated with the diffusion.

    Methods:
        __init__(polygon):
            Initializes a new instance of the Diffusion class with the provided polygon(Polygon).

        set_zone(zone):
            Append to the instance zone list a new zone(Zone) object.

        get_right_points_coords():
            Get the x maximum coordinates (list[(int, int)]) of the polygon of this instance.

        get_left_points_coords():
            Get the x minimum coordinates (list[(int, int)]) of the polygon of this instance.

        get_zone_by_index(index):
            Get a zone object by index(int) from the zone list of this instance.

        set_type(shape_type):
            Set the type(ShapeType) of shape to this instance.

    Usage:
        # Creating an instance of the Diffusion class
        my_diffusion = Diffusion(my_polygon)
    """

    def __init__(self, polygon):
        self.name = ""
        self.polygon = polygon
        self.zone_list = []
        self.shape_type = None

    def set_zone(self, zone):
        self.zone_list.append(zone)

    def get_diff_width(self) -> int:
        x_coords = [point[0] for point in self.polygon.exterior.coords]
        return max(x_coords) + min(x_coords)


    def get_right_points_coords(self) -> list[(int, int)]:
        x_coords = [point[0] for point in self.polygon.exterior.coords]
        max_x = max(x_coords)
        right_points = [(x, y) for x, y in self.polygon.exterior.coords if x == max_x]
        return right_points

    def get_left_points_coords(self) -> list[(int, int)]:
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
