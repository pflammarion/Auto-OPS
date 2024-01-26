import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import MultipleLocator


def parse_info(obj):
    if obj.def_file is None:
        is_def_file = "No"
    else:
        is_def_file = "Yes"

    info_str = (
        "\nInformation:\n\n"
        f"cell_name: {obj.cell_name}\n"
        f"selected_layer: {obj.selected_layer}\n"
        f"state_list: {obj.state_list}\n"
        "------------------------------------\n"
        f"x_position: {obj.x_position}\n"
        f"y_position: {obj.y_position}\n"
        f"lam_value: {obj.simulation.lam_value}\n"
        f"NA_value: {obj.simulation.NA_value}\n"
        f"is_confocal: {obj.simulation.is_confocal}\n"
        "------------------------------------\n"
        f"Kn_value: {obj.Kn_value}\n"
        f"Kp_value: {obj.Kp_value}\n"
        f"beta_value: {obj.beta_value}\n"
        f"Pl_value: {obj.Pl_value}\n"
        f"voltage_value: {obj.voltage_value}\n"
        f"noise_percentage: {obj.noise_percentage}\n"
        "------------------------------------\n"
        f"patch_counter: {obj.patch_counter}\n"
        f"nm_scale: {obj.simulation.nm_scale}\n"
        f"selected_area: {obj.selected_area}\n"
        f"selected_patch_size: {obj.selected_patch_size}\n"
        f"vpi_extraction: {obj.vpi_extraction}\n"
        f"flip_flop: {obj.flip_flop}  (if cell has a clock, set the output to 0 or 1)\n"
        "------------------------------------\n"
        f"Is def file ?: {is_def_file} (Can't be changed)"
    )

    print(info_str)


def update_variable(obj, prompt):
    try:
        _, variable, value = prompt.split(' ', 2)
        variable = variable.strip()
        value = value.strip()

        if value is None or value == "":
            value = None

        if hasattr(obj, variable):
            if value is None or value == "":
                value = None

            else:
                if variable == "cell_name" or variable == "state_list":
                    obj.def_file = None
                    value = str(value)

                elif variable == "is_confocal":
                    value = bool(value)

                elif variable == "patch_counter":
                    value = list(value)

                elif variable == "flip_flop":
                    value = int(value)

                elif variable == "vpi_extraction":
                    with open(value, 'r') as file:
                        extract = {}
                        for line in file:
                            key, inputs, outputs = line.strip().split(',')
                            extract[key] = {'inputs': inputs, 'outputs': outputs}

                    value = extract

                else:
                    value = float(value)

            if variable == "lam_value" or variable == "NA_value" or variable == "is_confocal" or variable == "nm_scale":
                setattr(obj.simulation, variable, value)
            else:
                setattr(obj, variable, value)

            print(f"Updated {variable} to: {value}\n"
                  f"Don't forget to save before exporting or plotting to apply all changed values")
        else:
            print(f"Variable {variable} does not exist in the object.")
    except ValueError:
        print("Invalid input format. Please use 'variable value'.")


def plot(image, obj, prompt):
    try:
        if prompt == "psf":
            im = plt.imshow(image, cmap='Reds', origin='lower')
            plt.colorbar(im)
        else:
            plt.imshow(image, cmap='gist_gray', origin='lower')

        if obj.simulation.nm_scale is not None:
            scale = obj.simulation.nm_scale
            scalebar = ScaleBar(scale, units="nm", location="lower left", label=f"1:{scale}nm")
            plt.gca().add_artist(scalebar)
            plt.grid(True, which='both', linestyle='-', linewidth=0.5, color='darkgrey')
            plt.gca().xaxis.set_major_locator(MultipleLocator(scale * 100))
            plt.gca().yaxis.set_major_locator(MultipleLocator(scale * 100))

        plt.title(prompt)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()

    except ValueError:
        print("An error occurred during plotting")
