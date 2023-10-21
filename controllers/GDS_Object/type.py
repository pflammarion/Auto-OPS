from enum import Enum

class ShapeType(Enum):
    DIFFUSION = 0
    POLYSILICON = 1
    VIA = 2
    METAL = 3
    INPUT = 10
    OUTPUT = 11
    VDD = 12
    VSS = 13
    ZONE = 20
