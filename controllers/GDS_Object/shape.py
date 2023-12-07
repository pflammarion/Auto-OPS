from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.element import Element
from controllers.GDS_Object.type import ShapeType


class Shape(Element):
    """
    Represents a shape that is a specific type of element.

    Attributes:
        Inherits attributes from the Element class.
        polygon (Polygon): A Polygon object associated with the shape.
        layer (int): The layer number associated with the shape.
        connection_list (list(Polygon)): A list of Polygon objects that holds connections associated with the shape.
        shape_type (ShapeType): The type of shape associated with the shape (optional).
        attribute (Attribute): The attribute associated with the shape (optional).

    Methods:
        __init__(name, polygon, coordinate, layer, shape_type=None, attribute=None):
            Initializes a new instance of the Shape class with the provided parameters.
        set_shape_type(layer_list):
            Sets the shape type based on the provided layer list.
        set_attribute(attribute):
            Sets the attribute associated with the shape.
        add_via(via):
            Adds a via to the connection list associated with the shape.

    Usage:
        # Creating an instance of the Shape class
        my_shape = Shape('ExampleShape', polygon, polygon.exterior.xy, [1, 5, 9, 10, 11])
        my_shape.set_shape_type([1, 5, 9, 10, 11])
        my_shape.set_attribute(Attribute(ShapeType.METAL', label='A1', state=True))
        my_shape.add_via(my_via_shape)
    """
    def __init__(self, name, polygon, coordinate, layer, shape_type=None, attribute=None):
        super().__init__(name, coordinate)
        self.polygon = polygon
        self.layer = layer
        self.connection_list = []
        self.shape_type = shape_type
        self.attribute = attribute
        self.layer_level = 0

    def set_shape_type(self, type_index) -> None:
        self.shape_type = ShapeType(type_index)

    def set_layer_level(self, layer_level) -> None:
        self.layer_level = layer_level

    def set_attribute(self, attribute) -> None:
        self.attribute = attribute

    def add_via(self, via) -> None:
        self.connection_list.append(via)



