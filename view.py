from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit

import controller


class View(QMainWindow):
    def __init__(self):
        super().__init__()
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
        info_label = QLabel("Physics info", self)
        info_input1 = QLineEdit(self)
        info_input2 = QLineEdit(self)

        input_layout = QGridLayout(info_widget)
        input_layout.addWidget(info_label, 0, 0)
        input_layout.addWidget(info_input1, 1, 0)
        input_layout.addWidget(info_input2, 1, 1)

        # Creating the selector widget

        selector_widget = QWidget()
        selector_input1 = QLineEdit(self)
        selector_input2 = QLineEdit(self)
        selector_button = QPushButton("Selector Button", self)

        selector_layout = QVBoxLayout(selector_widget)
        selector_layout.addWidget(selector_input1)
        selector_layout.addWidget(selector_input2)
        selector_layout.addWidget(selector_button)

        # Creating the main widget

        main_btn_container_widget = QWidget()
        main_btn_container_layout = QGridLayout(main_btn_container_widget)

        main_button1 = QPushButton("Button 1", self)
        main_button2 = QPushButton("Button 2", self)
        main_button3 = QPushButton("Button 3", self)
        main_button4 = QPushButton("Button 4", self)

        main_btn_container_layout.addWidget(main_button1, 0, 0)
        main_btn_container_layout.addWidget(main_button2, 0, 1)
        main_btn_container_layout.addWidget(main_button3, 0, 2)
        main_btn_container_layout.addWidget(main_button4, 0, 3)

        image_label = QLabel()
        image_label.setFixedSize(400, 400)
        image = QPixmap('./resources/image.jpg')
        image = image.scaled(image_label.size())
        image_label.setPixmap(image)

        text_label = QLabel("RCV :", self)

        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)

        main_layout.addWidget(main_btn_container_widget, 0, 0)
        main_layout.addWidget(image_label, 1, 0)
        main_layout.addWidget(text_label, 2, 0)

        # Add all to the window layout

        layout.addWidget(button_widget, 0, 0)
        layout.addWidget(info_widget, 0, 1)
        layout.addWidget(selector_widget, 1, 0)
        layout.addWidget(main_widget, 1, 1)

