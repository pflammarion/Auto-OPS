import pytest
from datetime import datetime
import json
import re
import time

import numpy as np

from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.auto_ops_propagation import AutoOPSPropagation
from controllers.GDS_Object.shape import Shape
import pandas as pd
import matplotlib.pyplot as plt

from controllers.GDS_Object.type import ShapeType


def plot_elements(propagation_object) -> None:
    """
    Plots elements based on their coordinates and types.

    This function iterates through a list of elements and plots them accordingly.
    If the element is of type 'Label', it is plotted as a point with an annotation
    representing its name. If the element is not of type 'Label', it is plotted as a line.

    Parameters:
    -----------
    propagation_object: AutoOPSPropagation
        AutoOPS object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur.
    """
    for element in propagation_object.element_list:
        x, y = element.coordinates
        if isinstance(element, Label):
            plt.scatter(x, y)
            plt.annotate(element.name, (x, y))
        else:
            plt.plot(x, y)

    plt.title(propagation_object.name)
    plt.show()


def plot_reflection(propagation_object) -> None:
    """
    Plots reflection zones based on their coordinates and state.

    This function iterates through a list of diffusion shapes and reflection zones and plots them accordingly.
    If a diffusion part in P_MOS, the states reflection are unversed because of reflection physical behaviour.

    Parameters:
    -----------
    propagation_object: AutoOPSPropagation
        AutoOPS Propagation object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If a zone state is None, an exception is raised with the gate name.
    """
    color_list = ['black', 'white']
    fig, ax = plt.subplots()
    for reflection in propagation_object.reflection_list:
        x, y = reflection.polygon.exterior.xy
        plt.plot(x, y)

        for zone in reflection.zone_list:
            x, y = zone.coordinates
            ax.scatter(x, y, marker='o')
            state = zone.state
            if reflection.shape_type == ShapeType.PMOS:
                if state is None:
                    reflect = False
                else:
                    reflect = not state
            else:
                reflect = state

            if bool(reflect):
                ax.fill(x, y, facecolor=color_list[state], alpha=0.2, edgecolor='black', linewidth=1)

    plt.title(propagation_object.name)
    plt.show()


def plot_show_case(propagation_object) -> None:
    """
    Plots elements based on their coordinates and types.

    This function iterates through a list of elements and plots them accordingly.
    If the element is of type 'Label', it is plotted as a point with an annotation
    representing its name. If the element is not of type 'Label', it is plotted as a line.

    Parameters:
    -----------
    propagation_object: AutoOPSPropagation
        AutoOPS object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If a zone state is None, an exception is raised with the gate name.
    """
    for element in propagation_object.element_list:
        x, y = element.coordinates

        color = "black"
        alpha = 0.4

        if isinstance(element, Shape):
            if element.shape_type == ShapeType.DIFFUSION:
                # light red
                color = (1.0, 0.6, 0.6)
            elif element.shape_type == ShapeType.NWELL:
                color = "green"
                alpha = 0
            elif element.shape_type == ShapeType.POLYSILICON:
                color = "green"
                alpha = 0.2
            elif element.shape_type == ShapeType.METAL:
                if isinstance(element.attribute, Attribute):
                    if element.attribute.shape_type == ShapeType.VSS:
                        # blue
                        color = (110 / 255, 140 / 255, 255 / 255)
                    elif element.attribute.shape_type == ShapeType.VDD:
                        # blue
                        color = (110 / 255, 140 / 255, 255 / 255)

                    elif element.attribute.shape_type == ShapeType.OUTPUT:
                        color = "lightblue"
                    elif element.attribute.shape_type == ShapeType.INPUT:
                        color = "yellow"
                        alpha = 1

            plt.plot(x, y, color=color)
            plt.fill(x, y, color=color, alpha=alpha)

        elif isinstance(element, Label):
            plt.scatter(x, y, color="black")
            plt.annotate(element.name, (x, y))

    plt.title(propagation_object.name)
    path_name = "tmp/" + propagation_object.name
    plt.savefig(path_name)
    plt.close()


def count_unknown_states(propagation_object) -> None:
    state_counter = 0
    for reflection in propagation_object.reflection_list:
        for zone in reflection.zone_list:
            if zone.state is None:
                state_counter += 1

    print(
        f"\033[1;33m \n {propagation_object.name}, {propagation_object.inputs}, None states = {state_counter}, "
        f"Loop counter = {propagation_object.loop_counter}")


def benchmark(object_list, def_extract, plot, vpi_extraction=None) -> None:
    ur_x = def_extract[0]["ur_x"]
    ll_x = def_extract[0]["ll_x"]
    ur_y = def_extract[0]["ur_y"]
    ll_y = def_extract[0]["ll_y"]

    # plt.figure(figsize=(8, 8))

    if plot:
        plt.gca().set_facecolor('black')
        plt.gca().set_aspect('equal', adjustable='box')

        plt.xlim(ll_x - 1, ur_x + 1)
        plt.ylim(ll_y - 1, ur_y + 1)

    for i in range(len(def_extract[1])):
        def_zone = def_extract[1][i]
        if plot:
            plt.pause(0.0001)
            plt.draw()

        for cell_name, cell_place in def_zone['gates'].items():
            if cell_name in object_list.keys():
                for position in cell_place:
                    if vpi_extraction:
                        propagation_object = vpi_object_extractor(object_list[cell_name], cell_name, vpi_extraction,
                                                                  position)
                    else:
                        key = list(object_list[cell_name].keys())[0]
                        propagation_object = object_list[cell_name][key]

                    for zone in propagation_object.orientation_list[position['Orientation']]:
                        x, y = zone["coords"]
                        x_adder, y_adder = position['Coordinates']
                        x = tuple([element + x_adder for element in x])
                        y = tuple([element + y_adder for element in y])

                        state = zone["state"]

                        if zone["diff_type"] == ShapeType.PMOS:
                            if state is None:
                                reflect = False
                            else:
                                reflect = not state
                        else:
                            reflect = state
                        if bool(reflect) and plot:
                            plt.fill(x, y, facecolor='white', alpha=1)

    if plot:
        plt.show()


def vpi_object_extractor(cell_object, cell_name, vpi_extraction, position) -> AutoOPSPropagation:
    try:
        input_combination = vpi_extraction[position['GateID']]['inputs']
        output_combination = vpi_extraction[position['GateID']]['outputs']
        if len(output_combination):
            input_combination = input_combination + "_" + output_combination

        propagation_object = cell_object[input_combination]
    except KeyError as key_error:
        key = list(cell_object.keys())[0]
        propagation_object = cell_object[key]
        print(f"KeyError: {key_error}. Default gate applied for {cell_name}, {position['Coordinates']}")
    except IndexError as index_error:
        key = list(cell_object.keys())[0]
        propagation_object = cell_object[key]
        print(f"IndexError: {index_error}. Default gate applied for {cell_name}, {position['Coordinates']}")
    except Exception as e:
        key = list(cell_object.keys())[0]
        propagation_object = cell_object[key]
        print(f"An unexpected error occurred: {e}. Default gate applied for {cell_name}, {position['Coordinates']}")

    return propagation_object


def benchmark_export_data(def_extract, ex_time, def_name):
    number_op_coord = 0
    ll_x = def_extract[0]["ll_x"]
    ur_x = def_extract[0]["ur_x"]
    ll_y = def_extract[0]["ll_y"]
    ur_y = def_extract[0]["ur_y"]

    area_square_meters = round((ur_x - ll_x) * (ur_y - ll_y), 2)

    for cell_name, cell in def_extract[1].items():
        number_op_coord += len(cell)

    with open('benchmarks.log', 'a') as f:
        execution_time = round(ex_time, 4)
        f.write(
            f"& {def_name} & & & {len(def_extract[2])} & {number_op_coord} & {area_square_meters} & {execution_time} \\\\ \cline{{2-8}} \n")
        # f.write(f"{def_name} & {execution_time} \\\\ \cline{{2-8}} \n")


def test_orientation(propagation_object):
    orientation_list = ["N", "FN", "E", "FE", "S", "FS", "W", "FW"]
    # orientation_list = ["S", "FS"]
    for orientation in orientation_list:
        for zone in propagation_object.orientation_list[orientation]:
            x, y = zone["coords"]
            state = zone["state"]
            if zone["diff_type"] == ShapeType.PMOS:
                if state is None:
                    reflect = False
                else:
                    reflect = not state
            else:
                reflect = state

            if bool(reflect):
                plt.fill(x, y, facecolor="black", alpha=1, edgecolor='grey', linewidth=1)
            else:
                plt.fill(x, y, facecolor="grey", alpha=1, edgecolor='grey', linewidth=1)

        file_name = str(propagation_object.name) + "__" + orientation
        path_name = "tmp/" + file_name + ".svg"
        plt.title(file_name)
        plt.savefig(path_name, format='svg')
        plt.close()


def export_reflection_to_png(propagation_object) -> None:
    """
    Export as a PNG the reflection zones based on their coordinates and state.
    The title of the figure is defined from the gate name, inputs names, and inputs states.
    The file name is the same as the figure name. The output folder is ./tmp by default.

    This function iterates through a list of diffusion shapes and reflection zones and plots them accordingly.
    If a diffusion part in P_MOS, the states reflection are unversed because of reflection physical behaviour.
    Waring, compared to plot_reflection() the reflection is in black else is white for a better readable output.

    Parameters:
    -----------
    propagation_object: AutoOPSPropagation
        AutoOPS object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If a zone state is None, an exception is raised with the gate name.

    Note:
    -----
    Ensure that the 'tmp' directory exists before calling this function,
    as it will attempt to write the PNG file to this location.
    """
    color_list = ['white', 'black']
    for reflection in propagation_object.reflection_list:
        for zone in reflection.zone_list:
            x, y = zone.coordinates
            state = zone.state
            if reflection.shape_type == ShapeType.PMOS:
                if state is None:
                    reflect = False
                else:
                    reflect = not state
            else:
                reflect = state

            if bool(reflect):
                plt.fill(x, y, facecolor=color_list[state], alpha=1, edgecolor='grey', linewidth=1)

    string_list = [f"{key}_{value}" for key, value in sorted(propagation_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(propagation_object.name) + "__" + result_string
    path_name = "tmp/" + file_name
    plt.title(file_name)
    plt.savefig(path_name)
    plt.close()


def export_reflection_to_png_over_gds_cell(propagation_object, reflection_draw=False, with_axes=True,
                                           flip_flop=None) -> None:
    plt.figure(figsize=(6, 8))

    for element in propagation_object.element_list:
        x, y = element.coordinates

        color = "grey"
        edge_color = "black"
        background_color = "grey"
        alpha = 0.4
        text = ""

        if isinstance(element, Shape):
            if element.shape_type == ShapeType.DIFFUSION:
                # light red
                color = (1.0, 0.6, 0.6)
            elif element.shape_type == ShapeType.NWELL:
                color = "green"
                alpha = 0
            elif element.shape_type == ShapeType.POLYSILICON:
                color = "green"
                alpha = 0.2
            elif element.shape_type == ShapeType.METAL:
                if isinstance(element.attribute, Attribute):
                    if element.attribute.shape_type == ShapeType.VSS:
                        # blue
                        color = (110 / 255, 140 / 255, 255 / 255)
                    elif element.attribute.shape_type == ShapeType.VDD:
                        # blue
                        color = (110 / 255, 140 / 255, 255 / 255)

                    elif element.attribute.shape_type == ShapeType.OUTPUT:
                        color = "lightblue"
                    elif element.attribute.shape_type == ShapeType.INPUT:
                        color = "yellow"
                        alpha = 1

            plt.plot(x, y, color=color)
            plt.fill(x, y, color=color, alpha=alpha)

        elif isinstance(element, Label):
            if element.name in propagation_object.truthtable.keys():
                for outputs in propagation_object.truthtable:
                    for truthtable_inputs, output in propagation_object.truthtable[outputs]:
                        if element.name in output and truthtable_inputs == propagation_object.inputs:
                            if any("CK" in name or "RESET" in name or "GATE" in name or "CLK" in name for name in
                                   list(propagation_object.inputs.keys())) or "Q" in outputs:
                                if "N" in str(element.name):
                                    # if None this will be 1 and the else 0
                                    value = int(bool(not flip_flop))
                                else:
                                    value = int(bool(flip_flop))
                                text = str(element.name) + " = " + str(value)
                            else:
                                text = str(element.name) + " = " + str(int(output[element.name]))
                            edge_color = 'lightblue'
                            background_color = (228 / 255, 239 / 255, 255 / 255)

            elif element.name in propagation_object.inputs.keys():
                text = str(element.name) + " = " + str(int(propagation_object.inputs[element.name]))
                background_color = 'yellow'
            else:
                edge_color = (110 / 255, 140 / 255, 255 / 255)
                background_color = (200 / 255, 206 / 255, 247 / 255)

                if element.name == "VSS":
                    text = "Vss"
                elif element.name == "VDD":
                    text = "Vdd"
                else:
                    text = element.name

            plt.annotate(text, (x, y),
                         bbox=dict(facecolor=background_color, edgecolor=edge_color, boxstyle='round,pad=0.2',
                                   linewidth=2),
                         color='black', fontsize=18)
            # , fontname='Times New Roman'

    for via in propagation_object.via_element_list:
        x, y = via.coordinates
        plt.plot(x, y, color='none')
        plt.fill(x, y, color="white", alpha=0.8)

    if reflection_draw:
        for reflection in propagation_object.reflection_list:
            for zone in reflection.zone_list:
                x, y = zone.coordinates
                state = zone.state
                if reflection.shape_type == ShapeType.PMOS:
                    if state is None:
                        reflect = None
                    else:
                        reflect = not state
                else:
                    reflect = state

                if bool(reflect):
                    plt.fill(x, y, facecolor="none", edgecolor="black", hatch='////', alpha=0.8)

                if reflect is None:
                    plt.fill(x, y, facecolor="none", edgecolor="red", hatch='////', alpha=0.8)

    string_list = [f"{key}_{value}" for key, value in sorted(propagation_object.inputs.items())]
    result_string = "_".join(string_list)
    if flip_flop is not None:
        result_string += "_" + "Q_" + str(flip_flop)
    file_name = str(propagation_object.name) + "_overlay__" + result_string + ".svg"
    path_name = "tmp/" + file_name

    if with_axes:
        plt.title(file_name)
        plt.savefig(path_name)
    else:
        plt.axis('off')
        plt.savefig(path_name, bbox_inches='tight', pad_inches=0, format='svg')
    plt.close()


def unit_test(processed_cells, unit_test_technology):
    reset_color = "\033[0m"
    green_color = "\033[1;32m"
    red_color = "\033[1;31m"

    test_length = len(processed_cells.keys())
    test_counter = 0
    reference_file = f'test/{str(unit_test_technology)}nm.json'
    differences_list = []

    with open(reference_file, 'r') as ref:
        ref_data = json.load(ref)

    for cell_name, states_list in processed_cells.items():
        test_counter += 1

        reflection_list = True
        differences_found = False

        if cell_name not in ref_data:
            print(
                f"{red_color}{test_counter}/{test_length} Failure: "
                f"Key '{cell_name}' not found in generated file.{reset_color}")

            differences_found = True

        for state_index, state in enumerate(states_list):
            zone_counter = 0

            if len(state.reflection_list) == 0:
                # to ignore fill and antenna cells
                if "fill" not in cell_name.lower() and "antenna" not in cell_name.lower():
                    reflection_list = False
                    continue

            for ref_index, reflection in enumerate(state.reflection_list):
                for zone_index, zone in enumerate(reflection.zone_list):
                    coordinates = [(x, y) for x, y in zip(*zone.coordinates)]
                    zone_type = str(zone.shape_type)
                    zone_state = zone.state

                    if (
                            cell_name in ref_data
                            and state_index < len(ref_data[cell_name])
                            and zone_counter < len(ref_data[cell_name][state_index])
                            and 'state' in ref_data[cell_name][state_index][zone_counter]
                            and 'type' in ref_data[cell_name][state_index][zone_counter]
                            and (
                            ref_data[cell_name][state_index][zone_counter]['state'] != zone_state
                            or ref_data[cell_name][state_index][zone_counter]['type'] != zone_type
                    )
                    ):
                        differences_found = True

                    zone_counter += 1

        if not reflection_list:
            print(
                f"{red_color}{test_counter}/{test_length} Failure: "
                f"Reflection list empty for '{cell_name}'{reset_color}")

            differences_list.append(cell_name)

        elif not differences_found:
            print(f"{green_color}{test_counter}/{test_length} Test Passed for '{cell_name}'.{reset_color}")
        else:
            print(
                f"{red_color}{test_counter}/{test_length} Failure: "
                f"Type or state mismatch for '{cell_name}'{reset_color}")

            differences_list.append(cell_name)

    if len(differences_list) == 0:
        print(f"\n{green_color}------------------------------")
        print(f"Success: All tests passed !")
        print(f"------------------------------{reset_color}")
    else:
        print(f"\n{red_color} {len(differences_list)}/{test_length} Test failure check logs{reset_color}\n\n")
        pytest.fail("Test failure. Check logs for details.")


def unit_test_generator(processed_cells):
    json_test = {}

    for cell_name, states_list in processed_cells.items():
        json_test[cell_name] = []
        for state_index, state in enumerate(states_list):
            state_data = []
            for reflection in state.reflection_list:
                for zone in reflection.zone_list:
                    coordinates = [(x, y) for x, y in zip(*zone.coordinates)]
                    zone_type = str(zone.shape_type)
                    zone_state = zone.state
                    state_data.append({'type': zone_type, 'state': zone_state, 'coordinates': coordinates})
            json_test[cell_name].append(state_data)

    with open('test/tmp.json', 'w') as json_file:
        json.dump(json_test, json_file, indent=4)


def export_reflection_to_json(propagation_object) -> None:
    """
    This function retrieves reflection data from the propagation_object and exports it to a JSON file.
    It constructs a dictionary 'data' containing cell_name, inputs, and reflection information. The 'reflection'
    key in 'data' stores a list of reflections, each having a 'type' and a list of 'zone_list' elements.

    'zone_list' contains dictionaries for each zone, including 'type', 'state', and 'coordinates' for the zone.
    The method constructs a file name using 'gate_name' and 'inputs', then saves the data in JSON format to a file
    in the 'tmp' directory.

    The file name is defined from the gate name, inputs names, and inputs states.

    Parameters:
    -----------
    propagation_object: AutoOPSPropagation
        AutoOPS object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur during file handling or JSON writing.

    Note:
    -----
    Ensure that the 'tmp' directory exists before calling this method,
    as it will attempt to write the JSON file to this location.

    """

    data = {'cell_name': propagation_object.name, 'inputs': propagation_object.inputs, 'reflection': []}
    for diffusion in propagation_object.reflection_list:

        ref_type = str(diffusion.shape_type)
        zone_list = []

        for zone in diffusion.zone_list:
            coordinates = [(x, y) for x, y in zip(*zone.coordinates)]
            state = zone.state
            zone_type = str(zone.shape_type)
            zone_list.append({'type': zone_type, 'state': state, 'coordinates': coordinates})

        data['reflection'].append({'type': ref_type, 'zone_list': zone_list})

    string_list = [f"{key}_{value}" for key, value in sorted(propagation_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(propagation_object.name) + "__" + result_string + ".json"
    path_name = "tmp/" + file_name

    with open(path_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def data_export_csv(cell_name, time_extraction, cumulative_time_op, propagation_object, hand_input):
    current_date = datetime.now().strftime('%Y-%m-%d_%H')
    filename = f"tmp/export_{current_date}.csv"

    suffix_number = np.nan
    prefix_name = np.nan
    prefix_number = np.nan

    number_of_zone = 0
    for diff in propagation_object.reflection_list:
        number_of_zone += len(diff.zone_list)

    number_of_input = len(propagation_object.inputs.keys())

    avg_time_op = cumulative_time_op / 2 ** number_of_input

    suffix_number_match = re.search(r'(\d+)$', cell_name)
    if suffix_number_match:
        suffix_number = int(suffix_number_match.group(1))

    prefix_number_match = re.search(r'(\d+)_X', cell_name)
    if prefix_number_match:
        prefix_number = int(prefix_number_match.group(1))

    prefix_name_match = re.search(r'^([A-Za-z]+)', cell_name)
    if prefix_name_match:
        prefix_name = prefix_name_match.group(1)

    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=['cell_name', 'time_extraction', 'number_of_zone', 'number_of_input', 'suffix_number',
                     'prefix_name', 'prefix_number', 'cumulative_time_op', 'avg_time_op', 'hand_input'])

    if cell_name in df['cell_name'].values:
        df.loc[df['cell_name'] == cell_name, [
            'time_extraction',
            'cumulative_time_op',
            'avg_time_op',
            'number_of_zone',
            'number_of_input',
            'suffix_number',
            'prefix_name',
            'prefix_number',
            'hand_input']] = \
            time_extraction, \
                cumulative_time_op, \
                avg_time_op, \
                number_of_zone, \
                number_of_input, \
                suffix_number, \
                prefix_name, \
                prefix_number, \
                hand_input
    else:
        new_row = {
            'cell_name': cell_name,
            'time_extraction': time_extraction,
            'cumulative_time_op': cumulative_time_op,
            'avg_time_op': avg_time_op,
            'number_of_zone': number_of_zone,
            'number_of_input': number_of_input,
            'suffix_number': suffix_number,
            'prefix_name': prefix_name,
            'prefix_number': prefix_number,
            'hand_input': hand_input
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(filename, index=False)

    print(f"Data successfully exported to {filename}.")


def write_output_log(start_time, end_time, state_counter=1, filtered_cells=None, time_counter_ex=None,
                     time_counter_op=None, error_cell_list=None):
    if error_cell_list is None:
        error_cell_list = []

    with open('output.log', 'a') as f:

        execution_time = round(end_time - start_time, 2)

        f.write(time.strftime("%d/%m/%Y %Hh%M") + "\n\n")
        f.write(f"Total Execution time: {execution_time} seconds\n")
        f.write(f"Number of state calculated : {state_counter}\n")

        if len(error_cell_list) > 0:
            f.write("An error occurred for those cells\n")
            f.write(str(error_cell_list) + "\n")

        if time_counter_op is not None:
            execution_time_op = round(time_counter_op, 4)
            time_per_sate = round(execution_time_op / state_counter, 4)
            f.write(f"OP Execution time: {execution_time_op} seconds\n")
            f.write(f"Avg Time per state : {time_per_sate} seconds\n")

        if time_counter_ex is not None:
            execution_time_ex = round(time_counter_ex, 2)
            f.write(f"Gate init Execution time: {execution_time_ex} seconds\n")

        if filtered_cells is not None:
            number_of_gate = len(filtered_cells) - len(error_cell_list)
            f.write(f"Number of cell processed: {number_of_gate} \n")

            if number_of_gate > 0:
                time_per_gate = round(execution_time / number_of_gate, 4)
                f.write(f"Avg Time/Cell : {time_per_gate} seconds\n\n")

        f.write("-----------------------------------------------------------\n\n")
