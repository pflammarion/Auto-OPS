from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QWidget, QLabel, QHBoxLayout, QCheckBox, QGridLayout


class GateLayout(QWidget):
    def __init__(self, value_dict):
        super().__init__()

        self.info_button_column_voltage = None
        self.layout = None
        self.widget = None
        self.submit_btn = None

        self.info_input_Kn = QLineEdit(self)
        self.info_input_Kp = QLineEdit(self)
        self.info_input_beta = QLineEdit(self)
        self.info_input_Pl = QLineEdit(self)
        self.info_input_voltage = QLineEdit(self)
        self.noise_percentage = QLineEdit(self)

        self.init_ui(value_dict)

    def init_ui(self, value_dict):

        info_widget = QWidget()

        info_label_Kn = QLabel("Kn:")
        self.info_input_Kn.setPlaceholderText(str(value_dict['Kn_value']))

        info_label_Kp = QLabel("Kp:")
        self.info_input_Kp.setPlaceholderText(str(value_dict['Kp_value']))

        info_label_beta = QLabel("Beta:")
        self.info_input_beta.setPlaceholderText(str(value_dict['beta_value']))

        info_label_Pl = QLabel("P_L:")
        self.info_input_Pl.setPlaceholderText(str(value_dict['Pl_value']))

        info_label_voltage = QLabel("Voltage:")
        self.info_input_voltage.setPlaceholderText(str(value_dict['voltage_value']))

        label_noise_percentage = QLabel("Noise (%):")
        self.noise_percentage.setPlaceholderText(str(value_dict['noise_percentage']))

        self.submit_btn = QPushButton("Submit values")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.info_button_column_voltage = QPushButton("Voltage columns")
        self.info_button_column_voltage.setCursor(Qt.CursorShape.PointingHandCursor)

        # Creating layouts
        input_layout = QGridLayout(info_widget)

        # Creating QHBoxLayouts for each line
        line1 = QHBoxLayout()
        line1.addWidget(info_label_Kn)
        line1.addWidget(self.info_input_Kn)

        line2 = QHBoxLayout()
        line2.addWidget(info_label_Kp)
        line2.addWidget(self.info_input_Kp)

        line3 = QHBoxLayout()
        line3.addWidget(info_label_beta)
        line3.addWidget(self.info_input_beta)

        line4 = QHBoxLayout()
        line4.addWidget(info_label_Pl)
        line4.addWidget(self.info_input_Pl)

        line5_widget = QWidget()
        line5 = QGridLayout(line5_widget)
        line5.setContentsMargins(0, 0, 0, 0)
        line5.addWidget(info_label_voltage, 0, 0)
        line5.addWidget(self.info_input_voltage, 0, 1)

        line5_btn = self.info_button_column_voltage
        line5_btn.hide()

        line6_widget = QWidget()
        line6 = QGridLayout(line6_widget)
        line6.setContentsMargins(0, 0, 0, 0)
        line6.addWidget(label_noise_percentage, 0, 0)
        line6.addWidget(self.noise_percentage, 0, 1)
        line6_widget.hide()

        # Adding the lines to the main layout
        input_layout.addLayout(line1, 0, 0)
        input_layout.addLayout(line2, 1, 0)
        input_layout.addLayout(line3, 2, 0)
        input_layout.addLayout(line4, 3, 0)
        input_layout.addWidget(line5_widget, 4, 0)
        input_layout.addWidget(line5_btn, 5, 0)

        input_layout.addWidget(line6_widget, 6, 0)
        input_layout.addWidget(self.submit_btn, 7, 0)

        input_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout.setSpacing(20)

        self.widget = info_widget
        self.layout = input_layout

        self.update_inputs(value_dict)

    def update_inputs(self, value_dict):
        self.info_input_Kn.setText(str(value_dict['Kn_value']))
        self.info_input_Kp.setText(str(value_dict['Kp_value']))
        self.info_input_beta.setText(str(value_dict['beta_value']))
        self.info_input_Pl.setText(str(value_dict['Pl_value']))
        self.info_input_voltage.setText(str(value_dict['voltage_value']))
        self.noise_percentage.setText(str(value_dict['noise_percentage']))

    def get_input_values(self):
        data = {'Kn_value': self.info_input_Kn.text(),
                'Kp_value': self.info_input_Kp.text(),
                'beta_value': self.info_input_beta.text(),
                'Pl_value': self.info_input_Pl.text(),
                'voltage_value': self.info_input_voltage.text(),
                'noise_percentage': self.noise_percentage.text(),
                }
        return data
