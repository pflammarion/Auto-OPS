class Attribute:
    """
    Represents a shape attribute with specific characteristics.

    Attributes:
        shape_type (ShapeType): The type of shape associated with the attribute.
        label (str): A label that can be assigned to the attribute (optional).
        state (bool): The state of the attribute, which can represent various conditions or statuses (optional).

    Methods:
        __init__(shape_type, label=None, state=None):
            Initializes a new instance of the Attribute class with the provided parameters.

    Usage:
        # Creating an instance of the Attribute class
        my_attribute = Attribute(ShapeType.METAL', label='A1', state=True)
    """

    def __init__(self, shape_type, label=None, state=None):
        self.shape_type = shape_type
        self.label = label
        self.state = state
