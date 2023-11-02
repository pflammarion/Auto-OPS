import json

from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.diffusion import Diffusion
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.op import Op
from controllers.GDS_Object.shape import Shape

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

import matplotlib.pyplot as plt

from controllers.GDS_Object.type import ShapeType
from controllers.GDS_Object.zone import Zone


def mergePolygons(polygons) -> list[Polygon]:
    """
    A shape could be created from multiple polygones.
    This function merge them to have only one shape based on coordinates.

    Parameters:
    -----------
    polygons : list[list[x, y]]
        A list of x and y points for each extracted polygones stored in that list.

    Returns:
    --------
    list[Polygon]:
        A list of all polygones created from the initial coordinates extracted.

    Raises:
    -------
    Any relevant exceptions that may occur.
    """

    polygons = [Polygon(p) for p in polygons]

    # Create a list to hold merged polygons
    merged_polygons = []

    while len(polygons) > 0:
        current_polygon = polygons.pop(0)  # Take the first polygon in the list
        connected_polygons = [current_polygon]

        i = 0
        while i < len(connected_polygons):
            for other_polygon in polygons:
                if connected_polygons[i].intersects(other_polygon):
                    connected_polygons.append(other_polygon)
                    polygons.remove(other_polygon)
            i += 1

        # Merge connected polygons using unary_union
        merged_polygon = unary_union(connected_polygons)
        merged_polygons.append(merged_polygon)

    return merged_polygons


def init_diffusion_zones(diffusion) -> None:
    """
    Function to create reflections zones from diffusion shapes and intersection with poly silicons.

    Extracting the left and right poly silicons intersections and create new zones on top of that.

    Parameters:
    -----------
    diffusion : Diffusion
        Objects in the class reflection list instance which hold the reflection zone objects

    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur.
    """

    temp_zone_to_add = []
    diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

    coords = diffusion.get_left_points_coords() + diffusion.get_zone_by_index(0).get_left_points_coords()
    new_zone = Zone(ShapeType.DIFFUSION)
    new_zone.set_coordinates_from_list(coords)
    temp_zone_to_add.append(new_zone)

    for index, zone in enumerate(diffusion.zone_list):
        if index == len(diffusion.zone_list) - 1:
            coords = diffusion.get_right_points_coords() + diffusion.get_zone_by_index(index).get_right_points_coords()

        else:
            coords = diffusion.get_zone_by_index(index).get_right_points_coords() + diffusion.get_zone_by_index(
                index + 1).get_left_points_coords()

        new_zone = Zone(ShapeType.DIFFUSION)
        new_zone.set_coordinates_from_list(coords)
        temp_zone_to_add.append(new_zone)

        # To handle non square polygones shapes
        unique_y_values = set(point[1] for point in coords)

        if len(unique_y_values) > 2:
            min_x = new_zone.get_min_x_coord()
            max_x = new_zone.get_max_x_coord()

            for x, y in zip(*diffusion.polygon.exterior.xy):
                if min_x < x < max_x:
                    coords.append((x, y))

            new_zone.set_coordinates_from_list(coords)

    for zone in temp_zone_to_add:
        diffusion.set_zone(zone)


def element_extractor(gds_cell, layer_list) -> list:
    """
    Function to init the class by extracting every needed polygones for the reflection calculation.
    This is also characterizing the different shapes on a shape type.

    Parameters:
    -----------
    self : object
        The instance of the class.

    layer_list: list(int)
        A list which contains the layer number in the gds file in that order:
        Diffusion layer, N well layer, poly silicon layer, via layer, metal layer.

    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur.
    """

    element_list = []

    for label in gds_cell.labels:
        if label.layer == layer_list[4]:
            founded_label = Label(label.text, label.position.tolist())
            element_list.append(founded_label)

    # extract polygons from GDS
    polygons = gds_cell.get_polygons(by_spec=True)

    for layer in layer_list:
        extracted_polygons = polygons.get((layer, 0), [])
        merged_polygons = mergePolygons(extracted_polygons)
        for polygon in merged_polygons:
            shape = Shape(None, polygon, polygon.exterior.xy, layer)
            shape.set_shape_type(layer_list)
            element_list.append(shape)

    return element_list


def create_op_object(cell_name, gds_cell, layer_list, truthtable, voltage, inputs) -> Op:

    elements_to_keep = []

    op_object = Op(cell_name, inputs, truthtable)

    op_object.element_list = element_extractor(gds_cell, layer_list)

    op_object.reflection_list = element_sorting(op_object.element_list, inputs, truthtable, voltage)

    for element in op_object.element_list:
        if isinstance(element, Shape) and element.shape_type == ShapeType.VIA:
            op_object.via_element_list.append(element)
        else:
            elements_to_keep.append(element)

    op_object.element_list = elements_to_keep

    for diffusion in op_object.reflection_list:
        connect_diffusion_to_polygon(op_object.element_list, diffusion)

    for diffusion in op_object.reflection_list:
        init_diffusion_zones(diffusion)

    for diffusion in op_object.reflection_list:
        connect_diffusion_to_metal(op_object.element_list, diffusion)

    set_zone_states(op_object.reflection_list)

    return op_object


def plot_elements(op_object) -> None:
    """
    Plots elements based on their coordinates and types.

    This function iterates through a list of elements and plots them accordingly.
    If the element is of type 'Label', it is plotted as a point with an annotation
    representing its name. If the element is not of type 'Label', it is plotted as a line.

    Parameters:
    -----------
    self : object
        The instance of the class.

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
    self : object
        The instance of the class.

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
    self : object
        The instance of the class.

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
    self : object
        The instance of the class.

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If a zone state is None, an exception is raised with the gate name.

    Note:
    -----
    Ensure that the 'tmp' directory exists before calling this method,
    as it will attempt to write the PNG file to this location.
    """
    color_list = ['white', 'black']
    fig, ax = plt.subplots()
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
                ax.fill(x, y, facecolor=color_list[state], alpha=1, edgecolor='grey', linewidth=1)

    string_list = [f"{key}_{value}" for key, value in sorted(op_object.inputs.items())]
    result_string = "_".join(string_list)
    file_name = str(op_object.name) + "__" + result_string
    path_name = "tmp/" + file_name
    plt.title(file_name)
    plt.savefig(path_name)
    plt.close()


def export_reflection_to_png_over_gds_cell(op_object) -> None:
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
                         color="black")

    for via in op_object.via_element_list:
        x, y = via.coordinates
        plt.plot(x, y, color='none')
        plt.fill(x, y, color="white", alpha=0.8)

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
    plt.title(file_name)
    plt.savefig(path_name)
    plt.close()


def export_reflection_to_json(op_object) -> None:
    """
    This function retrieves reflection data from the current instance of the class and exports it to a JSON file.
    It constructs a dictionary 'data' containing cell_name, inputs, and reflection information. The 'reflection'
    key in 'data' stores a list of reflections, each having a 'type' and a list of 'zone_list' elements.

    'zone_list' contains dictionaries for each zone, including 'type', 'state', and 'coordinates' for the zone.
    The method constructs a file name using 'gate_name' and 'inputs', then saves the data in JSON format to a file
    in the 'tmp' directory.

    The file name is defined from the gate name, inputs names, and inputs states.

    Parameters:
    -----------
    self : object
       The instance of the class.

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


def element_sorting(element_list, inputs, truthtable, voltage) -> list:
    """
    This function is to categorize the different shapes based on their shape type.
    It is also to append to every shapes the affiliated via to determine the connections.
    The diffusion instances are created and apply to the reflection list in this function too.

    Parameters:
    -----------
    self : object
       The instance of the class.


    Returns:
    --------
    None

    Raises:
    -------
    Any relevant exceptions that may occur

    """

    reflection_list = []

    for element in element_list:
        if isinstance(element, Shape) and element.shape_type != ShapeType.VIA:
            for via in element_list:
                if isinstance(via, Shape) and via.shape_type == ShapeType.VIA \
                        and element.polygon.intersects(via.polygon):
                    element.add_via(via)

    for element in element_list:
        if isinstance(element, Shape):
            is_connected(element_list, inputs, truthtable, voltage, element)

    for element in element_list:
        # To set up diffusion number if connected to at least one metal
        if isinstance(element, Shape) and element.shape_type == ShapeType.DIFFUSION \
                and isinstance(element.attribute, Shape):

            diffusion = Diffusion(element.polygon)

            is_p_mos = False
            for item in element_list:
                if isinstance(element, Shape) \
                        and isinstance(item, Shape) \
                        and item.shape_type == ShapeType.NWELL \
                        and item.polygon.intersects(element.polygon):
                    diffusion.set_type(ShapeType.PMOS)
                    is_p_mos = True
                    break

            if not is_p_mos:
                diffusion.set_type(ShapeType.NMOS)

            reflection_list.append(diffusion)

    return reflection_list


def is_connected(element_list, inputs, truthtable, voltage, element) -> None:
    """
    This function is to link element together.

    If a metal and a poly silicon are linked, the function add the metal as an attribute to the poly silicon.

    If a metal is linked to a label, the function add an instance of Attribute to the metal.


    Parameters:
    -----------
    self : object
       The instance of the class.

    element : Shape | Label
        Objects in the class element list instance

    Returns:
    --------
    None

    Raises:
    -------
    Exception
        Any relevant exceptions that may occur.
        Label missing but found in the GDS file.
        Input missing but found in the GDS file.

    """
    ground_pin_name = power_pin_name = ""
    for volt in voltage:
        if "ground" in volt["type"]:
            ground_pin_name = volt["name"]
        elif "power" in volt["type"]:
            power_pin_name = volt["name"]

    if element.shape_type == ShapeType.POLYSILICON or element.shape_type == ShapeType.DIFFUSION:
        for item in element_list:
            if isinstance(item, Shape) and item.shape_type == ShapeType.METAL:
                for element_connection in element.connection_list:
                    if element_connection in item.connection_list:
                        element.set_attribute(item)

    elif element.shape_type == ShapeType.METAL:
        for label in element_list:
            if isinstance(label, Label):
                if element.polygon.contains(Point(label.coordinates)):
                    if label.name in inputs.keys():
                        element.set_attribute(Attribute(ShapeType.INPUT, label.name, inputs[label.name]))
                        break

                    elif label.name in truthtable.keys():
                        for outputs in truthtable:
                            for truthtable_inputs, output in truthtable[outputs]:
                                if label.name in output:
                                    if truthtable_inputs == inputs:
                                        element.set_attribute(
                                            Attribute(ShapeType.OUTPUT, label.name, output[label.name])
                                        )
                                else:
                                    # Find why FA do not have used output
                                    raise Exception("Missing inputs: " + str(truthtable_inputs))

                        break
                    else:
                        raise Exception("Missing label: " + str(label.name))
                else:
                    _, point_y = label.coordinates
                    _, metal_y = element.coordinates
                    set_metal_y = set(metal_y)
                    is_label_found = False
                    for y in set_metal_y:
                        if y == point_y:
                            is_label_found = True
                            break

                    if label.name.lower() == ground_pin_name.lower() and is_label_found:
                        element.set_attribute(Attribute(ShapeType.VSS))
                        break

                    elif label.name.lower() == power_pin_name.lower() and is_label_found:
                        element.set_attribute(Attribute(ShapeType.VDD))
                        break


def connect_diffusion_to_polygon(element_list, diffusion) -> None:
    """
    To set up zones where the poly silicon overlap to the diffusion parts.
    Creating a zone from the overlaps coordinates.

    Parameters:
    -----------
    self : object
       The instance of the class.

    diffusion : Diffusion
        Objects in the class reflection list instance which hold the reflection zone objects

    Returns:
    --------
    None

    Raises:
    -------
    Exception
        Any relevant exceptions that may occur.
    """

    for element in element_list:
        if isinstance(element, Shape) and element.shape_type == ShapeType.POLYSILICON and \
                element.polygon.intersects(diffusion.polygon):

            intersections = diffusion.polygon.intersection(element.polygon)
            if hasattr(intersections, "geoms"):
                for index, inter in enumerate(intersections.geoms):
                    diffusion.set_zone(Zone(ShapeType.POLYSILICON, inter.exterior.xy, element))
            else:
                diffusion.set_zone(Zone(ShapeType.POLYSILICON, intersections.exterior.xy, element))


def connect_diffusion_to_metal(element_list, diffusion) -> None:
    """
    Identify each zones where a metal layer is connected through a via connection.

    Parameters:
    -----------
    self : object
       The instance of the class.

    diffusion : Diffusion
        Objects in the class reflection list instance which hold the reflection zone objects


    Returns:
    --------
    None

    Raises:
    -------
    Exception
        Any relevant exceptions that may occur.
    """

    for zone in diffusion.zone_list:
        if zone.shape_type == ShapeType.DIFFUSION:
            for element in element_list:
                if isinstance(element, Shape) and element.shape_type == ShapeType.METAL:
                    zone_polygon = Polygon(Polygon(list(zip(zone.coordinates[0], zone.coordinates[1]))))
                    for connection_polygons in element.connection_list:
                        if zone_polygon.intersects(connection_polygons):
                            zone.set_connected_to(element)

                            break


def set_zone_states(reflection_list) -> None:
    """
    This function is to determine a state for all the diffusion zones.

    First loop to set the known states to the zones (inputs, outputs, VDD, VSS)
    Second loop to set a state to poly silicons and metals which are connected together.
    Third loop to give a state to each zone which is not connected to either a metal or a poly silicon.


    Parameters:
    -----------
    self : object
       The instance of the class.

    Returns:
    --------
    None

    Raises:
    -------
    Exception
        Any relevant exceptions that may occur.
        None type for diffusion shape type during the previous steps.
        GCK input or output which are not covered.
        Wrong or unknown attribut applied to metal.

    """

    for diffusion in reflection_list:

        if diffusion.shape_type is None:
            Exception("Error diffusion shape type none")

        diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

        # known state loop
        for zone in diffusion.zone_list:
            if zone.connected_to is not None:
                if isinstance(zone.connected_to.attribute, Attribute):
                    if zone.connected_to.attribute.shape_type == ShapeType.VDD:
                        zone.set_state(1)
                    elif zone.connected_to.attribute.shape_type == ShapeType.VSS:
                        zone.set_state(0)

                    elif zone.connected_to.attribute.shape_type == ShapeType.OUTPUT:
                        zone.set_state(zone.connected_to.attribute.state)

                    elif zone.connected_to.attribute.shape_type == ShapeType.INPUT \
                            and zone.connected_to.attribute.label == "GCK":

                        raise AttributeError("Clock gates not working " + str(zone.connected_to.attribute.label))

                    else:
                        raise AttributeError("Wrong attribut in " + str(zone.connected_to.shape_type))

                elif isinstance(zone.connected_to.attribute, Shape) and isinstance(
                        zone.connected_to.attribute.attribute,
                        Attribute) and zone.connected_to.attribute.attribute.shape_type == ShapeType.INPUT:
                    zone.set_state(zone.connected_to.attribute.attribute.state)

        # Wire unknown loop
        for zone in diffusion.zone_list:
            if isinstance(zone.connected_to, Shape) and zone.connected_to.shape_type == ShapeType.METAL \
                    and not zone.wire and zone.connected_to.attribute is None:

                found_state = None
                for index, zone_to_find in enumerate(diffusion.zone_list):
                    if zone_to_find.connected_to == zone.connected_to:
                        if zone_to_find.state is not None:
                            found_state = zone_to_find.state
                        elif zone_to_find.connected_to.shape_type is not ShapeType.POLYSILICON:
                            found_state = find_neighbor_state(diffusion, index)
                        if found_state is not None:
                            break

                if found_state is not None:
                    for diffusion_loop in reflection_list:
                        # Find other zone connected to this wire branch
                        for index, zone_to_apply in enumerate(diffusion_loop.zone_list):
                            if zone_to_apply.connected_to == zone.connected_to or (
                                    isinstance(zone_to_apply.connected_to, Shape) and
                                    zone_to_apply.connected_to.attribute == zone.connected_to):
                                if zone_to_apply.state is None:
                                    zone_to_apply.set_state(found_state)
                                    zone_to_apply.wire = True

        # Unknown loop
        for index, zone in enumerate(diffusion.zone_list):
            if zone.connected_to is None:
                found_state = find_neighbor_state(diffusion, index)
                if found_state is not None:

                    zone.set_state(found_state)
                else:
                    if diffusion.shape_type == ShapeType.PMOS:
                        zone.set_state(1)

                    else:
                        zone.set_state(0)


def find_neighbor_state(diffusion, zone_index) -> bool:
    """
    This function is to find the state applicable to a zone based on physics electronic properties.

    P_MOS diffusion layer: power is passing through poly silicon's zone with a _0_ input

    N_MOS diffusion layer: power is passing through poly silicon's zone with a _1_ input

    This function tries to find the closed known state by going left and right from the initial index position.

    If the zone is between two poly silicons with an "un passing" state, not reflecting state is applied to the zone

    Parameters:
    -----------
    self : object
       The instance of the class.

    diffusion : Diffusion
        The diffusion part where the searching algorithm is going to be performed.

    zone_index: int
        The initial start index of the zone the algorthm wants to apply a state

    Returns:
    --------
    bool:
        The found state to be applied to the selected zone.

    Raises:
    -------
    Exception
        Any relevant exceptions that may occur.
    """

    diffusion_type = diffusion.shape_type
    zone_list = diffusion.zone_list
    neighbor_index = [zone_index - 1, zone_index + 1]
    stop_loop = False
    found_state = None

    while not stop_loop:
        for index in range(len(neighbor_index)):
            if neighbor_index[index] is not None and 0 <= neighbor_index[index] < len(zone_list):

                if index == 0:
                    next_index = neighbor_index[index] - 1
                else:
                    next_index = neighbor_index[index] + 1

                zone = zone_list[neighbor_index[index]]

                if zone.shape_type == ShapeType.POLYSILICON:
                    if diffusion_type == ShapeType.PMOS and zone.state == 0:
                        neighbor_index[index] = next_index
                        continue

                    elif diffusion_type == ShapeType.NMOS and zone.state == 1:
                        neighbor_index[index] = next_index
                        continue
                    else:
                        neighbor_index[index] = None
                        continue

                elif (
                        zone.connected_to is not None
                        and zone.connected_to.shape_type == ShapeType.METAL
                        and zone.state is not None
                ) \
                        or zone.state is not None:

                    found_state = zone.state
                    stop_loop = True
                    break

                else:
                    neighbor_index[index] = next_index
                    continue
            else:
                neighbor_index[index] = None
                continue

        # If the zone is between two un passing zones, not reflecting state applied
        if all(x is None for x in neighbor_index):

            if diffusion_type == ShapeType.PMOS:
                found_state = 1

            else:
                found_state = 0

            break

    return found_state
