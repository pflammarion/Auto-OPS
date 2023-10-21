from controllers.GDS_Object.element import Element
from controllers.GDS_Object.type import ShapeType


class Shape(Element):
    def __init__(self, name, coordinate, layer, shape_type=None, attribute=None):
        super().__init__(name, coordinate)
        self.layer = layer
        self.shape_type = shape_type
        self.attribute = attribute

    def set_shape_type(self, layer_list):
        type_index = layer_list.index(self.layer)
        if type_index:
            self.shape_type = ShapeType(type_index)


