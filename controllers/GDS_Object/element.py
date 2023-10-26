class Element:
    """
    Represents an element object found in a GDS file shapes.

    Attributes:
        name (str): The name associated with the element.
        coordinates (tuple: 2): The x and y coordinates associated with the element.

    Methods:
        __init__(name, coordinates):
            Initializes a new instance of the Element class with the provided name and coordinates.

    Usage:
        # Creating an instance of the Element class
        my_element = Element('ExampleElement', polygon.exterior.xy)
"""
    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates
