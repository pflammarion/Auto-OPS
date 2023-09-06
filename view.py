import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit
import pyqtgraph as pg
import controller


class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_view = pg.ImageView()
	# TODO add default values for the user
        self.info_input_tech = QLineEdit(self)
        self.info_input_voltage = QLineEdit(self)
        self.main_window = QMainWindow()
        self.controller = controller.Controller(self)
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
        info_label_tech = QLabel("Technology", self)
        info_label_voltage = QLabel("Voltage", self)
        info_button = QPushButton("Submit values", self)
        info_button.clicked.connect(self.controller.update_physics_values)

        input_layout = QGridLayout(info_widget)
        input_layout.addWidget(info_label, 0, 0)
        input_layout.addWidget(info_label_tech, 1, 0)
        input_layout.addWidget(self.info_input_tech, 2, 0)
        input_layout.addWidget(info_label_voltage, 1, 1)
        input_layout.addWidget(self.info_input_voltage, 2, 1)
        input_layout.addWidget(info_button, 3, 0)

        # Creating the selector widget

        selector_widget = QWidget()
        selector_labelx = QLabel("x: ", self)
        selector_input1 = QLineEdit(self)
        selector_labely = QLabel("y: ", self)
        selector_input2 = QLineEdit(self)
        selector_button = QPushButton("change position", self)

        selector_layout = QGridLayout(selector_widget)
        selector_layout.addWidget(selector_labelx, 0, 0)
        selector_layout.addWidget(selector_input1, 0, 1)
        selector_layout.addWidget(selector_labely, 1, 0)
        selector_layout.addWidget(selector_input2, 1, 1)
        selector_layout.addWidget(selector_button, 2, 1)

        # Creating the main widget

        main_btn_container_widget = QWidget()
        main_btn_container_layout = QGridLayout(main_btn_container_widget)

        main_button1 = QPushButton("Show original output", self)
        main_button2 = QPushButton("Calc RCV", self)
        main_button3 = QPushButton("EOFM", self)

        main_btn_container_layout.addWidget(main_button1, 0, 0)
        main_btn_container_layout.addWidget(main_button2, 0, 1)
        main_btn_container_layout.addWidget(main_button3, 0, 2)

        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        text_label = QLabel("RCV :", self)

        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)

        main_layout.addWidget(main_btn_container_widget, 0, 0)
        main_layout.addWidget(self.image_view, 1, 0)
        main_layout.addWidget(text_label, 2, 0)

        # Add all to the window layout

        layout.addWidget(button_widget, 0, 0)
        layout.addWidget(info_widget, 0, 1)
        layout.addWidget(selector_widget, 1, 0)
        layout.addWidget(main_widget, 1, 1)

    def display_image(self, image_matrix):
        # TODO find a nicer solution to display images
        image_matrix = np.rot90(image_matrix)
        self.image_view.setImage(image_matrix)

    def get_input_tech(self):
        return self.info_input_tech.text()

    def get_input_voltage(self):
        return self.info_input_voltage.text()
