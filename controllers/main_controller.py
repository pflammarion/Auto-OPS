import copy
import itertools
import json
import os
import threading
import time

import gdspy
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

from controllers import gds_drawing, def_parser
from controllers.GDS_Object.op import Op
from controllers.lib_reader import LibReader
from views.column_dialog import ColumnSelectionDialog
from views.layer_list_dialog import LayerSelectionDialog
from views.main import MainView
from views.technology_dialog import TechnologySelectionDialog


class MainController:
    def __init__(self):

        self.scale_up = None
        self.gds_cell_list = None
        self.lib_reader = None
        self.selected_layer = None
        self.op_master = None
        self.def_file = None
        self.vpi_extraction = None
        self.selected_area = 0
        self.selected_patch_size = 20

        self.state_list = "1"
        self.cell_name = "INV_X1"

        self.object_storage_list = {}

        self.imported_image = False

        # init all class variables
        self.technology_value = 45
        self.Kn_value = 1
        self.Kp_value = -1.3
        self.beta_value = 1
        self.Pl_value = 10E7
        self.voltage_value = 1.2
        self.noise_pourcentage = 5

        self.max_voltage_high_gate_state = float('-inf')
        self.high_gate_state_layout = None

        # to initialize the value and the rcv mask
        self.x_position = 1500
        self.y_position = 1500

        self.lam_value = 1300
        self.NA_value = 0.75
        self.is_confocal = True

        self.data = self.load_settings_from_json("config/config.json")

        if self.gds_cell_list is None or self.lib_reader is None or self.selected_layer is None:
            self.init_op_object()

        if self.def_file is None:
            self.extract_op_cell(self.cell_name)

        self.dataframe = None

        self.selected_columns = None

        self.main_label_value = ""

        self.image_matrix = None

        self.app_state = 0

        self.view = MainView(self)

        self.view.set_technology_label("Technology: " + str(self.technology_value) + " nm")

        self._running = True

        self.is_plot_export = False

        self.reload_view()

    def stop_thread(self):
        self._running = False

    def reload_view(self):
        threading.Thread(target=self.reload_view_wrapper).start()

    def reload_view_wrapper(self):
        self.scale_up = None
        self.view.set_footer_label("... Loading ...")
        start = time.time()
        if not self.imported_image:
            lam, G1, G2, Gap = self.parameters_init(self.Kn_value, self.Kp_value, self.voltage_value, self.beta_value, self.Pl_value)
            if self.op_master is not None:
                if self.def_file is not None:
                    self.image_matrix, self.scale_up = gds_drawing.benchmark_matrix(self.object_storage_list, self.def_file, G1, G2, self.vpi_extraction, self.selected_area)
                else:
                    if self.cell_name not in self.object_storage_list.keys():
                        self.extract_op_cell(self.cell_name)

                    if self.state_list not in self.object_storage_list[self.cell_name].keys():
                        self.apply_state_op(self.state_list)

                    op_object = self.object_storage_list[self.cell_name][self.state_list]
                    self.image_matrix, self.scale_up = gds_drawing.export_matrix_reflection(op_object, G1, G2)

            else:
                self.image_matrix = self.draw_layout(lam, G1, G2, Gap)

        if self.app_state == 1:
            self.print_psf()

        elif self.app_state == 2:
            self.print_rcv_image()

        elif self.app_state == 3:
            self.print_EOFM_image()

        elif self.app_state == 4:
            self.plot_rcv_calc()

        else:
            self.print_original_image()

        end = time.time()
        self.view.set_footer_label(f"Execution time: {end - start:.2f} seconds")

    def plot_rcv_calc_wrapper(self):
        self.view.set_footer_label("... Loading ...")
        start = time.time()
        self.plot_rcv_calc()
        end = time.time()
        self.view.set_footer_label(f"Execution time for plot_rcv_calc: {end - start:.2f} seconds")

    def set_state(self, state):
        self.app_state = int(state)
        self.reload_view()

    def load_settings_from_json(self, json_file_path):
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, "r") as json_file:
                    data = json.load(json_file)

                if "technology" in data:
                    self.technology_value = data["technology"]

                if "laser_config" in data:
                    self.lam_value = data["laser_config"]["lamda"]
                    self.NA_value = data["laser_config"]["NA"]
                    self.is_confocal = data["laser_config"]["is_confocal"]
                    self.x_position = data["laser_config"]["x_position"]
                    self.y_position = data["laser_config"]["y_position"]
                if "gate_config" in data:
                    self.technology_value = data["gate_config"]["technology"]
                    self.Kn_value = data["gate_config"]["Kn"]
                    self.Kp_value = data["gate_config"]["Kp"]
                    self.beta_value = data["gate_config"]["beta"]
                    self.Pl_value = data["gate_config"]["Pl"]
                    self.voltage_value = data["gate_config"]["voltage"]
                    self.noise_pourcentage = data["gate_config"]["noise_pourcentage"]

                if "op_config" in data:
                    std_file = data["op_config"]["std_file"]
                    lib_file = data["op_config"]["lib_file"]
                    def_file = data["op_config"]["def_file"]
                    vpi_file = data["op_config"]["vpi_file"]

                    selected_area = data["op_config"]["selected_area"]
                    if selected_area is not None and selected_area != "":
                        self.selected_area = selected_area

                    selected_patch_size = data["op_config"]["selected_patch_size"]
                    if selected_patch_size is not None and selected_patch_size != "":
                       self.selected_patch_size = selected_patch_size

                    lib = gdspy.GdsLibrary()

                    self.gds_cell_list = lib.read_gds(std_file).cells

                    self.lib_reader = LibReader(lib_file)
                    self.selected_layer = data["op_config"]["layer_list"]

                    if vpi_file is not None and vpi_file != "":
                        self.vpi_extraction = {}
                        with open(vpi_file, 'r') as file:
                            for line in file:
                                key, value = line.strip().split(',')
                                self.vpi_extraction[key] = value

                    if def_file is not None and def_file != "":
                        self.def_file = def_parser.get_gates_info_from_def_file(def_file, self.selected_patch_size)
                        cell_name_list = self.def_file[2]
                        for cell_name in cell_name_list:
                            self.extract_op_cell(cell_name)
                            combinations = list(itertools.product([0, 1], repeat=len(self.op_master.inputs_list)))
                            for input_combination in combinations:
                                input_str = ''.join(map(str, input_combination))
                                self.apply_state_op(input_str)

                return data

            except Exception as e:
                print(f"Error loading JSON data: {e}")
        else:
            print(f"JSON file '{json_file_path}' does not exist.")

    def save_settings_to_json(self):
        json_data = {
            "technology": self.technology_value,
            "laser_config": {
                "lamda": self.lam_value,
                "NA": self.NA_value,
                "is_confocal": self.is_confocal,
                "x_position": self.x_position,
                "y_position": self.y_position
            },
            "gate_config": {
                "Kn": self.Kn_value,
                "Kp": self.Kp_value,
                "beta": self.beta_value,
                "Pl": self.Pl_value,
                "voltage": self.voltage_value,
                "noise_pourcentage": self.noise_pourcentage
            }
        }

        json_file_path = "export/config.json"

        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        self.view.popup_window("Export Successful", "Settings exported successfully in 'export' folder!")

    def export_plots(self):
        start = time.time()

        self.is_plot_export = True
        state = self.app_state
        for i in range(0, 4):
            self.app_state = i
            self.reload_view_wrapper()
        self.is_plot_export = False
        self.app_state = state
        self.reload_view_wrapper()
        self.view.popup_window("Export Successful", "Plots exported successfully in 'export/plots' folder!")

        end = time.time()
        self.view.set_footer_label(f"Execution time for SVG export: {end - start:.2f} seconds")

    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                image_read = cv2.imread(image_path)

                if image_read is None:
                    print("Failed to load the image.py")
                    return

                original_height, original_width, _ = image_read.shape

                # Calculate the center of the image.py
                center_x, center_y = original_width // 2, original_height // 2

                target_size = (3000, 3000)

                # Calculate the cropping area
                crop_x1 = max(0, center_x - target_size[0] // 2)
                crop_x2 = min(original_width, center_x + target_size[0] // 2)
                crop_y1 = max(0, center_y - target_size[1] // 2)
                crop_y2 = min(original_height, center_y + target_size[1] // 2)

                # Crop and resize the image.py to the target size
                cropped_resized_image = image_read[crop_y1:crop_y2, crop_x1:crop_x2]
                cropped_resized_image = cv2.resize(cropped_resized_image, target_size)

                gray_image = cv2.cvtColor(cropped_resized_image, cv2.COLOR_BGR2GRAY)
                self.image_matrix = gray_image

                self.view.display_image(self.image_matrix, self.is_plot_export, "PNG image.py")
                self.imported_image = True
                print("Image loaded as a matrix")

    def upload_json(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("JSON (*.json)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.data = self.load_settings_from_json(file_path)
                # TODO handle error
                self.reload_view()
                self.update_view_input()

                self.view.popup_window("JSON Import Successful", "JSON settings imported successfully")

    def update_view_input(self):
        self.view.set_technology_label("Technology: " + str(self.technology_value) + " nm")

        self.view.set_input_Kn(str(self.Kn_value))
        self.view.set_input_Kp(str(self.Kp_value))
        self.view.set_input_beta(str(self.beta_value))
        self.view.set_input_Pl(str(self.Pl_value))
        self.view.set_input_voltage(str(self.voltage_value))
        self.view.set_input_pourcentage(str(self.noise_pourcentage))

        self.view.set_input_x(str(self.x_position))
        self.view.set_input_y(str(self.y_position))

        self.view.set_input_lam(str(self.lam_value))
        self.view.set_input_NA(str(self.NA_value))
        self.view.set_input_confocal(self.is_confocal)

        self.view.cell_selector.set_cell_name(str(self.cell_name))
        self.view.cell_selector.set_state_list(str(self.state_list))

    def upload_csv(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("CSV (*.csv)")

        if file_dialog.exec():  # Note the use of exec_() instead of exec()
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.dataframe = pd.read_csv(file_path)
                self.volage_column_dialog()

    def psf_xy(self, lam, na, x, y, xc, yc, radius_max=np.inf):

        def std_dev(std_lam, std_na):
            return 0.37 * std_lam / std_na

        r = np.sqrt(np.square(x - xc) + np.square(y - yc))
        ind = r <= radius_max

        y = 1 / np.sqrt(2 * np.pi * np.square(std_dev(lam, na))) * np.exp(
            -(np.square(x - xc) + np.square(y - yc)) / (2 * np.square(std_dev(lam, na))))

        # Clear values outside of radius_max
        y = y * ind

        return y

    def psf_2d_pos(self, fov, lam, na, xc, yc, clear_radius=np.inf):
        s_x, s_y = (fov, fov)  # mat.shape
        x, y = np.mgrid[0:s_x, 0:s_y]
        mat = self.psf_xy(lam, na, x, y, xc, yc, clear_radius)
        return mat

    def psf_2d(self, fov, lam, na, clear_radius=np.inf):
        s_x, s_y = (fov, fov)  # mat.shape
        xc = s_x // 2
        yc = s_y // 2
        return self.psf_2d_pos(fov, lam, na, xc, yc, clear_radius)

    def round(self, i):
        return int(np.rint(i))

    def draw_one_gate_layout(self, G1, draw_lam):

        layout_width = 3000
        layout_height = 3000

        layout = np.empty(shape=(layout_height, layout_width))
        layout.fill(0)

        x = self.round(2 * draw_lam)
        y = self.round(4 * draw_lam)

        start_x = (layout_width - x) // 2
        start_y = (layout_height - y) // 2

        layout[start_y:start_y + y, start_x:start_x + x] = G1

        return layout

    # TODO update sajjad code to be nicer and do not duplicate with the draw_one_gate_layout func
    def draw_layout(self, lam, G1, G2, Gap):
        layout = np.empty(shape=(1000, 1000))
        layout.fill(0)

        x = self.round(2 * lam)
        y = self.round(4 * lam)
        layout[0:x - 1, 0:y - 1].fill(0)

        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(G1)

        x = x + self.round(4 * lam)
        y = self.round(4 * lam)
        layout[x:x + self.round(12 * lam), 1:self.round(4 * lam)].fill(Gap)

        x = x + self.round(12 * lam)
        y = self.round(4 * lam)
        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(0)
        x = x + self.round(4 * lam)
        layout[x:x + self.round(2 * lam), 1:self.round(4 * lam)].fill(G2)

        # Try to center it in a larger field of view
        layout_full = np.empty(shape=(3000, 3000))
        layout_full.fill(0)
        offset = [1250, 1450]
        layout_full[offset[0]:offset[0] + layout.shape[0], offset[1]:offset[1] + layout.shape[1]] = layout

        return layout_full

    def parameters_init(self, Kn, Kp, voltage, beta, Pl):
        lam = self.technology_value / 2
        # RCV values
        G1 = voltage * Kn * beta * Pl
        G2 = voltage * Kp * beta * Pl
        Gap = 0
        return lam, G1, G2, Gap

    def calc_unique_rcv(self, voltage, L, old_G1, old_G2):

        # may be when the voltage is > 0,5 changing the gate state
        lam, G1, G2, Gap = self.parameters_init(self.Kn_value, self.Kp_value, voltage, self.beta_value, self.Pl_value)

        generated_gate_image = np.select([self.image_matrix == old_G1, self.image_matrix == old_G2], [G1, G2], self.image_matrix)

    # for preview in gui of current position of laser
        if voltage > self.max_voltage_high_gate_state:
            self.high_gate_state_layout = generated_gate_image
            self.max_voltage_high_gate_state = voltage

        amp_abs = np.sum(generated_gate_image * L)
        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser

        return amp_rel

    def update_cell_values(self):
        cell_name_value = self.view.cell_selector.get_cell_name()
        self.view.cell_selector.set_cell_name(str(cell_name_value))
        state_list_value = self.view.cell_selector.get_state_list()

        self.def_file = None

        if cell_name_value is not None and cell_name_value != "":
            self.cell_name = cell_name_value
        else:
            self.cell_name = "INV_X1"

        if state_list_value is not None and state_list_value != "":
            self.state_list = state_list_value
        else:
            self.state_list = "1"

        self.reload_view()

    def update_physics_values(self):

        self.imported_image = False

        Kn_input = self.view.get_input_Kn()
        Kp_input = self.view.get_input_Kp()
        beta_input = self.view.get_input_beta()
        Pl_input = self.view.get_input_Pl()
        voltage_input = self.view.get_input_voltage()
        pourcentage_input = self.view.get_input_pourcentage()

        # Check if the inputs are not null (not None) and not empty before converting to floats
        if Kn_input is not None and Kn_input != "":
            self.Kn_value = float(Kn_input)
        else:
            self.Kn_value = self.data["gate_config"]["Kn"]

        if Kp_input is not None and Kp_input != "":
            self.Kp_value = float(Kp_input)
        else:
            self.Kp_value = self.data["gate_config"]["Kp"]

        if beta_input is not None and beta_input != "":
            self.beta_value = float(beta_input)
        else:
            self.beta_value = self.data["gate_config"]["beta"]

        if Pl_input is not None and Pl_input != "":
            self.Pl_value = float(Pl_input)
        else:
            self.Pl_value = self.data["gate_config"]["Pl"]

        if voltage_input is not None and voltage_input != "":
            self.voltage_value = float(voltage_input)
        else:
            self.voltage_value = self.data["gate_config"]["voltage"]

        if pourcentage_input is not None and pourcentage_input != "":
            self.noise_pourcentage = int(pourcentage_input)
        else:
            self.noise_pourcentage = self.data["gate_config"]["noise_pourcentage"]

        self.reload_view()

    def calc_and_plot_RCV(self, offset=None):

        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal

        FWHM = 1.22 / np.sqrt(2) * lam / NA
        FOV = 3000
        if not offset:
            L = self.psf_2d(FOV, lam, NA, FWHM // 2 if is_confocal else np.inf)
        else:
            L = self.psf_2d_pos(FOV, lam, NA, offset[0], offset[1], FWHM // 2 if is_confocal else np.inf)

        amp_abs = np.sum(self.image_matrix * L)

        # This is only correct if the full laser spot is in L (if it is not truncated)
        # if is_confocal:
        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser
        self.main_label_value = "RCV (per nm²) = %.6f" % amp_rel

        return np.where(L > 0, 1, 0), L

    def update_rcv_position(self):
        x_input = self.view.get_input_x()
        y_input = self.view.get_input_y()

        if x_input is not None and x_input != "":
            self.x_position = int(x_input)
        else:
            self.x_position = self.data["laser_config"]["x_position"]

        if y_input is not None and y_input != "":
            self.y_position = int(y_input)
        else:
            self.y_position = self.data["laser_config"]["y_position"]

        if self.imported_image is False:
            self.update_settings()

        self.reload_view()

    def print_original_image(self):
        self.dataframe = None
        if self.imported_image:
            title = "PNG image.py"
        else:
            title = "Generated image.py"

        self.view.display_image(self.image_matrix, self.is_plot_export, title)

    def print_rcv_image(self):
        self.dataframe = None
        self.update_settings()
        points = np.where(self.image_matrix != 0, 1, 0)
        mask, _ = self.calc_and_plot_RCV(offset=[self.y_position, self.x_position])

        result = cv2.addWeighted(points, 1, mask, 0.5, 0)

        self.view.display_image(result, self.is_plot_export, self.main_label_value)

    def calc_and_plot_EOFM(self):
        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal
        FWHM = 1.22 / np.sqrt(2) * lam / NA
        FOV = 3000

        self.main_label_value = "FWHM = %.02f, is_confocal = %s" % (FWHM, is_confocal)

        return self.psf_2d(FOV, lam, NA, FWHM // 2 if is_confocal else np.inf)

    def print_EOFM_image(self):
        self.dataframe = None
        self.update_settings()
        L = self.calc_and_plot_EOFM()
        R = fftconvolve(self.image_matrix, L, mode='same')

        self.view.display_image(R, self.is_plot_export, "EOFM - " + self.main_label_value)
        inverted_image = np.abs(R)
        self.view.display_second_image(inverted_image, self.is_plot_export, "Absolute EOFM - " + self.main_label_value)

    def update_settings(self):
        lam_input = self.view.get_input_lam()
        NA_input = self.view.get_input_NA()
        confocal_input = self.view.get_input_confocal()

        if lam_input is not None and lam_input != "":
            self.lam_value = float(lam_input)
        else:
            self.lam_value = self.data["laser_config"]["lam"]

        if NA_input is not None and NA_input != "":
            self.NA_value = float(NA_input)
        else:
            self.NA_value = self.data["laser_config"]["NA"]

        if confocal_input is not None and confocal_input != "":
            self.is_confocal = bool(confocal_input)
        else:
            self.is_confocal = self.data["laser_config"]["is_confocal"]

    def print_psf(self):
        self.dataframe = None
        self.update_settings()
        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal

        FWHM = 1.22 / np.sqrt(2) * lam / NA
        FOV = 2000
        self.main_label_value = "FWHM = %.02f, is_confocal = %s" % (FWHM, is_confocal)
        L = self.psf_2d(FOV, lam, NA, FWHM // 2 if is_confocal else np.inf)
        self.view.display_image(L, self.is_plot_export, "LPS - " + self.main_label_value, True)

    def get_view(self):
        return self.view

    def plot_rcv_calc(self):
        self.app_state = 4
        self.max_voltage_high_gate_state = float('-inf')
        self.high_gate_state_layout = None

        selected_columns = self.selected_columns

        mask, L = self.calc_and_plot_RCV(offset=[self.y_position, self.x_position])

        _, old_G1, old_G2, _ = self.parameters_init(self.Kn_value, self.Kp_value, self.voltage_value, self.beta_value, self.Pl_value)

        self.dataframe['RCV'] = self.dataframe.apply(
            lambda row: self.calc_unique_rcv(row[selected_columns[1]], L, old_G1, old_G2), axis=1)

        if self.high_gate_state_layout is not None:
            points = np.where(self.high_gate_state_layout != 0, 1, 0)
            result = cv2.addWeighted(points, 1, mask, 0.5, 0)
            self.view.display_optional_image(result)

        self.view.plot_dataframe(self.dataframe, selected_columns)

    def volage_column_dialog(self):
        # Get the column names from the dataframe
        column_names = self.dataframe.columns.tolist()
        column_names_filtered = [col for col in column_names if col != "RCV"]

        # Create and show the column selection dialog
        dialog = ColumnSelectionDialog(column_names_filtered)
        if dialog.exec():
            self.selected_columns = dialog.get_selected_columns()

            threading.Thread(target=self.plot_rcv_calc_wrapper).start()

    def init_op_object(self):
        technology_dialog = TechnologySelectionDialog()
        if technology_dialog.exec():
            std_file, lib_file = technology_dialog.get_selected_technology()
            lib = gdspy.GdsLibrary()
            self.gds_cell_list = lib.read_gds(std_file).cells
            self.lib_reader = LibReader(lib_file)

        layer_dialog = LayerSelectionDialog()
        if layer_dialog.exec():
            self.selected_layer = layer_dialog.get_selected_layers()
            self.extract_op_cell(self.cell_name)

    def extract_op_cell(self, cell_name):
        for gds_cell_name, gds_cell in self.gds_cell_list.items():
            if gds_cell_name != cell_name:
                continue

            try:
                truth_table, voltage, input_names = self.lib_reader.extract_truth_table(gds_cell_name)
                self.op_master = Op(gds_cell_name, gds_cell, self.selected_layer, truth_table, voltage, input_names)

                self.object_storage_list[gds_cell_name] = {}

            except Exception as e:
                print(f"Error {e}")

    def apply_state_op(self, cell_input_string):
        draw_inputs = {}
        inputs_list = self.op_master.inputs_list

        cell_input = [int(char) for char in cell_input_string]

        if cell_input and len(cell_input) == len(inputs_list):
            for index, inp in enumerate(inputs_list):
                draw_inputs[inp] = cell_input[index]

            op_object = copy.deepcopy(self.op_master)
            op_object.apply_state(draw_inputs)

            if self.def_file is not None:
                op_object.calculate_orientations()

            self.object_storage_list[self.op_master.name][cell_input_string] = copy.deepcopy(op_object)
