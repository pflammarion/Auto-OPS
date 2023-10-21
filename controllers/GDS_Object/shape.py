from controllers.GDS_Object.element import Element
from controllers.GDS_Object.type import ShapeType


class Shape(Element):
    def __init__(self, name, polygon, coordinate, layer, shape_type=None, attribute=None):
        super().__init__(name, coordinate)
        self.polygon = polygon
        self.layer = layer
        self.connection_list = []
        self.shape_type = shape_type
        self.attribute = attribute

    def set_shape_type(self, layer_list):
        type_index = layer_list.index(self.layer)
        if type_index is not None:
            self.shape_type = ShapeType(type_index)

    def set_attribute(self, attribute):
        self.attribute = attribute

    def add_via(self, via):
        self.connection_list.append(via.polygon)


