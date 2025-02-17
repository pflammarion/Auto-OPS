import copy
import csv
import datetime
import itertools
import json
import os
import sys
import threading
import time
import random

import gdspy
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np
import pandas as pd

from controllers import def_parser, gui_parser
from controllers.GDS_Object.auto_ops_propagation import AutoOPSPropagation
from controllers.lib_reader import LibReader
from controllers.simulation import Simulation, benchmark_simulation_object, rcv_parameter, export_simulation_object
from views.dialogs.column_dialog import ColumnSelectionDialog
from views.dialogs.layer_list_dialog import LayerSelectionDialog
from views.main import MainView
from views.dialogs.technology_dialog import TechnologySelectionDialog

from prompt_toolkit import PromptSession
import subprocess


class MainController:
    def __init__(self, command_line, config, script=None):

        self.is_flip_flop = False
        self.merge = False
        self.script = script
        self.command_line = command_line

        self.merged_image_matrix = np.empty(shape=(3000, 3000))
        self.merged_image_matrix.fill(0)

        self.patch_counter = [1, 1]
        self.gds_cell_list = None
        self.lib_reader = None
        self.selected_layer = None
        self.propagation_master = None
        self.def_file = None
        self.vpi_extraction = None
        self.selected_area = 0
        self.selected_patch_size = 20

        self.state_list = ""
        self.cell_name = ""

        self.object_storage_list = {}

        self.imported_image = False

        # init all class variables
        self.technology_value = 45
        self.Kn_value = 1
        self.Kp_value = -1.3
        self.beta_value = 1
        self.Pl_value = 10E7
        self.voltage_value = 1.2
        self.noise_percentage = 5

        self.max_voltage_high_gate_state = float('-inf')
        self.high_gate_state_layout = None

        # to initialize the value and the rcv mask

        self.x_position = 1500
        self.y_position = 1500

        self.simulation = Simulation()

        self.flip_flop = None

        if config is None or config == "":
            config = "config/config.json"

        self.data = self.load_settings_from_json(config)

        if self.gds_cell_list is None or self.lib_reader is None or self.selected_layer is None and not command_line:
            self.init_propagation_object()

        if self.def_file is None:
            self.extract_op_cell(self.cell_name)

        self.dataframe = None

        self.selected_columns = None

        self.main_label_value = ""

        self.image_matrix = None

        self.app_state = 0

        if not command_line:
            self.view = MainView(self)
            self.view.set_technology_label("Technology: " + str(self.technology_value) + " nm")

            self._running = True

            self.is_plot_export = False

            self.reload_view()

        else:
            print("""
            
     █████  ██    ██ ████████  ██████         ██████  ██████  ███████ 
    ██   ██ ██    ██    ██    ██    ██       ██    ██ ██   ██ ██      
    ███████ ██    ██    ██    ██    ██ █████ ██    ██ ██████  ███████ 
    ██   ██ ██    ██    ██    ██    ██       ██    ██ ██           ██ 
    ██   ██  ██████     ██     ██████         ██████  ██      ███████ 
                                                            
            """)
            if self.script is None or script == "":
                session = PromptSession()
                while True:
                    user_input = session.prompt('auto_ops_gui> ')
                    self.process_command_line_mode(user_input)

            else:
                self.run_script()

    def process_command_line_mode(self, command):
        if command == "exit" or command == "quit":
            print("\nSee you soon!\n")
            sys.exit(0)
        elif command == "h" or command == "help":
            print("Help:\n"
                  "Commands available: info, update, rcv, plot, export.\n\n"
                  "info: To get the current variables information\n"
                  "update: {variable_name} {new_value} to update a variable with a new value\n"
                  "save: To save to save the propagation in the matrix•\n"
                  "merge To merge the propagation into the precedent matrix\n"
                  "reset: To reset the merged matrix to 0\n"
                  "rcv: To calculate the rcv value of the current matrix. You can use the {export} argument to save it in export/rcv.csv\n"
                  "plot: {original, rcv, psf, eofm{-abs}, save} to plot the matrix\n"
                  "export: To export the numpy array matrix\n"
                  "-----------------------------------------")

        elif command == "info":
            gui_parser.parse_info(self)
        elif command.startswith("update"):
            gui_parser.update_variable(self, command)
        elif command.startswith("rcv"):
            self.update_image_matrix()
            result, value, self.main_label_value = self.simulation.overlay_psf_rcv(
                self.image_matrix,
                self.x_position,
                self.y_position
            )
            _, variable = command.split(' ', 1)
            variable = variable.strip()

            print(value)

            if variable == "export":
                csv_file_path = os.path.join("export/rcv.csv")
                with open(csv_file_path, mode='a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(
                        [self.cell_name, self.state_list, self.flip_flop, self.x_position, self.y_position, value])
                print(f"Result saved in export/rcv.csv")

        elif command.startswith("plot"):
            variable = ""
            try:
                _, variable = command.split(' ', 1)
                variable = variable.strip()

            except ValueError:
                print("No Title set")

            value = ""
            result = None

            try:
                if variable == "rcv":
                    result, rcv_value = self.print_rcv_image()
                    value = f": {rcv_value}"

                elif variable == "eofm":
                    result = self.print_EOFM_image()

                elif variable == "eofm-abs":
                    result = np.abs(self.print_EOFM_image())

                elif variable == "psf":
                    result, self.main_label_value = self.print_psf()

                elif variable == "save" or self.image_matrix is None:
                    self.update_image_matrix()
                    result = self.image_matrix

                else:
                    result = self.image_matrix

            except ValueError:
                print("Error !")

            if result is None:
                print("No result plotted, verify your information or save them")
            else:
                gui_parser.plot(result, self, variable + value)

        elif command == "export":
            self.export_np_array()

        elif command == "save":
            self.update_image_matrix()

        elif command == "merge":
            self.merge_image_matrix()

        elif command == "reset":
            self.reset_merge_image_matrix()

        else:
            print("Command not found")

    def run_script(self):
        try:
            process = subprocess.Popen(['bash', self.script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                print("\nauto_ops_gui> " + line.strip())
                self.process_command_line_mode(line.strip())
            process.wait()

            if process.returncode != 0:
                print(f"Error executing script:\n{process.stderr.read()}")
            else:
                print("\nScript execution completed. Exiting.")
                sys.exit(0)
        except Exception as e:
            print(f"Error executing script: {e}")

    def stop_thread(self):
        self._running = False

    def merge_image_matrix(self):
        self.update_image_matrix()
        self.merged_image_matrix += np.where(self.merged_image_matrix == 0, self.image_matrix, 0)
        self.image_matrix = copy.deepcopy(self.merged_image_matrix)

    def reset_merge_image_matrix(self):
        self.merged_image_matrix = np.empty(shape=(3000, 3000))
        self.merged_image_matrix.fill(0)
        self.reload_view()

    def reload_view(self):
        threading.Thread(target=self.reload_view_wrapper).start()

    def update_image_matrix(self):
        if not self.imported_image:
            G1 = rcv_parameter(self.Kn_value, self.voltage_value, self.beta_value, self.Pl_value)
            G2 = rcv_parameter(self.Kp_value, self.voltage_value, self.beta_value, self.Pl_value)
            if self.cell_name is not None and self.cell_name != "" or self.def_file is not None:
                if self.def_file is not None:
                    self.image_matrix, self.simulation.nm_scale = benchmark_simulation_object(self.object_storage_list,
                                                                                              self.def_file, G1, G2,
                                                                                              self.simulation.FOV,
                                                                                              self.vpi_extraction,
                                                                                              self.selected_area,
                                                                                              nm_scale=self.simulation.nm_scale)
                else:
                    if self.cell_name not in self.object_storage_list.keys():
                        self.extract_op_cell(self.cell_name)

                    if self.state_list not in self.object_storage_list[self.cell_name].keys():
                        self.apply_state_propagation(self.state_list, self.flip_flop)

                    if self.is_flip_flop:
                        # format of key for a flip-flop is "inputs_output" -> "01010_1"
                        cell_input_string = self.state_list + "_" + str(self.flip_flop)
                    else:
                        cell_input_string = self.state_list
                    propagation_object = self.object_storage_list[self.cell_name][cell_input_string]
                    self.image_matrix, self.simulation.nm_scale = export_simulation_object(
                        propagation_object,
                        G1, G2, self.simulation.FOV,
                        nm_scale=self.simulation.nm_scale)

            else:

                self.image_matrix = self.draw_layout(self.technology_value / 2, G1, G2, 0)

    def reload_view_wrapper(self):
        self.simulation.nm_scale = 2
        self.view.set_footer_label("... Loading ...")
        start = time.time()

        if self.merge:
            self.merge_image_matrix()
        else:
            self.update_image_matrix()

        self.merge = False

        if self.app_state == 1:
            L = self.print_psf()
            self.view.display_image(L, self.is_plot_export, "LPS - " + self.main_label_value, True)

        elif self.app_state == 2:
            result, _ = self.print_rcv_image()
            self.view.display_image(result, self.is_plot_export, self.main_label_value)

        elif self.app_state == 3:
            R = self.print_EOFM_image()
            self.view.display_image(R, self.is_plot_export, "EOFM - " + self.main_label_value)
            inverted_image = np.abs(R)
            self.view.display_second_image(inverted_image, self.is_plot_export,
                                           "Absolute EOFM - " + self.main_label_value)

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
                    self.simulation.lam_value = data["laser_config"]["lamda"]
                    self.simulation.NA_value = data["laser_config"]["NA"]
                    self.simulation.is_confocal = data["laser_config"]["is_confocal"]
                    self.x_position = data["laser_config"]["x_position"]
                    self.y_position = data["laser_config"]["y_position"]
                if "gate_config" in data:
                    self.technology_value = data["gate_config"]["technology"]
                    self.Kn_value = data["gate_config"]["Kn"]
                    self.Kp_value = data["gate_config"]["Kp"]
                    self.beta_value = data["gate_config"]["beta"]
                    self.Pl_value = data["gate_config"]["Pl"]
                    self.voltage_value = data["gate_config"]["voltage"]
                    self.noise_percentage = data["gate_config"]["noise_percentage"]

                if "op_config" in data:
                    std_file = data["op_config"]["std_file"]
                    lib_file = data["op_config"]["lib_file"]
                    def_file = data["op_config"]["def_file"]
                    vpi_file = data["op_config"]["vpi_file"]

                    selected_area = data["op_config"]["selected_area"]
                    if selected_area is not None and selected_area != "":
                        self.selected_area = int(selected_area)

                    selected_patch_size = data["op_config"]["selected_patch_size"]
                    if selected_patch_size is not None and selected_patch_size != "":
                        self.selected_patch_size = int(selected_patch_size)

                    lib = gdspy.GdsLibrary()

                    self.gds_cell_list = lib.read_gds(std_file).cells

                    self.lib_reader = LibReader(lib_file)
                    self.selected_layer = data["op_config"]["layer_list"]

                    if vpi_file is not None and vpi_file != "":
                        self.vpi_extraction = {}
                        with open(vpi_file, 'r') as file:
                            for line in file:
                                key, inputs, outputs = line.strip().split(',')
                                self.vpi_extraction[key] = {'inputs': inputs, 'outputs': outputs}

                    if def_file is not None and def_file != "":
                        self.def_file = def_parser.get_gates_info_from_def_file(def_file, self.selected_patch_size)
                        cell_name_list = self.def_file[2]
                        self.patch_counter = self.def_file[3]
                        for cell_name in cell_name_list:
                            self.extract_op_cell(cell_name)
                            combinations = list(
                                itertools.product([0, 1], repeat=len(self.propagation_master.inputs_list)))
                            for input_combination in combinations:
                                input_str = ''.join(map(str, input_combination))
                                self.apply_state_propagation(input_str, 0)
                                if self.is_flip_flop:
                                    self.apply_state_propagation(input_str, 1)

                return data

            except Exception as e:
                print(f"Error loading JSON data: {e}")
        else:
            print(f"JSON file '{json_file_path}' does not exist.")

    def patch_matrix_preview(self):

        layout = np.empty(shape=(1000, 1000))
        layout.fill(0)

        patch_size = 1000 / max(self.patch_counter)
        patch_counter = 0
        for i in range(0, self.patch_counter[1]):
            for j in range(0, self.patch_counter[0]):

                value = 0.5

                if patch_counter == self.selected_area:
                    value = 1

                patch_counter += 1

                x = j * patch_size
                y = i * patch_size

                x_start, x_end = int(x), int(x + patch_size)
                y_start, y_end = int(y), int(y + patch_size)

                layout[y_start:y_end, x_start:x_end] = value

        self.view.display_optional_image(layout, f"Selected Patch N°{self.selected_area}/{patch_counter - 1}", False)

    # TODO update this save
    def save_settings_to_json(self):
        json_data = {
            "technology": self.technology_value,
            "laser_config": {
                "lamda": self.simulation.lam_value,
                "NA": self.simulation.NA_value,
                "is_confocal": self.simulation.is_confocal,
                "x_position": self.x_position,
                "y_position": self.y_position
            },
            "gate_config": {
                "Kn": self.Kn_value,
                "Kp": self.Kp_value,
                "beta": self.beta_value,
                "Pl": self.Pl_value,
                "voltage": self.voltage_value,
                "noise_percentage": self.noise_percentage
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

    def export_np_array(self):
        start = time.time()

        if self.cell_name != "":
            name = self.cell_name
            if self.state_list is not None:
                name += "_" + str(self.state_list)
        else:
            name = "numpyarray"

        current_time = datetime.datetime.now()
        timestamp_string = current_time.strftime("%Y%m%d%H%M%S")
        random_number = random.randint(0, 100)

        name += "_" + str(timestamp_string) + "_" + str(random_number)

        np.save(f'export/np_arrays/{name}.npy', self.image_matrix)

        message = f"Numpy array exported successfully in 'export/np_arrays/{name}.npy'"

        if not self.command_line:
            self.view.popup_window("Export Successful", message)

            end = time.time()
            self.view.set_footer_label(f"Execution time for NP array export: {end - start:.2f} seconds")
        else:
            print(message)

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
        # TODO delete safely this function
        self.view.set_technology_label("Technology: " + str(self.technology_value) + " nm")

        self.view.cell_selector.set_cell_name(str(self.cell_name))
        self.view.cell_selector.set_state_list(str(self.state_list))

        self.view.update_inputs_values()

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

    def round(self, i):
        return int(np.rint(i))

    def draw_layout(self, lam, G1, G2, Gap):
        layout = np.empty(shape=(1000, 1000))
        layout.fill(0)

        x = self.round(2 * lam)
        y = self.round(4 * lam)
        layout[0:x - 1, 0:y - 1].fill(0)

        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(G1)

        x = x + self.round(4 * lam)
        layout[x:x + self.round(12 * lam), 1:self.round(4 * lam)].fill(Gap)

        x = x + self.round(12 * lam)
        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(0)
        x = x + self.round(4 * lam)
        layout[x:x + self.round(2 * lam), 1:self.round(4 * lam)].fill(G2)

        # Try to center it in a larger field of view
        layout_full = np.empty(shape=(3000, 3000))
        layout_full.fill(0)
        offset = [1250, 1450]
        layout_full[offset[0]:offset[0] + layout.shape[0], offset[1]:offset[1] + layout.shape[1]] = layout

        return layout_full

    def calc_unique_rcv(self, voltage, L, old_G1, old_G2):

        # may be when the voltage is > 0,5 changing the gate state
        G1 = rcv_parameter(self.Kn_value, self.voltage_value, self.beta_value, self.Pl_value)
        G2 = rcv_parameter(self.Kp_value, self.voltage_value, self.beta_value, self.Pl_value)

        generated_gate_image = np.select([self.image_matrix == old_G1, self.image_matrix == old_G2], [G1, G2],
                                         self.image_matrix)

        # for preview in gui of current position of laser
        if voltage > self.max_voltage_high_gate_state:
            self.high_gate_state_layout = generated_gate_image
            self.max_voltage_high_gate_state = voltage

        amp_abs = np.sum(generated_gate_image * L)
        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser

        return amp_rel

    def update_cell_values(self, merge=False):
        cell_name_value = self.view.cell_selector.get_cell_name()
        self.view.cell_selector.set_cell_name(str(cell_name_value))
        state_list_value = self.view.cell_selector.get_state_list()

        self.def_file = None
        self.merge = merge

        if cell_name_value is not None and cell_name_value != "":
            self.cell_name = cell_name_value
        else:
            self.cell_name = ""

        if state_list_value is not None and state_list_value != "":
            self.state_list = state_list_value
        else:
            self.state_list = "1"

        self.reload_view()

    def update_physics_values(self):

        self.imported_image = False

        input_values = self.view.gate_layout.get_input_values()
        Kn_input = input_values['Kn_value']
        Kp_input = input_values['Kp_value']
        beta_input = input_values['beta_value']
        Pl_input = input_values['Pl_value']
        voltage_input = input_values['voltage_value']
        pourcentage_input = input_values['noise_percentage']

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
            self.noise_percentage = int(pourcentage_input)
        else:
            self.noise_percentage = self.data["gate_config"]["noise_percentage"]

        self.reload_view()

    def update_rcv_position(self):
        input_values = self.view.laser_position_layout.get_input_values()
        x_input = input_values['input_x']
        y_input = input_values['input_y']

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
        self.patch_matrix_preview()

    def print_rcv_image(self):
        self.dataframe = None

        if not self.command_line:
            self.update_settings()

        result, value, self.main_label_value = self.simulation.overlay_psf_rcv(self.image_matrix, self.x_position,
                                                                               self.y_position)

        return result, value

    def print_EOFM_image(self):
        self.dataframe = None

        if not self.command_line:
            self.update_settings()

        R, self.main_label_value = self.simulation.print_EOFM_image(self.image_matrix)

        return R

    def update_settings(self):
        laser_values = self.view.laser_layout.get_laser_values()
        lam_input = laser_values['lam_value']
        NA_input = laser_values['NA_value']
        confocal_input = laser_values['is_confocal']

        if lam_input is not None and lam_input != "":
            self.simulation.lam_value = float(lam_input)
        else:
            self.simulation.lam_value = self.data["laser_config"]["lam"]

        if NA_input is not None and NA_input != "":
            self.simulation.NA_value = float(NA_input)
        else:
            self.simulation.NA_value = self.data["laser_config"]["NA"]

        if confocal_input is not None and confocal_input != "":
            self.simulation.is_confocal = bool(confocal_input)
        else:
            self.simulation.is_confocal = self.data["laser_config"]["is_confocal"]

    def print_psf(self):
        self.dataframe = None
        if not self.command_line:
            self.update_settings()

        L, self.main_label_value = self.simulation.get_psf(FOV=3000)

        return L

    def get_view(self):
        return self.view

    def plot_rcv_calc(self):
        self.app_state = 4
        self.max_voltage_high_gate_state = float('-inf')
        self.high_gate_state_layout = None

        selected_columns = self.selected_columns

        mask, L, _, _ = self.simulation.calc_RCV(self.image_matrix, offset=[self.y_position, self.x_position])

        old_G1 = rcv_parameter(self.Kn_value, self.voltage_value, self.beta_value, self.Pl_value)
        old_G2 = rcv_parameter(self.Kp_value, self.voltage_value, self.beta_value, self.Pl_value)

        self.dataframe['RCV'] = self.dataframe.apply(
            lambda row: self.calc_unique_rcv(row[selected_columns[1]], L, old_G1, old_G2), axis=1)

        if self.high_gate_state_layout is not None:
            points = np.where(self.high_gate_state_layout != 0, 1, 0)
            result = cv2.addWeighted(points, 1, mask, 1, 0)
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

    def init_propagation_object(self):
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

            self.is_flip_flop = False
            try:
                truth_table, voltage, input_names, self.is_flip_flop = self.lib_reader.extract_truth_table(
                    gds_cell_name)
                self.propagation_master = AutoOPSPropagation(gds_cell_name, gds_cell, self.selected_layer, truth_table,
                                                             voltage, input_names)

                self.object_storage_list[gds_cell_name] = {}

            except Exception as e:
                print(f"Error {e}")

    def apply_state_propagation(self, cell_input_string, flip_flop):
        draw_inputs = {}
        inputs_list = self.propagation_master.inputs_list

        cell_input = [int(char) for char in cell_input_string]

        if cell_input and len(cell_input) == len(inputs_list):
            for index, inp in enumerate(inputs_list):
                draw_inputs[inp] = cell_input[index]

            propagation_object = copy.deepcopy(self.propagation_master)
            propagation_object.apply_state(draw_inputs, flip_flop)

            if self.def_file is not None:
                propagation_object.calculate_orientations()

            if self.is_flip_flop:
                # format of key for a flip-flop is "inputs_output" -> "01010_1"
                cell_input_string = cell_input_string + "_" + str(flip_flop)

            self.object_storage_list[self.propagation_master.name][cell_input_string] = copy.deepcopy(
                propagation_object)
