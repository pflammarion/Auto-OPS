from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QWidget, QLabel, QHBoxLayout, QCheckBox, QGridLayout


class LaserPositionLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.selector_button = None
        self.selector_input_y = None
        self.selector_input_x = None
        self.info_button_column_voltage = None
        self.layout = None
        self.widget = None
        self.submit_btn = None

    def init_ui(self, value_dict):

        selector_widget = QWidget()
        selector_label_x = QLabel("x:")
        selector_label_y = QLabel("y:")

        self.selector_input_x = QLineEdit()
        self.selector_input_x.setPlaceholderText(str(value_dict['input_x']))
        self.selector_input_y = QLineEdit(self)
        self.selector_input_y.setPlaceholderText(str(value_dict['input_y']))

        self.selector_button = QPushButton("Submit values", self)
        self.selector_button.setCursor(Qt.CursorShape.PointingHandCursor)

        selector_layout = QVBoxLayout(selector_widget)
        line1_layout = QHBoxLayout()
        line2_layout = QHBoxLayout()

        line1_layout.addWidget(selector_label_x)
        line1_layout.addWidget(self.selector_input_x)

        line2_layout.addWidget(selector_label_y)
        line2_layout.addWidget(self.selector_input_y)

        selector_layout.addLayout(line1_layout)
        selector_layout.addLayout(line2_layout)
        selector_layout.addWidget(self.selector_button)

        selector_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        selector_layout.setSpacing(20)

        selector_widget.setMaximumWidth(200)

        self.widget = selector_widget
        self.layout = selector_layout

        self.update_inputs(value_dict)

    def update_inputs(self, value_dict):
        self.selector_input_x.setText(str(value_dict['input_x']))
        self.selector_input_y.setText(str(value_dict['input_y']))

    def get_input_values(self):
        data = {'input_x': self.selector_input_x.text(),
                'input_y': self.selector_input_y.text(),
                }
        return data
