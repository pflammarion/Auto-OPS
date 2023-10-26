from enum import Enum

class ShapeType(Enum):
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
