import re
import time

import numpy as np
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QMessageBox, QApplication, QMenu
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib_scalebar.scalebar import ScaleBar

from views.components.cell_layout import CellLayout
from views.components.gate_layout import GateLayout
from views.components.laser_layout import LaserLayout
from views.components.laser_position_layout import LaserPositionLayout


class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        # fill infos from controller
        self.laser_layout = LaserLayout({'lam_value': self.controller.lam_value,
                                         'NA_value': self.controller.NA_value,
                                         'is_confocal': self.controller.is_confocal
                                         })

        self.gate_layout = GateLayout({'Kn_value': self.controller.Kn_value,
                                       'Kp_value': self.controller.Kp_value,
                                       'beta_value': self.controller.beta_value,
                                       'Pl_value': self.controller.Pl_value,
                                       'voltage_value': self.controller.voltage_value,
                                       'noise_pourcentage': self.controller.noise_pourcentage
                                       })
        self.laser_position_layout = LaserPositionLayout()

        self.main_figure = None
        self.main_canvas = None

        self.second_figure = None
        self.second_canvas = None

        self.preview_figure = None
        self.preview_canvas = None

        self.footer_label = QLabel()
        self.footer_label.setObjectName("footer")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.technology_label = QLabel()
        self.technology_label.setObjectName("footer")
        self.technology_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.cell_selector = CellLayout(self.controller.gds_cell_list)
        self.cell_selector.filterLineEdit.textChanged.connect(lambda: self.cell_selector.filter_items())
        self.cell_selector.cell_button.clicked.connect(lambda: self.controller.update_cell_values())
        self.cell_selector.set_cell_name(str(self.controller.cell_name))
        self.cell_selector.set_state_list(str(self.controller.state_list))

        self.buttons = []

        self.main_window = QMainWindow()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("CMOS-INV-GUI")
        self.setGeometry(0, 0, 1000, 800)
        self.showFullScreen()
        self.setStyleSheet(open("resources/styles.css").read())

        main_widget = QWidget()
        main_widget.setObjectName("main")
        self.setCentralWidget(main_widget)

        layout = QGridLayout(main_widget)
        # main_widget.setStyleSheet("border : 1px solid black")

        central_widget = QWidget()
        central_layout = QGridLayout(central_widget)

        left_widget = QWidget()
        left_layout = QGridLayout(left_widget)
        left_widget.setMaximumWidth(200)
        left_widget.setMinimumWidth(200)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_central_widget = QWidget()
        main_central_layout = QGridLayout(main_central_widget)

        right_widget = QWidget()
        right_widget_layout = QGridLayout(right_widget)
        right_widget.setMaximumWidth(200)
        right_widget.setMinimumWidth(200)

        # Creating the menu bar
        self.init_menu_bar()

        # Creating the info widget

        info_widget = self.gate_layout.widget
        self.gate_layout.info_button_column_voltage.clicked.connect(self.controller.volage_column_dialog)
        self.gate_layout.submit_btn.clicked.connect(self.controller.update_physics_values)

        # Creating cell widget

        cell_widget = self.init_cell_widget()

        # Creating the laser widget
        laser_widget = self.laser_layout.widget
        laser_submit_btn = self.laser_layout.submit_btn
        laser_submit_btn.clicked.connect(self.controller.update_physics_values)

        # Creating the navigation bar widget
        nav_bar = self.init_nav_bar(central_layout)
        nav_bar.setMaximumHeight(60)
        nav_bar.setMinimumHeight(60)

        # Optional widget

        preview_widget = self.init_preview_layout()
        preview_widget.setMaximumHeight(400)
        preview_widget.setMinimumWidth(400)

        # Creating the plot widget

        plot_container_widget = self.init_plot_widget()

        footer_widget = QWidget()
        footer_layout = QGridLayout(footer_widget)
        footer_layout.addWidget(self.footer_label, 0, 1)
        footer_layout.addWidget(self.technology_label, 0, 0)
        footer_widget.setMaximumHeight(50)
        footer_widget.setMinimumHeight(50)

        # Add all to the window layout

        left_layout.addWidget(laser_widget, 0, 0)
        left_layout.addWidget(preview_widget, 2, 0)
        right_widget_layout.addWidget(info_widget, 0, 0)
        right_widget_layout.addWidget(cell_widget, 1, 0)
        main_central_layout.addWidget(plot_container_widget, 0, 0)

        central_layout.addWidget(left_widget, 0, 0)
        central_layout.addWidget(main_central_widget, 0, 1)
        central_layout.addWidget(right_widget, 0, 2)

        layout.addWidget(nav_bar, 0, 0)
        layout.addWidget(central_widget, 2, 0)
        layout.addWidget(footer_widget, 3, 0)

    def set_mode(self, central_layout, mode=0):

        left_widget = central_layout.itemAtPosition(0, 0).widget()
        left_layout = left_widget.layout()

        right_layout = central_layout.itemAtPosition(0, 2).widget().layout()
        info_layout = right_layout.itemAtPosition(0, 0).widget().layout()
        voltage_widget = info_layout.itemAtPosition(4, 0).widget()
        noise_pourcentage_widget = info_layout.itemAtPosition(6, 0).widget()

        left_widget.setMaximumWidth(200)

        self.clear_figures()

        # hide and show the voltage button for csv mode
        self.gate_layout.info_button_column_voltage.hide()
        voltage_widget.show()

        self.preview_canvas.hide()
        self.second_canvas.hide()
        noise_pourcentage_widget.hide()

        # Clear the layout if there's already a widget at position (0, 0)
        if left_layout.itemAtPosition(1, 0) is not None:
            item = left_layout.itemAtPosition(1, 0)
            widget_to_remove = item.widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # RCV mode
        if mode == 1:
            self.laser_position_layout.init_ui({'input_x': self.controller.x_position,
                                                'input_y': self.controller.y_position
                                                })
            widget = self.laser_position_layout.widget
            self.laser_position_layout.selector_button.clicked.connect(self.controller.update_rcv_position)

            left_layout.addWidget(widget, 1, 0)

        # EOFM mode
        elif mode == 2:
            self.second_canvas.show()

        # CSV mode
        elif mode == 3:
            self.laser_position_layout.init_ui({'input_x': self.controller.x_position,
                                                'input_y': self.controller.y_position
                                                })
            widget = self.laser_position_layout.widget
            self.laser_position_layout.selector_button.clicked.connect(self.controller.update_rcv_position)

            left_layout.addWidget(widget, 1, 0)
            self.preview_canvas.show()

            left_widget.setMaximumWidth(400)

            voltage_widget.hide()
            self.gate_layout.info_button_column_voltage.show()
            noise_pourcentage_widget.show()

    def init_nav_bar(self, central_layout) -> QWidget:
        nav_bar_widget = QWidget()
        nav_bar_container_layout = QHBoxLayout(nav_bar_widget)

        laser_pixmap = QPixmap('resources/logo/LPS_logo.png')

        # Add spaces between icon and name to have a margin (not found another way)
        main_button0 = QPushButton(QIcon(laser_pixmap), "  Laser point spread", self)

        main_button0.setCursor(Qt.CursorShape.PointingHandCursor)
        main_button0.clicked.connect(lambda: self.set_selected(main_button0))

        main_button0.clicked.connect(lambda: self.set_mode(central_layout, 0))
        main_button0.clicked.connect(lambda: self.controller.set_state(1))

        layout_pixmap = QPixmap('resources/logo/Layout_logo.png')

        main_button1 = QPushButton(QIcon(layout_pixmap), "  Show original output", self)

        main_button1.setCursor(Qt.CursorShape.PointingHandCursor)
        main_button1.clicked.connect(lambda: self.set_selected(main_button1))

        main_button1.clicked.connect(lambda: self.set_mode(central_layout, 4))
        main_button1.clicked.connect(lambda: self.controller.set_state(0))

        RCV_pixmap = QPixmap('resources/logo/RCV_logo.png')

        main_button2 = QPushButton(QIcon(RCV_pixmap), "  Calc RCV", self)

        main_button2.setCursor(Qt.CursorShape.PointingHandCursor)
        main_button2.clicked.connect(lambda: self.set_selected(main_button2))

        main_button2.clicked.connect(lambda: self.set_mode(central_layout, 1))
        main_button2.clicked.connect(lambda: self.controller.set_state(2))

        EOFM_pixmap = QPixmap('resources/logo/EOFM_logo.png')

        main_button3 = QPushButton(QIcon(EOFM_pixmap), "  EOFM", self)
        main_button3.setCursor(Qt.CursorShape.PointingHandCursor)
        main_button3.clicked.connect(lambda: self.set_selected(main_button3))

        main_button3.clicked.connect(lambda: self.set_mode(central_layout, 2))
        main_button3.clicked.connect(lambda: self.controller.set_state(3))

        CSV_pixmap = QPixmap('resources/logo/CSV_logo.png')

        main_button4 = QPushButton(QIcon(CSV_pixmap), "  Import CSV data", self)
        main_button4.setCursor(Qt.CursorShape.PointingHandCursor)
        main_button4.clicked.connect(lambda: self.set_selected(main_button4))

        main_button4.clicked.connect(lambda: self.set_mode(central_layout, 3))
        main_button4.clicked.connect(lambda: self.controller.upload_csv())

        nav_bar_container_layout.addWidget(main_button0)
        nav_bar_container_layout.addWidget(main_button1)
        nav_bar_container_layout.addWidget(main_button2)
        nav_bar_container_layout.addWidget(main_button3)
        nav_bar_container_layout.addWidget(main_button4)

        self.buttons.append(main_button0)
        self.buttons.append(main_button1)
        self.buttons.append(main_button2)
        self.buttons.append(main_button3)
        self.buttons.append(main_button4)

        for btn in self.buttons:
            btn.setObjectName("nav-bar-btn")

        self.set_selected(main_button1)

        return nav_bar_widget

    def init_menu_bar(self):
        menubar = self.menuBar()

        window_menu = QMenu('Import / Export', self)
        menubar.addMenu(window_menu)

        exit_action = QAction("Stop Auto-OPS", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        window_menu.addAction(exit_action)

        window_menu.addSeparator()

        import_png_file = QAction('Import PNG file', self)
        import_png_file.triggered.connect(self.controller.upload_image)
        window_menu.addAction(import_png_file)

        import_json_config = QAction('Import JSON config', self)
        import_json_config.triggered.connect(self.controller.upload_json)
        window_menu.addAction(import_json_config)

        window_menu.addSeparator()

        export_json_config = QAction('Export JSON config', self)
        export_json_config.triggered.connect(self.controller.save_settings_to_json)
        window_menu.addAction(export_json_config)

        export_results = QAction('Export SVG plots', self)
        export_results.triggered.connect(self.controller.export_plots)
        window_menu.addAction(export_results)

        export_np_array = QAction('Export Np array plots', self)
        export_np_array.triggered.connect(self.controller.export_np_array)
        window_menu.addAction(export_np_array)

    def init_preview_layout(self) -> QWidget:

        self.preview_figure = Figure()
        self.preview_canvas = FigureCanvas(self.preview_figure)
        self.preview_canvas.hide()

        return self.preview_canvas

    def init_cell_widget(self) -> QWidget:
        cell_widget = QWidget()

        cell_layout = QVBoxLayout(cell_widget)
        cell_layout.addLayout(self.cell_selector.get_layout())

        return cell_widget

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

    def set_selected(self, selected_button):
        for button in self.buttons:
            if button is not selected_button:
                button.setStyleSheet("")
            else:
                button.setStyleSheet("background-color: lightgoldenrodyellow")

    def display_image(self, image_matrix, export, title="", lps=False):
        if len(self.main_figure.axes) > 0:
            self.main_figure.clear()

        ax = self.main_figure.add_subplot(111)

        if lps:
            im = ax.imshow(image_matrix, cmap='Reds', origin='lower')
            self.main_figure.colorbar(im)
        else:
            ax.imshow(image_matrix, cmap='gist_gray', origin='lower')

        if self.controller.scale_up is not None:
            scale = self.controller.scale_up
            scalebar = ScaleBar(1 / scale, units="um", location="lower left", label=f"1:{scale}")
            ax.add_artist(scalebar)

        ax.set_title(str(title))
        ax.set_xlabel("x")
        ax.set_ylabel('y')
        if not export:
            self.main_canvas.draw()
        else:
            if title == "":
                title = str(time)
            title = re.sub(r'[^a-zA-Z0-9]', '_', title)
            self.main_figure.savefig('export/plots/' + title + '.svg', format='svg')

        self.controller.stop_thread()

    def clear_figures(self):
        self.main_figure.clear()
        self.preview_figure.clear()
        self.second_figure.clear()

    def display_optional_image(self, image_matrix, title="", axis=True):
        if len(self.preview_figure.axes) > 0:
            self.preview_figure.clear()

        ax = self.preview_figure.add_subplot(111)
        ax.imshow(image_matrix, cmap='gist_gray', origin='lower')
        ax.set_title(str(title))

        if axis:
            ax.set_xlabel("x")
            ax.set_ylabel('y')
        else:
            ax.axis('off')

        self.preview_canvas.draw()
        self.controller.stop_thread()

    def display_second_image(self, image_matrix, export, title=""):
        if len(self.second_figure.axes) > 0:
            self.second_figure.clear()

        ax = self.second_figure.add_subplot(111)
        ax.imshow(image_matrix, cmap='gist_gray')
        ax.set_title(str(title))
        ax.set_xlabel("x")
        ax.set_ylabel('y')
        if not export:
            self.second_canvas.draw()
        else:
            if title == "":
                title = str(time)
            title = re.sub(r'[^a-zA-Z0-9]', '_', title)
            self.second_figure.savefig('export/plots/' + title + '.svg', format='svg')

        self.controller.stop_thread()

    def set_technology_label(self, text):
        self.technology_label.setText(text)

    def set_footer_label(self, text):
        self.footer_label.setText(text)

    def popup_window(self, title, text):
        QMessageBox.about(self, title, text)

    def plot_dataframe(self, df, selected_columns):
        if len(self.main_figure.axes) > 0:
            self.main_figure.clear()
        time_abs = df[selected_columns[0]]
        voltage = df[selected_columns[1]]
        rcv = df['RCV']
        percentage = float(self.controller.noise_pourcentage) / 100
        noisy_rcv = rcv + np.random.normal(0, rcv.std(), time_abs.size) * percentage

        ax1 = self.main_figure.add_subplot(211)

        ax2 = self.main_figure.add_subplot(212)
        ax3 = ax2.twinx()

        ax1.plot(time_abs, rcv, label="RCV", color='purple')
        ax2.plot(time_abs, noisy_rcv, label='Noisy RCV', color='red')
        ax3.plot(time_abs, voltage, label=f'Voltage - ({selected_columns[1]})', color='blue', linewidth=0.5)

        ax2.set_xlabel(f'Time (s) - ({selected_columns[0]})')
        ax3.set_ylabel(f'Voltage - ({selected_columns[1]})', color='blue')
        ax1.set_ylabel('RCV (nm²)', color='purple')
        ax2.set_ylabel('RCV (nm²)', color='red')

        ax1.set_title('RCV in function of time')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left')
        ax3.legend(loc='upper right')

        ax1.set_xlim(time_abs.min(), time_abs.max())
        ax2.set_xlim(time_abs.min(), time_abs.max())

        self.main_canvas.draw()
        self.controller.stop_thread()

    def update_inputs_values(self):
        self.laser_layout.update_inputs({'lam_value': self.controller.lam_value,
                                         'NA_value': self.controller.NA_value,
                                         'is_confocal': self.controller.is_confocal
                                         })

        self.gate_layout.update_inputs({'Kn_value': self.controller.Kn_value,
                                        'Kp_value': self.controller.Kp_value,
                                        'beta_value': self.controller.beta_value,
                                        'Pl_value': self.controller.Pl_value,
                                        'voltage_value': self.controller.voltage_value,
                                        'noise_pourcentage': self.controller.noise_pourcentage
                                        })

        self.laser_position_layout.update_inputs({'input_x': self.controller.x_position,
                                                  'input_y': self.controller.y_position
                                                  })
