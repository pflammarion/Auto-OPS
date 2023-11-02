class Op:
    def __init__(self, cell_name, inputs, truthtable):
        self.name = cell_name
        self.inputs = inputs
        self.truthtable = truthtable
        self.via_element_list = []
        self.element_list = []
        self.reflection_list = []
