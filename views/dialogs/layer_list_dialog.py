from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout

class LayerSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select layer list")

        self.layers = {
            "Diffusion": QLineEdit(),
            "N_WELL": QLineEdit(),
            "Polysilicon": QLineEdit(),
            "Via": [],
            "Metal": [],
            "Labels": [],
        }

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)

        self.number_of_lines_input = QLineEdit()
        self.number_of_lines_input.setFixedWidth(100)
        self.number_of_lines_input.setPlaceholderText("Nbr layers")

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_input_lines)
        self.add_button.setFixedWidth(100)

        add_btn_container_layout = QHBoxLayout()
        add_btn_container_layout.addWidget(self.number_of_lines_input)
        add_btn_container_layout.addWidget(self.add_button)
        add_btn_container_layout.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()

        help_label = QLabel("Enter the following layers of the selected technology to define the GDS elements.\nEnter "
                            "numbers separated by a slash.\n\nD: 1/0, N: 5/0, P: 9/0, V1: 10/0, M1: 11/0, L1: 11/0")
        layout.addWidget(help_label)

        for layer_name, line_edit in self.layers.items():
            if isinstance(line_edit, QLineEdit):
                label = QLabel(layer_name)
                layout.addWidget(label)
                line_edit.setFixedWidth(100)
                layout.addWidget(line_edit)

        layout.addLayout(add_btn_container_layout)
        self.layer_layout = QVBoxLayout()
        layout.addLayout(self.layer_layout)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def create_layer_input_layout(self, layer_name):
        layer_layout = QHBoxLayout()
        label = QLabel(layer_name)
        layer_layout.addWidget(label)

        return layer_layout

    def add_input_lines(self):
        self.ok_button.setEnabled(True)

        self.clear_layout(self.layer_layout)

        num_lines_text = self.number_of_lines_input.text().strip()
        try:
            num_lines = int(num_lines_text)
        except ValueError:
            return

        for layer_name in ["Via", "Metal", "Labels"]:
            self.layers[layer_name] = []
            for _ in range(num_lines):
                line_edit = QLineEdit()
                self.layers[layer_name].append(line_edit)

        for layer_name, line_edit in self.layers.items():
            if layer_name in ["Via", "Metal", "Labels"]:
                layer_layout = self.create_layer_input_layout(layer_name)
                for line in line_edit:
                    line.setFixedWidth(100)
                    layer_layout.addWidget(line)
                self.layer_layout.addLayout(layer_layout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                self.clear_layout(item.layout())

    def get_selected_layers(self):
        layer_values = []
        for layer_name, line_edits in self.layers.items():
            if isinstance(line_edits, list):
                layer_input = [line_edit.text() for line_edit in line_edits if line_edit.text()]
                if layer_input:
                    tmp_list = []
                    for input_string in layer_input:
                        values_list = [int(value) for value in input_string.split('/')]
                        tmp_list.append(values_list)
                    layer_values.append(tmp_list)
            else:
                layer_input = line_edits.text()
                if layer_input:
                    values_list = [int(value) for value in layer_input.split('/')]
                    layer_values.append(values_list)

        return layer_values
