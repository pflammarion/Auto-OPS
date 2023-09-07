import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import controller


# TODO put lambda na and button in the same line and separate optional info in last box
# TODO try to add color into plot especially for lps
# TODO center plot in window

class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_view = pg.ImageItem(None)
        self.plot_widget = None
        self.controller = controller.Controller(self)

        self.info_input_Kn = QLineEdit(self)
        self.info_input_Kp = QLineEdit(self)
        self.info_input_beta = QLineEdit(self)
        self.info_input_Pl = QLineEdit(self)
        self.info_input_voltage = QLineEdit(self)

        #fill infos from controller
        self.info_input_Kn.setText(str(self.controller.Kn_value))
        self.info_input_Kp.setText(str(self.controller.Kp_value))
        self.info_input_beta.setText(str(self.controller.beta_value))
        self.info_input_Pl.setText(str(self.controller.Pl_value))
        self.info_input_voltage.setText(str(self.controller.voltage_value))

        self.selector_input_x = None
        self.selector_input_y = None

        self.selector_input_lam = None
        self.selector_input_NA = None
        self.selector_input_confocal = None

        self.second_image_view = pg.ImageItem(None)

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
        button_add_png = QPushButton("Add png file", self)
        button_add_png.clicked.connect(self.controller.upload_image)
        button_add_json = QPushButton("Add JSON config", self)
        button_add_json.clicked.connect(self.controller.upload_json)

        button_layout = QVBoxLayout(button_widget)
        button_layout.addWidget(button_add_png)
        button_layout.addWidget(button_add_json)

        # Creating the info widget

        info_widget = self.init_physic_info_widget()

        # Creating the side widget

        side_widget = QWidget()
        side_layout = QGridLayout(side_widget)

        laser_widget = self.init_laser_widget()

        side_layout.addWidget(laser_widget, 0, 0)

        # Creating the main widget

        main_widget = self.init_main_widget(side_layout)

        # Add all to the window layout

        layout.addWidget(button_widget, 0, 0)
        layout.addWidget(info_widget, 0, 1)
        layout.addWidget(side_widget, 1, 0)
        layout.addWidget(main_widget, 1, 1)

    def init_physic_info_widget(self) -> QWidget:
        info_widget = QWidget()
        info_label = QLabel("Physics info:", self)
        info_label_Kn = QLabel("Kn", self)
        info_label_Kp = QLabel("Kp", self)
        info_label_beta = QLabel("Beta", self)
        info_label_Pl = QLabel("P_L", self)
        info_label_voltage = QLabel("Voltage", self)
        info_button = QPushButton("Submit values", self)
        info_button.clicked.connect(self.controller.update_physics_values)

        # TODO set placeholder
        #self.info_input_Kn.setPlaceholderText(self.controller.Kn_value)

        input_layout = QGridLayout(info_widget)
        input_layout.addWidget(info_label, 0, 0)
        input_layout.addWidget(info_label_Kn, 1, 0)
        input_layout.addWidget(self.info_input_Kn, 2, 0)
        input_layout.addWidget(info_label_beta, 1, 1)
        input_layout.addWidget(self.info_input_beta, 2, 1)
        input_layout.addWidget(info_label_Pl, 1, 2)
        input_layout.addWidget(self.info_input_Pl, 2, 2)
        input_layout.addWidget(info_label_Kp, 3, 0)
        input_layout.addWidget(self.info_input_Kp, 4, 0)
        input_layout.addWidget(info_label_voltage, 3, 1)
        input_layout.addWidget(self.info_input_voltage, 4, 1)
        input_layout.addWidget(info_button, 4, 2)

        return info_widget

    def init_main_widget(self, side_layout) -> QWidget:
        main_btn_container_widget = QWidget()
        main_btn_container_layout = QGridLayout(main_btn_container_widget)

        main_button0 = QPushButton("Laser point spread", self)
        main_button0.clicked.connect(self.controller.print_psf)
        main_button0.clicked.connect(lambda: self.set_mode(side_layout, 0))
        main_button1 = QPushButton("Show original output", self)
        main_button1.clicked.connect(self.controller.print_original_image)
        main_button1.clicked.connect(lambda: self.set_mode(side_layout, 0))
        main_button2 = QPushButton("Calc RCV", self)
        main_button2.clicked.connect(lambda: self.set_mode(side_layout, 1))
        main_button2.clicked.connect(self.controller.print_rcv_image)
        main_button3 = QPushButton("EOFM", self)
        main_button3.clicked.connect(lambda: self.set_mode(side_layout, 2))
        main_button3.clicked.connect(self.controller.print_EOFM_image)

        main_btn_container_layout.addWidget(main_button0, 0, 0)
        main_btn_container_layout.addWidget(main_button1, 0, 1)
        main_btn_container_layout.addWidget(main_button2, 0, 2)
        main_btn_container_layout.addWidget(main_button3, 0, 3)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addItem(self.image_view)
        self.plot_widget.setFixedWidth(400)
        self.plot_widget.setFixedHeight(400)

        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)

        main_layout.addWidget(main_btn_container_widget, 0, 0)
        main_layout.addWidget(self.plot_widget, 1, 0)

        return main_widget

    def init_laser_widget(self) -> QWidget:
        widget = QWidget()
        layout = QGridLayout(widget)
        self.selector_input_lam = QLineEdit(self)
        self.selector_input_lam.setText(str(self.controller.lam_value))
        label_lam = QLabel("Lambda")
        self.selector_input_NA = QLineEdit(self)
        self.selector_input_NA.setText(str(self.controller.NA_value))
        label_NA = QLabel("NA")
        self.selector_input_confocal = QCheckBox()
        self.selector_input_confocal.setChecked(bool(self.controller.is_confocal))
        label_confocal = QLabel("Confocal")

        widget_confocal = QWidget()
        layout_confocal = QGridLayout(widget_confocal)
        layout_confocal.addWidget(label_confocal, 0, 0)
        layout_confocal.addWidget(self.selector_input_confocal, 0, 1)

        layout.addWidget(label_lam, 0, 0)
        layout.addWidget(self.selector_input_lam, 1, 0)
        layout.addWidget(label_NA, 0, 1)
        layout.addWidget(self.selector_input_NA, 1, 1)
        layout.addWidget(widget_confocal, 2, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        return widget

    def set_mode(self, side_layout, mode=0):
        # Clear the layout if there's already a widget at position (1, 0)
        if side_layout.itemAtPosition(1, 0) is not None:
            item = side_layout.itemAtPosition(1, 0)
            widget_to_remove = item.widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        if mode == 1:
            widget = self.init_rcv_widget()
            side_layout.addWidget(widget, 1, 0)

        elif mode == 2:
            second_plot_widget = pg.PlotWidget()
            second_plot_widget.addItem(self.second_image_view)
            second_plot_widget.setFixedWidth(200)
            second_plot_widget.setFixedHeight(200)
            side_layout.addWidget(second_plot_widget, 1, 0)

    def display_image(self, image_matrix, eofm=False):
        # TODO find a nicer solution to display images
        image_matrix = np.rot90(image_matrix)

        self.image_view.setImage(image_matrix)

        if eofm:
            seconde_image_matrix = np.abs(image_matrix)
            self.second_image_view.setImage(seconde_image_matrix)

    def get_input_Kn(self):
        return self.info_input_Kn.text()

    def get_input_Kp(self):
        return self.info_input_Kp.text()

    def get_input_beta(self):
        return self.info_input_beta.text()

    def get_input_Pl(self):
        return self.info_input_Pl.text()

    def get_input_voltage(self):
        return self.info_input_voltage.text()

    def update_main_label_value(self, text):
        if self.plot_widget is not None:
            self.plot_widget.setTitle(text)

    def get_input_x(self):
        return self.selector_input_x.text()

    def get_input_y(self):
        return self.selector_input_y.text()

    def get_input_lam(self):
        return self.selector_input_lam.text()

    def get_input_NA(self):
        return self.selector_input_NA.text()

    def get_input_confocal(self):
        return self.selector_input_confocal.isChecked()

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
