import re


def get_gates_info_from_def_file(file_path) -> list:
    with open(file_path, 'r') as file:
        data = file.read()

    distance_match = re.search(r'UNITS\sDISTANCE\sMICRONS\s(\d+)', data)
    design_size_match = re.search(
        r'DESIGN\sFE_CORE_BOX_LL_X\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_UR_X\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_LL_Y\sREAL\s(\d+\.\d+).*?\n\s*DESIGN\sFE_CORE_BOX_UR_Y\sREAL\s(\d+\.\d+)',
        data)

    dif_size = {}
    gate_dict = {}
    cell_list = []

    if design_size_match and distance_match:
        distance_micron = int(distance_match.group(1))
        dif_size["micron"] = distance_micron

        ll_x = float(design_size_match.group(1))
        ur_x = float(design_size_match.group(2))
        ll_y = float(design_size_match.group(3))
        ur_y = float(design_size_match.group(4))

        dif_size["ur_x"] = ur_x
        dif_size["ll_x"] = ll_x
        dif_size["ur_y"] = ur_y
        dif_size["ll_y"] = ll_y

        # 5um * 5um
        patch_size = 5
        dif_size["patch_size"] = patch_size

        width_patch = int((ur_x-ll_x) / patch_size) + 1
        height_patch = int((ur_y-ll_y) / patch_size) + 1

        for i in range(0, height_patch):
            position_y = ll_y + i * patch_size
            for j in range(0, width_patch):
                position_x = ll_x + j * patch_size
                gate_dict[i * j] = {'position_x': position_x, 'position_y': position_y, 'gates': {}}

        components = re.findall(r'-\s(\w+)\s(\w+)\s\+\sPLACED\s\(\s(\d+)\s(\d+)\s\)\s([A-Z]+)', data)

        for component in components:
            gate_id = component[0]
            gate_name = component[1]
            x_coord = int(component[2])/distance_micron
            y_coord = int(component[3])/distance_micron
            orientation = component[4]

            if gate_name not in cell_list:
                cell_list.append(gate_name)

            for patch_key in gate_dict:
                patch = gate_dict[patch_key]
                if patch['position_x'] <= x_coord < patch['position_x'] + patch_size and \
                        patch['position_y'] <= y_coord < patch['position_y'] + patch_size:

                    if gate_name in patch['gates']:
                        patch['gates'][gate_name].append(
                            {'GateID': gate_id, 'Coordinates': (x_coord, y_coord), 'Orientation': orientation})
                    else:
                        patch['gates'][gate_name] = [
                            {'GateID': gate_id, 'Coordinates': (x_coord, y_coord), 'Orientation': orientation}]

    def_extraction = [dif_size, gate_dict, cell_list]

    return def_extraction
