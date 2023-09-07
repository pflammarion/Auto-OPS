import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit
import pyqtgraph as pg
import controller


class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_view = pg.ImageView()
        self.rcv_value = QLabel("", self)
        self.controller = controller.Controller(self)

        self.info_input_Kn = QLineEdit(self)
        self.info_input_Kp = QLineEdit(self)
        self.info_input_alpha = QLineEdit(self)
        self.info_input_beta = QLineEdit(self)
        self.info_input_Pl = QLineEdit(self)
        self.info_input_voltage = QLineEdit(self)
        self.info_input_voltage.setText(str(self.controller.voltage_value))

        self.selector_input_x = None
        self.selector_input_y = None

        self.selector_input_lam = None
        self.selector_input_NA = None

        self.main_window = QMainWindow()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("CMOS-INV-GUI")
        self.setStyleSheet(open('style.css').read())
        self.setGeometry(0, 0, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        # Creating the add widget

        button_widget = QWidget()
        button_add = QPushButton("Add png file", self)
        button_add.clicked.connect(self.controller.upload_image)

        button_layout = QVBoxLayout(button_widget)
        button_layout.addWidget(button_add)

        # Creating the info widget

        info_widget = QWidget()
        info_label = QLabel("Physics info:", self)
        info_label_Kn = QLabel("Kn", self)
        info_label_Kp = QLabel("Kp", self)
        info_label_alpha = QLabel("Alpha", self)
        info_label_beta = QLabel("Beta", self)
        info_label_Pl = QLabel("Pl", self)
        info_label_voltage = QLabel("Voltage", self)
        info_button = QPushButton("Submit values", self)
        info_button.clicked.connect(self.controller.update_physics_values)

        input_layout = QGridLayout(info_widget)
        input_layout.addWidget(info_label, 0, 0)
        input_layout.addWidget(info_label_Kn, 1, 0)
        input_layout.addWidget(self.info_input_Kn, 2, 0)
        input_layout.addWidget(info_label_alpha, 1, 1)
        input_layout.addWidget(self.info_input_alpha, 2, 1)
        input_layout.addWidget(info_label_Pl, 1, 2)
        input_layout.addWidget(self.info_input_Pl, 2, 2)
        input_layout.addWidget(info_label_Kp, 3, 0)
        input_layout.addWidget(self.info_input_Kp, 4, 0)
        input_layout.addWidget(info_label_beta, 3, 1)
        input_layout.addWidget(self.info_input_beta, 4, 1)
        input_layout.addWidget(info_label_voltage, 3, 2)
        input_layout.addWidget(self.info_input_voltage, 4, 2)
        input_layout.addWidget(info_button, 5, 0)

        # Creating the selector widget



        # Creating the main widget

        main_btn_container_widget = QWidget()
        main_btn_container_layout = QGridLayout(main_btn_container_widget)

        main_button1 = QPushButton("Show original output", self)
        main_button1.clicked.connect(self.controller.print_original_image)
        main_button2 = QPushButton("Calc RCV", self)
        main_button2.clicked.connect(lambda: self.set_mode(layout, 1))
        main_button2.clicked.connect(self.controller.print_rcv_image)
        main_button3 = QPushButton("EOFM", self)
        main_button3.clicked.connect(lambda: self.set_mode(layout, 2))
        main_button3.clicked.connect(self.controller.print_EOFM_image)

        main_btn_container_layout.addWidget(main_button1, 0, 0)
        main_btn_container_layout.addWidget(main_button2, 0, 1)
        main_btn_container_layout.addWidget(main_button3, 0, 2)

        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)

        main_layout.addWidget(main_btn_container_widget, 0, 0)
        main_layout.addWidget(self.image_view, 1, 0)
        main_layout.addWidget(self.rcv_value, 2, 0)

        # Add all to the window layout

        layout.addWidget(button_widget, 0, 0)
        layout.addWidget(info_widget, 0, 1)
        layout.addWidget(main_widget, 1, 1)

    def set_mode(self, layout, mode=0):
        # Clear the layout if there's already a widget at position (1, 0)
        if layout.itemAtPosition(1, 0) is not None:
            item = layout.itemAtPosition(1, 0)
            widget_to_remove = item.widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        if mode == 1:
            widget = self.init_rcv_widget()
            layout.addWidget(widget, 1, 0)


    def display_image(self, image_matrix):
        # TODO find a nicer solution to display images
        image_matrix = np.rot90(image_matrix)
        self.image_view.setImage(image_matrix)
        self.rcv_value.setText("")


    def get_input_voltage(self):
        return self.info_input_voltage.text()

    def update_rcv_value(self, text):
        self.rcv_value.setText(text)

    def get_input_x(self):
        return self.selector_input_x.text()

    def get_input_y(self):
        return self.selector_input_y.text()

    def init_rcv_widget(self) -> QWidget:
        selector_widget = QWidget()
        selector_label_x = QLabel("x: ", self)
        selector_label_y = QLabel("y: ", self)

        self.selector_input_x = QLineEdit(self)
        self.selector_input_x.setText(str(self.controller.x_position))
        self.selector_input_y = QLineEdit(self)
        self.selector_input_y.setText(str(self.controller.y_position))

        selector_button = QPushButton("change position", self)
        selector_button.clicked.connect(self.controller.update_rcv_position)

        selector_layout = QGridLayout(selector_widget)
        selector_layout.addWidget(selector_label_x, 0, 0)
        selector_layout.addWidget(self.selector_input_x, 0, 1)
        selector_layout.addWidget(selector_label_y, 1, 0)
        selector_layout.addWidget(self.selector_input_y, 1, 1)
        selector_layout.addWidget(selector_button, 2, 1)

        return selector_widget


