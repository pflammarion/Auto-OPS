from controllers.GDS_Object.attribute import Attribute
from controllers.GDS_Object.diffusion import Diffusion
from controllers.GDS_Object.label import Label
from controllers.GDS_Object.shape import Shape

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from controllers.GDS_Object.type import ShapeType
from controllers.GDS_Object.zone import Zone


class Op:
    """
    Represents an object usable to perform Optical probing simulation from a GDS (Graphics Data System) layout.

    Args:
        cell_name (str): The name of the gate in the gds file in the Cells' list.
        gds_cell (GdsLibrary): Dictionary of cells in the library's object, indexed by name.
        layer_list (list[int]): Diffusion layer, N well layer, poly silicon layer, via layer, metal layer.
        truthtable (dict{list[set(dict)]})): A list containing the information the output based on the input for a gate.
        voltage(list[dict]): Contains the voltage names and types.
        inputs(dict): contains the inputs values.
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
        >>> drawing = Op(
        >>>         "INV_X1",
        >>>         gds_cell,
        >>>         [1, 5, 9, 10, 11],
        >>>         {'ZN': [({'A': True}, {'ZN': False}), ({'A': False}, {'ZN': True})]},
        >>>         [{'name': 'VDD', 'type': 'primary_power'}, {'name': 'VSS', 'type': 'primary_ground'}],
        >>>         {'A1': 1, 'A2': 1}
        >>>     )

    This class create an object from a GDS input and store information as the optical state of each gate,
     depending on the position and gates states.
    """

    def __init__(self, cell_name, gds_cell, layer_list, truthtable, voltage, inputs):
        self.name = cell_name
        self.inputs = inputs
        self.truthtable = truthtable
        self.via_element_list = []

        self.element_list = element_extractor(gds_cell, layer_list)
        self.reflection_list = element_sorting(self.element_list, inputs, truthtable, voltage)

        elements_to_keep = []

        for element in self.element_list:
            if isinstance(element, Shape) and element.shape_type == ShapeType.VIA:
                self.via_element_list.append(element)
            else:
                elements_to_keep.append(element)

        self.element_list = elements_to_keep

        for diffusion in self.reflection_list:
            connect_diffusion_to_polygon(self.element_list, diffusion)

        for diffusion in self.reflection_list:
            init_diffusion_zones(diffusion)

        for diffusion in self.reflection_list:
            connect_diffusion_to_metal(self.element_list, diffusion)

        set_zone_states(self.reflection_list)


def element_sorting(element_list, inputs, truthtable, voltage) -> list:
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

    for label in gds_cell.labels:
        if label.layer == layer_list[4]:
            founded_label = Label(label.text, label.position.tolist())
            element_list.append(founded_label)

    # extract polygons from GDS
    polygons = gds_cell.get_polygons(by_spec=True)

    for layer in layer_list:
        extracted_polygons = polygons.get((layer, 0), [])
        merged_polygons = merge_polygons(extracted_polygons)
        for polygon in merged_polygons:
            shape = Shape(None, polygon, polygon.exterior.xy, layer)
            shape.set_shape_type(layer_list)
            element_list.append(shape)

    return element_list


def is_connected(element_list, inputs, truthtable, voltage, element) -> None:
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
                                if label.name in outputs:
                                    if truthtable_inputs == inputs:
                                        element.set_attribute(
                                            Attribute(ShapeType.OUTPUT, label.name, output[label.name])
                                        )
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
