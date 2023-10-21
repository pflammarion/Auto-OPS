class Zone:
    def __init__(self, shape_type, coordinates):
        self.shape_type = shape_type
        self.coordinates = coordinates
        self.state = 0
        self.connected_to = None

    def set_state(self, state):
        self.state = state

    def set_connected_to(self, shape):
        self.connected_to = shape

