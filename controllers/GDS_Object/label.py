from controllers.GDS_Object.element import Element


class Label(Element):
    """
    Represents a label that is a specific type of element.

    Attributes:
        Inherits attributes from the Element class.

    Methods:
        __init__(name, coordinate):
            Initializes a new instance of the Label class with the provided name and coordinate.

    Usage:
        # Creating an instance of the Label class
        my_label = Label('ExampleLabel', (x, y))
    """

    def __init__(self, name, coordinate):
        super().__init__(name, coordinate)
        