class Diffusion:
    def __init__(self, polygon):
        self.name = ""
        self.polygon = polygon
        self.zone_list = []

    def set_zone(self, zone):
        self.zone_list.append(zone)
