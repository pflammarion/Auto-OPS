from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.diffusion import Diffusion
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.shape import Shape

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from controllers.GDS_Object.type import ShapeType
from controllers.GDS_Object.zone import Zone


class AutoOPSPropagation:
    """
    Represents an object usable to perform body voltage propagation simulation from a GDS-II (Graphics Data System) layout.

    Args:
        cell_name (str): The name of the gate in the gds file in the Cells' list.
        gds_cell (GdsLibrary): Dictionary of cells in the library's object, indexed by name.
        layer_list (list[list[int]): Diffusion layer, N well layer, poly silicon layer, via layers, metal layers and label layers.
        truthtable (dict{list[set(dict)]})): A list containing the information the output based on the input for a gate.
        voltage(list[dict]): Contains the voltage names and types.
        inputs_list(list(str)): contains the inputs names.
    Attributes:
        name (str): The name of the gate in the gds file in the Cells' list.
        inputs(dict): Contains the inputs names and values.
        truthtable (dict): The truthtable is a list containing the information the output based on the input for a gate.
        via_element_list(list) Contains all the extracted via elements converted to objects.
        element_list(list): Contains all the extracted elements converted to objects.
        reflection_list(list): Contains all reflecting elements as diffusion's zones and poly-silicon's overlapping.

    Example:
        To create a GdsDrawing instance:
        >>> import gdspy
        >>> lib = gdspy.GdsLibrary()
        >>> gds_cell = lib.read_gds("Platforms/PDK45nm/stdcells.gds").cells["INV_X1"]
        >>> drawing = AutoOPSPropagation(
        >>>         "INV_X1",
        >>>         gds_cell,
        >>>         [[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]],
        >>>         {'ZN': [({'A': True}, {'ZN': False}), ({'A': False}, {'ZN': True})]},
        >>>         [{'name': 'VDD', 'type': 'primary_power'}, {'name': 'VSS', 'type': 'primary_ground'}],
        >>>         ['A']
        >>>     )

    This class create an object from a GDS input and store information as the optical state of each gate,
     depending on the position and gates states.
    """

    def __init__(self, cell_name, gds_cell, layer_list, truthtable, voltage, inputs_list):
        self.name = cell_name
        self.truthtable = truthtable
        self.inputs_list = inputs_list
        self.via_element_list = []
        self.orientation_list = {}

        self.inputs = {}

        self.element_list = element_extractor(gds_cell, layer_list)
        self.reflection_list = []

        # list without the filtering of unused diffusion zones
        temp_reflection_list = element_sorting(self.element_list, inputs_list, truthtable, voltage)

        elements_to_keep = []

        for element in self.element_list:
            if isinstance(element, Shape) and element.shape_type == ShapeType.VIA:
                self.via_element_list.append(element)
            else:
                elements_to_keep.append(element)

        self.element_list = elements_to_keep

        for diffusion in temp_reflection_list:
            is_intersecting = connect_diffusion_to_polygon(self.element_list, diffusion)
            if is_intersecting:
                self.reflection_list.append(diffusion)

        for diffusion in self.reflection_list:
            connect_diffusion_to_metal(self.element_list, diffusion)

    def get_height(self):
        min_y = float("inf")
        max_y = 0
        for diff in self.reflection_list:
            y_coords = [point[1] for point in diff.polygon.exterior.coords]
            if max(y_coords) > max_y:
                max_y = max(y_coords)
            if min(y_coords) < min_y:
                min_y = min(y_coords)

        return min_y + max_y

    def get_width(self):
        min_x = float("inf")
        max_x = 0
        for diff in self.reflection_list:
            x_coords = [point[0] for point in diff.polygon.exterior.coords]
            if max(x_coords) > max_x:
                max_x = max(x_coords)
            if min(x_coords) < min_x:
                min_x = min(x_coords)

        return min_x + max_x

    def calculate_orientations(self):
        orientation_side = ["N", "FN", "E", "FE", "S", "FS", "W", "FW"]

        cell_height = self.get_height()

        for orientation in orientation_side:
            self.orientation_list[orientation] = []
            for reflection in self.reflection_list:
                for zone in reflection.zone_list:
                    x, y = apply_transformation(zone.coordinates, orientation, reflection.get_diff_width(), cell_height)
                    self.orientation_list[orientation].append(
                        {'coords': [x, y], 'state': zone.state, "diff_type": reflection.shape_type}
                    )

    def apply_state(self, inputs, flip_flop=0):

        self.inputs = inputs

        if flip_flop is None:
            flip_flop = 0

        for element in self.element_list:
            if isinstance(element, Shape) and element.attribute is not None and isinstance(element.attribute, Attribute):
                if element.attribute.shape_type == ShapeType.INPUT:
                    if element.attribute.label in inputs.keys():
                        element.attribute.set_state(inputs[element.attribute.label])

                elif element.attribute.shape_type == ShapeType.OUTPUT:
                    for outputs in self.truthtable:
                        for truthtable_inputs, output in self.truthtable[outputs]:
                            if element.attribute.label in outputs and element.attribute.label in output.keys():
                                is_equal = False
                                for truthtable_inputs_value, truthtable_inputs_key in enumerate(truthtable_inputs):
                                    if truthtable_inputs_key not in inputs or inputs[truthtable_inputs_key] != truthtable_inputs[truthtable_inputs_key]:
                                        is_equal = False
                                        break
                                    else:
                                        is_equal = True

                                if is_equal:
                                    if any("CK" in name or "RESET" in name or "GATE" in name or "CLK" in name for name in list(inputs.keys())) or "Q" in outputs:
                                        if "N" in list(output.keys())[0]:
                                            value = bool(not flip_flop)
                                        else:
                                            value = bool(flip_flop)
                                        element.attribute.set_state(value)
                                    else:
                                        element.attribute.set_state(output[element.attribute.label])

        none_counter = 0
        none_loop_counter = 0
        while True:
            new_none_counter = set_zone_states(self.reflection_list)

            if none_counter == new_none_counter:
                break
            else:
                none_counter = new_none_counter

            none_loop_counter += 1


def apply_transformation(coordinates, transformation, width, height):

    x, y = coordinates

    if transformation == 'N':
        # No transformation for North
        x = x
        y = y
    elif transformation == 'FN':
        # Flip the coordinates along the x-axis
        x = tuple((xi * - 1) + width for xi in reversed(x))
        y = tuple(yi for yi in reversed(y))

    elif transformation == 'E':
        # Rotate 90 degrees clockwise: swap x and y coordinates, and negate the new x coordinate
        x, y = tuple(yi for yi in y), tuple((xi * -1) + width for xi in x)
    elif transformation == 'FE':
        # Flip the coordinates along the y-axis and rotate 90 degrees clockwise (same as MY90)
        x, y = tuple(yi for yi in reversed(y)), tuple(xi for xi in reversed(x))

    elif transformation == 'S':
        # Rotate 180 degrees: reverse both x and y coordinates
        x = tuple((xi * -1) + width for xi in reversed(x))
        y = tuple((yi * -1) + height for yi in reversed(y))
    elif transformation == 'FS':
        # Flip the coordinates along the x-axis
        x = tuple(xi for xi in x)
        y = tuple((yi * -1) + height for yi in y)

    elif transformation == 'W':
        # Rotate 270 degrees clockwise: swap x and y coordinates, and negate the new y coordinate
        x, y = tuple((yi * -1) + height for yi in reversed(y)), tuple(xi for xi in reversed(x))
    elif transformation == 'FW':
        # Flip the coordinates along the y-axis and rotate 270 degrees clockwise (same as MY270)
        x, y = tuple((yi * -1) + height for yi in y), tuple((xi * -1) + width for xi in x)

    else:
        raise ValueError("Invalid transformation provided.")

    return x, y


def element_sorting(element_list, inputs_list, truthtable, voltage) -> list:
    """
    This function is to categorize the different shapes based on their shape type.
    It is also to append to every shapes the affiliated via to determine the connections.
    The diffusion instances are created and apply to the reflection list in this function too.

    Parameters:
    -----------
     element_list: list
        Contains all the extracted elements converted to objects.

     inputs: dict
        Contains the inputs names and values.

     truthtable: dict
        The truthtable is a list containing the information the output based on the input for a gate.

     voltage: list[dict]
        Contains all the extracted via elements converted to objects.

    Returns:
    --------
    reflection_list: list
        Contains all reflecting elements as diffusion's zones and poly-silicon's overlapping.

    Raises:
    -------
    Any relevant exceptions that may occur

    """

    reflection_list = []

    for element in element_list:
        if isinstance(element, Shape) and (
                element.shape_type == ShapeType.METAL or element.shape_type == ShapeType.DIFFUSION or element.shape_type == ShapeType.POLYSILICON):
            for via in element_list:
                if isinstance(via, Shape) and via.shape_type == ShapeType.VIA \
                        and element.polygon.intersects(via.polygon) and \
                        (via.layer_level == element.layer_level or via.layer_level == element.layer_level + 1):
                    element.add_via(via)

    for element in element_list:
        if isinstance(element, Shape) and element.attribute is None:
            # TODO check why this loop is entering already defined attribut
            is_connected(element_list, inputs_list, truthtable, voltage, element)

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


def merge_polygons(polygons) -> list[Polygon]:
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
    WARNING old function useless

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
    gds_cell: GdsLibrary
        Dictionary of cells in the library's object, indexed by name.

    layer_list: list(int)
        A list which contains the layer number in the gds file in that order:
        Diffusion layer, N well layer, poly silicon layer, via layer, metal layer.

    Returns:
    --------
    element_list: list
        Contains all the extracted elements converted to objects.

    Raises:
    -------
    Any relevant exceptions that may occur.
    """

    element_list = []
    label_index = 5

    for label in gds_cell.labels:
        for i in range(len(layer_list[label_index])):
            if label.layer == layer_list[label_index][i][0]:
                founded_label = Label(label.text, label.position.tolist())
                element_list.append(founded_label)

    # extract polygons from GDS
    polygons = gds_cell.get_polygons(by_spec=True)

    for layer_index, layer in enumerate(layer_list):
        if layer_index == 3 or layer_index == 4:
            for sublayer_index, sublayer in enumerate(layer):
                layer_level = sublayer_index + 1
                extract_and_merge_polygons(polygons, element_list, layer_index, sublayer, layer_level)
        elif layer_index != label_index:
            extract_and_merge_polygons(polygons, element_list, layer_index, layer)

    return element_list


def extract_and_merge_polygons(polygons, element_list, layer_index, layer, layer_level=0) -> None:
    extracted_polygons = polygons.get((layer[0], layer[1]), [])
    merged_polygons = merge_polygons(extracted_polygons)
    for polygon in merged_polygons:
        shape = Shape(None, polygon, polygon.exterior.xy, layer)
        shape.set_shape_type(layer_index)
        shape.set_layer_level(layer_level)
        element_list.append(shape)


def is_connected(element_list, inputs_list, truthtable, voltage, element) -> None:
    """
    This function is to link element together.

    If a metal and a poly silicon are linked, the function add the metal as an attribute to the poly silicon.

    If a metal is linked to a label, the function add an instance of Attribute to the metal.


    Parameters:
    -----------
    element_list: list
        Contains all the extracted elements converted to objects.

    inputs: dict
        Contains the inputs names and values.

    truthtable: dict
        The truthtable is a list containing the information the output based on the input for a gate.

    voltage: list[dict]
        Contains all the extracted via elements converted to objects.

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
            if isinstance(item,
                          Shape) and item.shape_type == ShapeType.METAL and item.layer_level != element.layer_level:
                for element_connection in element.connection_list:
                    if element_connection in item.connection_list:
                        element.set_attribute(item)
                        break

    elif element.shape_type == ShapeType.METAL and element.attribute is None:
        for label in element_list:
            if isinstance(label, Label):
                if element.polygon.contains(Point(label.coordinates)):
                    if label.name in inputs_list:
                        element.set_attribute(Attribute(ShapeType.INPUT, label.name))
                        break

                    elif label.name in truthtable.keys():
                        element.set_attribute(Attribute(ShapeType.OUTPUT, label.name))
                        break

                    elif label.name.lower() == "vss":
                        element.set_attribute(Attribute(ShapeType.VSS))
                        break
                    elif label.name.lower() == "vdd":
                        element.set_attribute(Attribute(ShapeType.VDD))
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


def connect_diffusion_to_polygon(element_list, diffusion) -> bool:
    """
    To set up zones where the poly silicon overlap to the diffusion parts.
    Creating a zone from the overlaps coordinates.

    Parameters:
    -----------
    element_list: list
        Contains all the extracted elements converted to objects.

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
    # If a diffusion zone does not intersect any poly the
    poly_element_list = []
    for element in element_list:
        if isinstance(element, Shape) and element.shape_type == ShapeType.POLYSILICON:
            if element.polygon.intersects(diffusion.polygon):
                intersections = diffusion.polygon.intersection(element.polygon)
                if hasattr(intersections, "geoms"):
                    for index, inter in enumerate(intersections.geoms):
                        diffusion.set_zone(Zone(ShapeType.POLYSILICON, inter.exterior.xy, [element]))
                else:
                    diffusion.set_zone(Zone(ShapeType.POLYSILICON, intersections.exterior.xy, [element]))

                poly_element_list.append(element.polygon)

    diffusion_zones = diffusion.polygon.difference(unary_union(poly_element_list))
    if hasattr(diffusion_zones, "geoms"):
        for index, inter in enumerate(diffusion_zones.geoms):
            diffusion.set_zone(Zone(ShapeType.DIFFUSION, inter.exterior.xy))

    return len(poly_element_list) > 0


def connect_diffusion_to_metal(element_list, diffusion) -> None:
    """
    Identify each zones where a metal layer is connected through a via connection.

    Parameters:
    -----------
    element_list: list
        Contains all the extracted elements converted to objects.

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
            zone_polygon = Polygon(zip(zone.coordinates[0], zone.coordinates[1]))
            for element in element_list:
                if (
                        isinstance(element, Shape)
                        and element.shape_type == ShapeType.METAL
                        and element.layer_level == 1
                ):
                    for connection_polygons in element.connection_list:
                        if (
                                connection_polygons.layer_level == 1
                                and zone_polygon.intersects(connection_polygons.polygon)
                        ):
                            zone.set_connected_to(element)
                            add_connection_zone(element_list, element, zone)
                            break

        elif zone.shape_type == ShapeType.POLYSILICON:
            add_connection_zone(element_list, zone.connected_to[0], zone)


def add_connection_zone(element_list, element, zone):
    for next_element in element_list:
        if (
                isinstance(next_element, Shape)
                and next_element.shape_type == ShapeType.METAL
                and next_element not in zone.connected_to
                and any(connection in next_element.connection_list for connection in element.connection_list)
        ):
            zone.set_connected_to(next_element)
            add_connection_zone(element_list, next_element, zone)
            return


def set_zone_states(reflection_list) -> int:
    """
    This function is to determine a state for all the diffusion zones.

    First loop to set the known states to the zones (inputs, outputs, VDD, VSS)
    Second loop to set a state to poly silicons and metals which are connected together.
    Third loop to give a state to each zone which is not connected to either a metal or a poly silicon.


    Parameters:
    -----------
    reflection_list: list
        Contains all reflecting elements as diffusion's zones and poly-silicon's overlapping.

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
    state_counter = 0

    for diffusion in reflection_list:

        if diffusion.shape_type is None:
            Exception("Error diffusion shape type none")

        diffusion.zone_list = sorted(diffusion.zone_list, key=lambda selected_zone: selected_zone.get_min_x_coord())

        # known state loop
        for zone_index, zone in enumerate(diffusion.zone_list):
            if zone.state is not None:
                for connected_path in zone.connected_to:
                    connected_path.set_state(zone.state)
                continue

            if len(zone.connected_to) > 0:
                for connection in zone.connected_to:

                    # to apply the state in the all path for opti
                    if connection.state is not None:
                        zone.set_state(connection.state)

                        for connected_path in zone.connected_to:
                            connected_path.set_state(connection.state)

                        break

                    if isinstance(connection.attribute, Attribute):
                        if connection.attribute.shape_type == ShapeType.VDD:
                            zone.set_state(1)
                            break
                        elif connection.attribute.shape_type == ShapeType.VSS:
                            zone.set_state(0)
                            break

                        elif connection.attribute.shape_type == ShapeType.OUTPUT or \
                                connection.attribute.shape_type == ShapeType.INPUT:
                            zone.set_state(connection.attribute.state)

                            break

                    elif isinstance(connection.attribute, Shape) and isinstance(
                            connection.attribute.attribute,
                            Attribute) and connection.attribute.attribute.shape_type == ShapeType.INPUT:
                        zone.set_state(connection.attribute.attribute.state)
                        break

        # Unknown loop
        for index, zone in enumerate(diffusion.zone_list):
            if zone.shape_type == ShapeType.POLYSILICON:
                find_incoherent_states(diffusion, index, zone)
                continue

            elif zone.state is not None:
                continue

            found_state = find_neighbor_state(diffusion, index)
            if found_state is not None:
                zone.set_state(found_state)

        for zone in diffusion.zone_list:
            if zone.state is None:
                state_counter += 1
            else:
                for connected_path in zone.connected_to:
                    connected_path.set_state(zone.state)

    return state_counter


def find_incoherent_states(diffusion, zone_index, zone) -> None:
    if 1 <= zone_index < len(diffusion.zone_list) - 1:
        left_neighbor_state = diffusion.zone_list[zone_index - 1].state
        right_neighbor_state = diffusion.zone_list[zone_index + 1].state
        if left_neighbor_state is not None and right_neighbor_state is not None:
            if left_neighbor_state != right_neighbor_state:
                if diffusion.shape_type == ShapeType.NMOS:
                    state = 0
                else:
                    state = 1

                if zone.state is not None and zone.state != state:
                    Exception("State missmatch")

                else:
                    zone.set_state(state)
                    for connected_path in zone.connected_to:
                        connected_path.set_state(state)


def find_neighbor_state(diffusion, zone_index) -> bool:
    """
    This function is to find the state applicable to a zone based on physics electronic properties.

    P_MOS diffusion layer: power is passing through poly silicon's zone with a _0_ input

    N_MOS diffusion layer: power is passing through poly silicon's zone with a _1_ input

    This function tries to find the closed known state by going left and right from the initial index position.

    If the zone is between two poly silicons with an "un passing" state, not reflecting state is applied to the zone

    Parameters:
    -----------
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

                elif zone.state is not None:
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
            break

    return found_state
