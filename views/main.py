import numpy as np
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit, QCheckBox, \
    QHBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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

        self.main_figure = None
        self.main_canvas = None

        self.second_figure = None
        self.second_canvas = None

        self.optional_figure = None
        self.optional_canvas = None

        self.footer_label = QLabel()
        font = self.footer_label.font()
        font.setItalic(True)
        self.footer_label.setFont(font)

        self.main_window = QMainWindow()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("CMOS-INV-GUI")
        self.setGeometry(0, 0, 1000, 800)
        self.showFullScreen()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QGridLayout(main_widget)

        central_widget = QWidget()
        central_layout = QGridLayout(central_widget)

        left_widget = QWidget()
        left_layout = QGridLayout(left_widget)
        left_widget.setMaximumWidth(200)
        left_widget.setMinimumWidth(200)

        main_central_widget = QWidget()
        main_central_layout = QGridLayout(main_central_widget)

        right_widget = QWidget()
        right_widget_layout = QGridLayout(right_widget)
        right_widget.setMaximumWidth(200)
        right_widget.setMinimumWidth(200)

        # Creating the menu bar
        self.init_menu_bar()

        # Creating the info widget

        info_widget = self.init_physic_info_widget()

        # Creating the laser widget

        laser_widget = self.init_laser_widget()

        # Creating the navigation bar widget
        nav_bar = self.init_nav_bar(central_layout)
        nav_bar.setMaximumHeight(50)
        nav_bar.setMinimumHeight(50)

        # Optional widget

        optional_widget = QWidget()
        self.init_optional_layout(optional_widget)

        # Creating the plot widget

        plot_container_widget = self.init_plot_widget()

        footer_widget = QWidget()
        footer_layout = QGridLayout(footer_widget)
        footer_layout.addWidget(self.footer_label, 0, 0)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer_widget.setMaximumHeight(50)
        footer_widget.setMinimumHeight(50)

        # Add all to the window layout

        left_layout.addWidget(laser_widget, 0, 0)
        left_layout.addWidget(optional_widget, 1, 0)
        right_widget_layout.addWidget(info_widget, 0, 0)
        main_central_layout.addWidget(plot_container_widget, 0, 0)

        central_layout.addWidget(left_widget, 0, 0)
        central_layout.addWidget(main_central_widget, 0, 1)
        central_layout.addWidget(right_widget, 0, 2)

        layout.addWidget(nav_bar, 0, 0)
        layout.addWidget(central_widget, 2, 0)
        layout.addWidget(footer_widget, 3, 0)


    def set_mode(self, central_layout, mode=0):

        left_layout = central_layout.itemAtPosition(0, 0).widget().layout()
        optional_layout = left_layout.itemAtPosition(1, 0).widget().layout()

        right_layout = central_layout.itemAtPosition(0, 2).widget().layout()
        info_layout = right_layout.itemAtPosition(0, 0).widget().layout()
        voltage_layout = info_layout.itemAtPosition(4, 0).layout()

        self.clear_figures()

        # hide and show the voltage button for csv mode
        self.info_button_column_voltage.hide()
        voltage_layout.addWidget(self.info_input_voltage, 0, 1)
        self.info_input_voltage.show()

        self.optional_canvas.hide()
        self.second_canvas.hide()

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
        elif mode == 2:
            self.second_canvas.show()
            voltage_layout.addWidget(self.info_input_voltage, 0, 1)

        # CSV mode
        elif mode == 3:
            self.info_input_voltage.hide()
            widget = self.init_rcv_widget()
            optional_layout.addWidget(widget, 0, 0)
            self.optional_canvas.show()
            voltage_layout.addWidget(self.info_button_column_voltage, 0, 1)
            self.info_button_column_voltage.show()

    def init_nav_bar(self, optional_layout) -> QWidget:
        nav_bar_widget = QWidget()
        nav_bar_container_layout = QHBoxLayout(nav_bar_widget)

        main_button0 = QPushButton("Laser point spread", self)
        main_button0.clicked.connect(lambda: self.controller.set_state(1))
        main_button0.clicked.connect(lambda: self.set_mode(optional_layout, 0))
        main_button1 = QPushButton("Show original output", self)
        main_button1.clicked.connect(lambda: self.controller.set_state(0))
        main_button1.clicked.connect(lambda: self.set_mode(optional_layout, 0))
        main_button2 = QPushButton("Calc RCV", self)
        main_button2.clicked.connect(lambda: self.set_mode(optional_layout, 1))
        main_button2.clicked.connect(lambda: self.controller.set_state(2))
        main_button3 = QPushButton("EOFM", self)
        main_button3.clicked.connect(lambda: self.set_mode(optional_layout, 2))
        main_button3.clicked.connect(lambda: self.controller.set_state(3))

        main_button4 = QPushButton("Import CSV data", self)
        main_button4.clicked.connect(lambda: self.set_mode(optional_layout, 3))
        main_button4.clicked.connect(lambda: self.controller.upload_csv())

        nav_bar_container_layout.addWidget(main_button0)
        nav_bar_container_layout.addWidget(main_button1)
        nav_bar_container_layout.addWidget(main_button2)
        nav_bar_container_layout.addWidget(main_button3)
        nav_bar_container_layout.addWidget(main_button4)

        return nav_bar_widget

    def init_menu_bar(self):
        menubar = self.menuBar()
        window_menu = menubar.addMenu('Import / Export')

        import_png_file = QAction('Import PNG file', self)
        import_png_file.triggered.connect(self.controller.upload_image)
        window_menu.addAction(import_png_file)

        import_json_config = QAction('Import JSON config', self)
        import_json_config.triggered.connect(self.controller.upload_json)
        window_menu.addAction(import_json_config)

        window_menu.addSeparator()

        export_json_config = QAction('Export JSON config', self)
        export_json_config.triggered.connect(self.on_export)
        window_menu.addAction(export_json_config)

        export_results = QAction('Export results', self)
        export_results.triggered.connect(self.on_export)
        window_menu.addAction(export_results)

    def init_optional_layout(self, optional_widget) -> QGridLayout:
        optional_layout = QGridLayout(optional_widget)

        self.optional_figure = Figure()
        self.optional_canvas = FigureCanvas(self.optional_figure)
        optional_layout.addWidget(self.optional_canvas, 2, 0)
        self.optional_canvas.hide()

        optional_layout.itemAtPosition(2, 0).widget().setMaximumHeight(200)

        return optional_layout

    def init_physic_info_widget(self) -> QWidget:
        info_widget = QWidget()
        info_label_Kn = QLabel("Kn:", self)
        info_label_Kp = QLabel("Kp:", self)
        info_label_beta = QLabel("Beta:", self)
        info_label_Pl = QLabel("P_L:", self)
        info_label_voltage = QLabel("Voltage:", self)
        info_button = QPushButton("Submit values", self)
        info_button.clicked.connect(self.controller.update_physics_values)

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

        line5 = QGridLayout()
        line5.addWidget(info_label_voltage, 0, 0)
        line5.addWidget(self.info_input_voltage, 0, 1)

        # Adding the lines to the main layout
        input_layout.addLayout(line1, 0, 0)
        input_layout.addLayout(line2, 1, 0)
        input_layout.addLayout(line3, 2, 0)
        input_layout.addLayout(line4, 3, 0)
        input_layout.addLayout(line5, 4, 0)
        input_layout.addWidget(info_button, 5, 0)

        input_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout.setSpacing(20)

        return info_widget

    def init_plot_widget(self) -> QWidget:

        plot_container_widget = QWidget()
        plot_layout = QGridLayout(plot_container_widget)

        self.main_figure = Figure()
        self.main_canvas = FigureCanvas(self.main_figure)
        plot_layout.addWidget(self.main_canvas, 0, 0)

        self.second_figure = Figure()
        self.second_canvas = FigureCanvas(self.second_figure)
        plot_layout.addWidget(self.second_canvas, 0, 1)
        self.second_canvas.hide()

        return plot_container_widget

    def init_laser_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.selector_input_lam = QLineEdit(self)
        self.selector_input_lam.setText(str(self.controller.lam_value))
        self.selector_input_lam.setPlaceholderText(str(self.controller.lam_value))
        label_lam = QLabel("Lambda:")

        self.selector_input_NA = QLineEdit(self)
        self.selector_input_NA.setText(str(self.controller.NA_value))
        self.selector_input_NA.setPlaceholderText(str(self.controller.NA_value))
        label_NA = QLabel("NA:")

        self.selector_input_confocal = QCheckBox()
        self.selector_input_confocal.setChecked(bool(self.controller.is_confocal))
        label_confocal = QLabel("Confocal")

        info_button = QPushButton("Submit values", self)
        info_button.clicked.connect(self.controller.update_physics_values)

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

        layout.addWidget(info_button)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

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

        selector_button = QPushButton("Submit values", self)
        selector_button.clicked.connect(self.controller.update_rcv_position)

        selector_layout = QGridLayout(selector_widget)
        selector_layout.addWidget(selector_label_x, 0, 0)
        selector_layout.addWidget(self.selector_input_x, 0, 1)
        selector_layout.addWidget(selector_label_y, 1, 0)
        selector_layout.addWidget(self.selector_input_y, 1, 1)
        selector_layout.addWidget(selector_button, 2, 1)

        selector_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        selector_layout.setSpacing(20)

        return selector_widget

    def display_image(self, image_matrix, title="", lps=False):
        ax = self.main_figure.add_subplot(111)

        if lps:
            im = ax.imshow(image_matrix)
            self.main_figure.colorbar(im)
        else:
            ax.imshow(image_matrix, cmap='gist_gray')

        ax.set_title(str(title))
        ax.set_xlabel("x")
        ax.set_ylabel('y')

        self.main_canvas.draw()
        self.controller.stop_thread()

    def clear_figures(self):
        self.main_figure.clear()
        self.optional_figure.clear()
        self.second_figure.clear()

    def display_optional_image(self, image_matrix, title=""):
        ax = self.optional_figure.add_subplot(111)
        ax.imshow(image_matrix, cmap='gist_gray')
        ax.set_title(str(title))
        ax.set_xlabel("x")
        ax.set_ylabel('y')
        self.optional_canvas.draw()
        self.controller.stop_thread()

    def display_second_image(self, image_matrix, title=""):
        ax = self.second_figure.add_subplot(111)
        ax.imshow(image_matrix, cmap='gist_gray')
        ax.set_title(str(title))
        ax.set_xlabel("x")
        ax.set_ylabel('y')
        self.second_canvas.draw()
        self.controller.stop_thread()

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

    def set_footer_label(self, text):
        self.footer_label.setText(text)

    def plot_dataframe(self, df, selected_columns):
        time = df[selected_columns[0]]
        voltage = df[selected_columns[1]]
        rcv = df['RCV']
        # TODO add pourcentage as a parameter in view
        percentage = 0.05
        noisy_rcv = rcv + np.random.normal(0, rcv.std(), time.size) * percentage

        ax1 = self.main_figure.add_subplot(211)

        ax2 = self.main_figure.add_subplot(212)
        ax3 = ax2.twinx()

        ax1.plot(time, rcv, label="RCV", color='purple')
        ax2.plot(time, noisy_rcv, label='Noisy RCV', color='red')
        ax3.plot(time, voltage, label=f'Voltage - ({selected_columns[1]})', color='blue', linewidth=0.5)

        ax2.set_xlabel(f"Time (s) - ({selected_columns[0]})")
        ax3.set_ylabel('Voltage (V)', color='blue')
        ax1.set_ylabel('RCV (nm²)', color='purple')
        ax2.set_ylabel('RCV (nm²)', color='red')

        ax1.set_title('RCV in function of time')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left')
        ax3.legend(loc='upper right')

        ax1.set_xlim(time.min(), time.max())
        ax2.set_xlim(time.min(), time.max())

        self.main_canvas.draw()
        self.controller.stop_thread()

    def on_import(self):
        print('Import action triggered')

    def on_export(self):
        print('Export action triggered')

