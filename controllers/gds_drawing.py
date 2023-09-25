class GdsDrawing:
    """
    Represents a drawing element in a GDS (Graphics Data System) layout.

    Args:
        gds (str): The GDS file path or name.
        gate_type (str): The name of the gate in the gds file in the Cells' list.
        diffusion_layer (int): The number affiliated to the layer of the n and p diffusion.
        polysilicon_layer (int): The number affiliated to the layer of the polysilicon.
        positions (list): A list containing the X and Y coordinates of the drawing's position.
        state (list): The state of each part of the gate of diffusion and polysilicon from
        left to right and then from top to bottom.

    Attributes:
        gds (str): The GDS file path or name.
        gate_type (str): The name of the gate in the gds file in the Cells' list.
        diffusion_layer (int): The number affiliated to the layer of the n and p diffusion.
        polysilicon_layer (int): The number affiliated to the layer of the polysilicon.
        positions (list): A list containing the X and Y coordinates of the drawing's position.
        state (list): The state or status of the drawing.

    Example:
        To create a GdsDrawing instance:

        >>> drawing = GdsDrawing("example.gds", "INV_X1", 1, 9, [10, 20], [0, 1, 0, 1, 0, 1])

    This class draw over a GDS input the optical state of each gate depending on the position and gates states.
    """
    def __init__(self, gds, gate_type, diffusion_layer, polysilicon_layer, positions, state):
        self.gds = gds
        self.gate_type = gate_type
        self.diffusion_layer = diffusion_layer
        self.polysilicon_layer = polysilicon_layer
        self.positions = positions
        self.state = state

