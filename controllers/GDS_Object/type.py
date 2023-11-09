from enum import Enum


class ShapeType(Enum):
    """
    Represents different types of shapes used in a specific context.

    Attributes:
        DIFFUSION (int): Represents a diffusion shape.
        NWELL (int): Represents an N-well shape.
        POLYSILICON (int): Represents a polysilicon shape.
        VIA (int): Represents a via shape.
        METAL (int): Represents a metal shape.
        INPUT (int): Represents an input shape.
        OUTPUT (int): Represents an output shape.
        VDD (int): Represents a VDD shape.
        VSS (int): Represents a VSS shape.
        WIRE (int): Represents a wire shape.
        PMOS (int): Represents a PMOS shape.
        NMOS (int): Represents an NMOS shape.

    Usage:
        # Accessing enum values
        shape_type = ShapeType.DIFFUSION
        print(shape_type.value)  # Output: 0
    """

    DIFFUSION = 0
    NWELL = 1
    POLYSILICON = 2
    VIA = 3
    METAL = 4
    INPUT = 10
    OUTPUT = 11
    VDD = 12
    VSS = 13
    WIRE = 14
    PMOS = 20
    NMOS = 21
