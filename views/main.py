import numpy as np
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# TODO try to add color into plot especially for lps

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.info_input_Kn = QLineEdit(self)
        self.info_input_Kp = QLineEdit(self)
        self.info_input_beta = QLineEdit(self)
        self.info_input_Pl = QLineEdit(self)
        self.info_input_voltage = QLineEdit(self)

        # fill infos from controller
        self.info_input_Kn.setText(str(self.controller.Kn_value))
        self.info_input_Kn.setPlaceholderText(str(self.controller.Kn_value))
        self.info_input_Kp.setText(str(self.controller.Kp_value))
        self.info_input_Kp.setPlaceholderText(str(self.controller.Kp_value))
        self.info_input_beta.setText(str(self.controller.beta_value))
        self.info_input_beta.setPlaceholderText(str(self.controller.beta_value))
        self.info_input_Pl.setText(str(self.controller.Pl_value))
        self.info_input_Pl.setPlaceholderText(str(self.controller.Pl_value))
        self.info_input_voltage.setText(str(self.controller.voltage_value))
        self.info_input_voltage.setPlaceholderText(str(self.controller.voltage_value))

        self.info_button_column_voltage = QPushButton("Voltage columns")
        self.info_button_column_voltage.clicked.connect(self.controller.volage_column_dialog)

        self.selector_input_x = None
        self.selector_input_y = None

        self.selector_input_lam = None
        self.selector_input_NA = None
        self.selector_input_confocal = None

        title = QFont()
        title.setPointSize(16)
        title.setBold(True)

        self.image_view = pg.ImageItem(None)
        self.main_plot_label = QLabel()
        self.main_plot_label.setFont(title)
        self.second_image_view = pg.ImageItem(None)
        self.second_plot_label = QLabel()
        self.second_plot_label.setFont(title)

        self.figure = None
        self.canvas = None

        self.main_window = QMainWindow()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("CMOS-INV-GUI")
        self.setGeometry(0, 0, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        # Creating the add widget

        button_widget = self.init_button_widget(layout)

        # Creating the info widget

        info_widget = self.init_physic_info_widget()

        # Creating the laser widget

        laser_widget = self.init_laser_widget()

        # Creating the navigation bar widget
        nav_bar = self.init_nav_bar(layout)

        # Optional widget

        optional_widget = QWidget()
        self.init_optional_layout(optional_widget)

        # Creating the plot widget

        plot_container_widget = self.init_plot_widget()

        # Add all to the window layout

        layout.addWidget(button_widget, 0, 0)
        layout.addWidget(info_widget, 0, 1)
        layout.addWidget(laser_widget, 1, 0)
        layout.addWidget(nav_bar, 1, 1)
        layout.addWidget(optional_widget, 2, 0)
        layout.addWidget(plot_container_widget, 2, 1)

    def set_mode(self, layout, mode=0):

        optional_layout = layout.itemAtPosition(2, 0).widget().layout()
        plot_layout = layout.itemAtPosition(2, 1).widget().layout()
        info_layout = layout.itemAtPosition(0, 1).widget().layout()

        # Find and clear the second_plot_widget
        main_plot_widget = plot_layout.itemAtPosition(1, 0).widget()
        main_plot_widget_df = plot_layout.itemAtPosition(2, 0).widget()
        second_plot_widget = optional_layout.itemAtPosition(2, 0).widget()

        voltage_input = info_layout.itemAtPosition(4, 1).widget()

        # TODO fix overwrite sometime
        if voltage_input:
            voltage_input.hide()
            info_layout.addWidget(self.info_input_voltage, 4, 1)
            self.info_input_voltage.show()

        self.second_plot_label.setText("")
        if second_plot_widget is not None:
            second_plot_widget.hide()

        if main_plot_widget_df is not None:
            main_plot_widget_df.hide()

        if main_plot_widget is not None:
            main_plot_widget.show()

        # Clear the layout if there's already a widget at position (0, 0)
        if optional_layout.itemAtPosition(0, 0) is not None:
            item = optional_layout.itemAtPosition(0, 0)
            widget_to_remove = item.widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # RCV mode
        if mode == 1:
            widget = self.init_rcv_widget()
            optional_layout.addWidget(widget, 0, 0)

        # EOFM mode
        elif (mode == 2) & (second_plot_widget is not None):
            self.second_plot_label.setText("Inverted EOFM plot")
            second_plot_widget.show()
            info_layout.addWidget(self.info_input_voltage, 4, 1)

        # CSV mode
        elif mode == 3:
            voltage_input.hide()
            widget = self.init_rcv_widget()
            optional_layout.addWidget(widget, 0, 0)
            main_plot_widget_df.show()
            main_plot_widget.hide()
            second_plot_widget.show()
            info_layout.addWidget(self.info_button_column_voltage, 4, 1)
            self.info_button_column_voltage.show()


    def init_nav_bar(self, optional_layout) -> QWidget:
        nav_bar_widget = QWidget()
        nav_bar_container_layout = QGridLayout(nav_bar_widget)

        main_button0 = QPushButton("Laser point spread", self)
        main_button0.clicked.connect(self.controller.print_psf)
        main_button0.clicked.connect(lambda: self.set_mode(optional_layout, 0))
        main_button1 = QPushButton("Show original output", self)
        main_button1.clicked.connect(self.controller.print_original_image)
        main_button1.clicked.connect(lambda: self.set_mode(optional_layout, 0))
        main_button2 = QPushButton("Calc RCV", self)
        main_button2.clicked.connect(lambda: self.set_mode(optional_layout, 1))
        main_button2.clicked.connect(self.controller.print_rcv_image)
        main_button3 = QPushButton("EOFM", self)
        main_button3.clicked.connect(lambda: self.set_mode(optional_layout, 2))
        main_button3.clicked.connect(self.controller.print_EOFM_image)

        nav_bar_container_layout.addWidget(main_button0, 0, 0)
        nav_bar_container_layout.addWidget(main_button1, 0, 1)
        nav_bar_container_layout.addWidget(main_button2, 0, 2)
        nav_bar_container_layout.addWidget(main_button3, 0, 3)

        return nav_bar_widget

    def init_button_widget(self, optional_layout) -> QWidget:
        button_widget = QWidget()
        button_add_png = QPushButton("Add png file", self)
        button_add_png.clicked.connect(self.controller.upload_image)
        button_add_json = QPushButton("Add JSON config", self)
        button_add_json.clicked.connect(self.controller.upload_json)
        button_add_csv = QPushButton("Add csv file", self)
        button_add_csv.clicked.connect(self.controller.upload_csv)
        button_add_csv.clicked.connect(lambda: self.set_mode(optional_layout, 3))

        button_layout = QVBoxLayout(button_widget)
        button_layout.addWidget(button_add_png)
        button_layout.addWidget(button_add_json)
        button_layout.addWidget(button_add_csv)

        return button_widget

    def init_optional_layout(self, optional_widget) -> QGridLayout:
        optional_layout = QGridLayout(optional_widget)

        optional_layout.addWidget(self.second_plot_label, 1, 0)

        second_plot_widget = pg.PlotWidget()
        second_plot_widget.addItem(self.second_image_view)
        second_plot_widget.setFixedWidth(400)
        second_plot_widget.setFixedHeight(400)
        optional_layout.addWidget(second_plot_widget, 2, 0)
        second_plot_widget.hide()

        return optional_layout

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

    def init_plot_widget(self) -> QWidget:
        plot_widget = pg.PlotWidget()
        plot_widget.addItem(self.image_view)
        plot_widget.setFixedWidth(400)
        plot_widget.setFixedHeight(400)

        plot_container_widget = QWidget()
        plot_layout = QGridLayout(plot_container_widget)
        plot_layout.addWidget(self.main_plot_label, 0, 0)
        plot_layout.addWidget(plot_widget, 1, 0)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(self.canvas, 2, 0)
        self.canvas.hide()

        return plot_container_widget

    def init_laser_widget(self) -> QWidget:
        widget = QWidget()
        layout = QGridLayout(widget)
        self.selector_input_lam = QLineEdit(self)
        self.selector_input_lam.setText(str(self.controller.lam_value))
        self.selector_input_lam.setPlaceholderText(str(self.controller.lam_value))
        label_lam = QLabel("Lambda")
        self.selector_input_NA = QLineEdit(self)
        self.selector_input_NA.setText(str(self.controller.NA_value))
        self.selector_input_NA.setPlaceholderText(str(self.controller.NA_value))
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

    def init_rcv_widget(self) -> QWidget:
        selector_widget = QWidget()
        selector_label_x = QLabel("x: ", self)
        selector_label_y = QLabel("y: ", self)

        self.selector_input_x = QLineEdit(self)
        self.selector_input_x.setText(str(self.controller.x_position))
        self.selector_input_x.setPlaceholderText(str(self.controller.x_position))
        self.selector_input_y = QLineEdit(self)
        self.selector_input_y.setText(str(self.controller.y_position))
        self.selector_input_y.setPlaceholderText(str(self.controller.y_position))

        selector_button = QPushButton("change position", self)
        selector_button.clicked.connect(self.controller.update_rcv_position)

        selector_layout = QGridLayout(selector_widget)
        selector_layout.addWidget(selector_label_x, 0, 0)
        selector_layout.addWidget(self.selector_input_x, 0, 1)
        selector_layout.addWidget(selector_label_y, 1, 0)
        selector_layout.addWidget(self.selector_input_y, 1, 1)
        selector_layout.addWidget(selector_button, 2, 1)

        return selector_widget


    def display_image(self, image_matrix, eofm=False):
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
        self.main_plot_label.setText(text)

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

    def plot_dataframe(self, df, selected_columns):
        self.figure.clear()

        time = df[selected_columns[0]]
        voltage = df[selected_columns[1]]

        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()

        ax1.plot(time, voltage, label='Voltage', color='blue')
        ax2.plot(time, df['RCV'], label='RCV', color='red')

        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)', color='blue')
        ax2.set_ylabel('RCV (nm²)', color='red')

        ax1.set_title('DataFrame Plot')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        ax1.set_xlim(time.min(), time.max())

        self.canvas.draw()
