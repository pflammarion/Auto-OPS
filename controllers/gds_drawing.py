import json

from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.shape import Shape

import matplotlib.pyplot as plt

from controllers.GDS_Object.type import ShapeType


def plot_elements(op_object) -> None:
    """
    Plots elements based on their coordinates and types.

    This function iterates through a list of elements and plots them accordingly.
    If the element is of type 'Label', it is plotted as a point with an annotation
    representing its name. If the element is not of type 'Label', it is plotted as a line.

    Parameters:
    -----------
    op_object: Op
        Op object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur.
    """
    for element in op_object.element_list:
        x, y = element.coordinates
        if isinstance(element, Label):
            plt.scatter(x, y)
            plt.annotate(element.name, (x, y))
        else:
            plt.plot(x, y)

    plt.title(op_object.name)
    plt.show()


def plot_reflection(op_object) -> None:
    """
    Plots reflection zones based on their coordinates and state.

    This function iterates through a list of diffusion shapes and reflection zones and plots them accordingly.
    If a diffusion part in P_MOS, the states reflection are unversed because of reflection physical behaviour.

    Parameters:
    -----------
    op_object: Op
        Op object which contains the information to be extracted

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
    for reflection in op_object.reflection_list:
        x, y = reflection.polygon.exterior.xy
        plt.plot(x, y)

        for zone in reflection.zone_list:
            x, y = zone.coordinates
            ax.scatter(x, y, marker='o')
            state = zone.state
            if reflection.shape_type == ShapeType.PMOS:
                if bool(state):
                    state = 0
                else:
                    state = 1

            if state is None:
                raise Exception("The RCV calculation cannot be performed on this shape " + str(
                    op_object.name) + ". Please try again")
            else:
                ax.fill(x, y, facecolor=color_list[state], alpha=0.2, edgecolor='black', linewidth=1)

    plt.title(op_object.name)
    plt.show()


def plot_show_case(op_object) -> None:
    """
    Plots elements based on their coordinates and types.

    This function iterates through a list of elements and plots them accordingly.
    If the element is of type 'Label', it is plotted as a point with an annotation
    representing its name. If the element is not of type 'Label', it is plotted as a line.

    Parameters:
    -----------
    op_object: Op
        Op object which contains the information to be extracted

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If a zone state is None, an exception is raised with the gate name.
    """
    for element in op_object.element_list:
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

    plt.title(op_object.name)
    path_name = "tmp/" + op_object.name
    plt.savefig(path_name)
    plt.close()


def export_reflection_to_png(op_object) -> None:
    """
    Export as a PNG the reflection zones based on their coordinates and state.
    The title of the figure is defined from the gate name, inputs names, and inputs states.
    The file name is the same as the figure name. The output folder is ./tmp by default.

    This function iterates through a list of diffusion shapes and reflection zones and plots them accordingly.
    If a diffusion part in P_MOS, the states reflection are unversed because of reflection physical behaviour.
    Waring, compared to plot_reflection() the reflection is in black else is white for a better readable output.

    Parameters:
    -----------
    op_object: Op
        Op object which contains the information to be extracted

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
    for reflection in op_object.reflection_list:
        for zone in reflection.zone_list:
            x, y = zone.coordinates
            state = zone.state
            if reflection.shape_type == ShapeType.PMOS:
                if bool(state):
                    state = 0
                else:
                    state = 1

            if state is None:
                raise Exception("The RCV calculation cannot be performed on this shape " + str(
                    op_object.name) + ". Please try again")
            else:
                plt.fill(x, y, facecolor=color_list[state], alpha=1, edgecolor='grey', linewidth=1)

    string_list = [f"{key}_{value}" for key, value in sorted(op_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(op_object.name) + "__" + result_string
    path_name = "tmp/" + file_name
    plt.title(file_name)
    plt.savefig(path_name)
    plt.close()


def export_reflection_to_png_over_gds_cell(op_object, reflection_draw=False, with_axes=True) -> None:

    # plt.figure(figsize=(6, 8))

    for element in op_object.element_list:
        x, y = element.coordinates

        color = "grey"
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
            if element.name in op_object.truthtable.keys():
                for outputs in op_object.truthtable:
                    for truthtable_inputs, output in op_object.truthtable[outputs]:
                        if element.name in output and truthtable_inputs == op_object.inputs:
                            text = str(element.name) + " = " + str(int(output[element.name]))

            elif element.name in op_object.inputs.keys():
                text = str(element.name) + " = " + str(int(op_object.inputs[element.name]))
            else:
                text = element.name

            plt.annotate(text, (x, y), bbox=dict(facecolor='grey', edgecolor='none', boxstyle='round,pad=0.2'),
                         color=(0.95, 0.90, 0.67))

    for via in op_object.via_element_list:
        x, y = via.coordinates
        plt.plot(x, y, color='none')
        plt.fill(x, y, color="white", alpha=0.8)

    if reflection_draw:
        for reflection in op_object.reflection_list:
            for zone in reflection.zone_list:
                x, y = zone.coordinates
                state = zone.state
                if reflection.shape_type == ShapeType.PMOS:
                    if bool(state):
                        state = 0
                    else:
                        state = 1

                if state is None:
                    raise Exception("The RCV calculation cannot be performed on this shape " + str(
                        op_object.name) + ". Please try again")
                elif bool(state):
                    plt.fill(x, y, facecolor="black", alpha=1)

    string_list = [f"{key}_{value}" for key, value in sorted(op_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(op_object.name) + "_overlay__" + result_string
    path_name = "tmp/" + file_name

    if with_axes:
        plt.title(file_name)
        plt.savefig(path_name)
    else:
        plt.axis('off')
        plt.savefig(path_name, bbox_inches='tight', pad_inches=0, format='png')
    plt.close()


def export_reflection_to_json(op_object) -> None:
    """
    This function retrieves reflection data from the op_object and exports it to a JSON file.
    It constructs a dictionary 'data' containing cell_name, inputs, and reflection information. The 'reflection'
    key in 'data' stores a list of reflections, each having a 'type' and a list of 'zone_list' elements.

    'zone_list' contains dictionaries for each zone, including 'type', 'state', and 'coordinates' for the zone.
    The method constructs a file name using 'gate_name' and 'inputs', then saves the data in JSON format to a file
    in the 'tmp' directory.

    The file name is defined from the gate name, inputs names, and inputs states.

    Parameters:
    -----------
    op_object: Op
        Op object which contains the information to be extracted

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

    data = {'cell_name': op_object.name, 'inputs': op_object.inputs, 'reflection': []}
    for diffusion in op_object.reflection_list:

        ref_type = str(diffusion.shape_type)
        zone_list = []

        for zone in diffusion.zone_list:
            coordinates = [(x, y) for x, y in zip(*zone.coordinates)]
            state = zone.state
            zone_type = str(zone.shape_type)
            zone_list.append({'type': zone_type, 'state': state, 'coordinates': coordinates})

        data['reflection'].append({'type': ref_type, 'zone_list': zone_list})

    string_list = [f"{key}_{value}" for key, value in sorted(op_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(op_object.name) + "__" + result_string + ".json"
    path_name = "tmp/" + file_name

    with open(path_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)
