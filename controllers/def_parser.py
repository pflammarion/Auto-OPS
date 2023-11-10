import re

def get_gates_info_from_def_file(file_path) -> list:

    with open(file_path, 'r') as file:
        data = file.read()


    distance_match = re.search(r'UNITS\sDISTANCE\sMICRONS\s(\d+)', data)
    design_size_match = re.search(r'DESIGN\sFE_CORE_BOX_LL_X\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_UR_X\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_LL_Y\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_UR_Y\sREAL\s(\d+\.\d+)', data)

    dif_size = {}
    if distance_match:
        distance_micron = int(distance_match.group(1))
        dif_size["micron"] = distance_micron

    if design_size_match:
        ll_x = float(design_size_match.group(1))
        ur_x = float(design_size_match.group(2))
        ll_y = float(design_size_match.group(3))
        ur_y = float(design_size_match.group(4))

        dif_size["ur_x"] = ur_x
        dif_size["ll_x"] = ll_x
        dif_size["ur_y"] = ur_y
        dif_size["ll_y"] = ll_y


    components = re.findall(r'-\s(?!.*SOURCE DIST).+?(\w+)\s\+\sPLACED\s\(\s(\d+)\s(\d+)\s\)\s([A-Z]+)', data)

    gate_dict = {}

    for component in components:
        gate_name = component[0]
        x_coord = int(component[1])
        y_coord = int(component[2])
        orientation = component[3]

        if gate_name in gate_dict:
            gate_dict[gate_name].append({'Coordinates': (x_coord, y_coord), 'Orientation': orientation})
        else:
            gate_dict[gate_name] = [{'Coordinates': (x_coord, y_coord), 'Orientation': orientation}]



    dif_extraction = [dif_size, gate_dict]

    return dif_extraction

