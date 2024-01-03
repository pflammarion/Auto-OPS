from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QListWidget, QPushButton, QWidget, QLabel, QHBoxLayout, QCheckBox


class LaserLayout(QWidget):
    def __init__(self, value_dict):
        super().__init__()

        self.layout = None
        self.widget = None
        self.submit_btn = None
        self.selector_input_confocal = None
        self.selector_input_NA = None
        self.selector_input_lam = None
        self.init_ui(value_dict)

    def init_ui(self, value_dict):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.selector_input_lam = QLineEdit(self)
        self.selector_input_lam.setText(str(value_dict['lam_value']))
        self.selector_input_lam.setPlaceholderText(str(value_dict['lam_value']))
        label_lam = QLabel("Lambda:")

        self.selector_input_NA = QLineEdit(self)
        self.selector_input_NA.setText(str(value_dict['NA_value']))
        self.selector_input_NA.setPlaceholderText(str(value_dict['NA_value']))
        label_NA = QLabel("NA:")

        self.selector_input_confocal = QCheckBox()
        self.selector_input_confocal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.selector_input_confocal.setChecked(bool(value_dict['is_confocal']))

        label_confocal = QLabel("Confocal")

        self.submit_btn = QPushButton("Submit values", self)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout_confocal = QHBoxLayout()
        layout_lam = QHBoxLayout()
        layout_NA = QHBoxLayout()

        layout_confocal.addWidget(label_confocal)
        layout_confocal.addWidget(self.selector_input_confocal)

        layout_lam.addWidget(label_lam)
        layout_lam.addWidget(self.selector_input_lam)

        layout_NA.addWidget(label_NA)
        layout_NA.addWidget(self.selector_input_NA)

        layout.addLayout(layout_lam)
        layout.addLayout(layout_NA)
        layout.addLayout(layout_confocal)

        layout.addWidget(self.submit_btn)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        widget.setMaximumWidth(200)

        self.widget = widget
        self.layout = layout

    def update_inputs(self, value_dict):
        self.selector_input_lam.setText(str(value_dict['lam_value']))
        self.selector_input_NA.setText(str(value_dict['NA_value']))
        self.selector_input_confocal.setChecked(bool(value_dict['is_confocal']))

    def get_laser_values(self):
        data = {'lam_value': self.selector_input_lam.text(),
                'NA_value': self.selector_input_NA.text(),
                'is_confocal': self.selector_input_confocal.isChecked()
                }
        return data
