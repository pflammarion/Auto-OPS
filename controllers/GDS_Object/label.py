from controllers.GDS_Object.element import Element


class Label(Element):
    def __init__(self, name, coordinate):
        super().__init__(name, coordinate)
        