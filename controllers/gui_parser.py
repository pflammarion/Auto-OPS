import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import MultipleLocator

def parse_info(obj):
    info_str = (
        "\nInformation:\n\n"
        f"cell_name: {obj.cell_name}\n"
        f"selected_layer: {obj.selected_layer}\n"
        f"state_list: {obj.state_list}\n"
        "------------------------------------\n"
        f"x_position: {obj.x_position}\n"
        f"y_position: {obj.y_position}\n"
        f"lam_value: {obj.lam_value}\n"
        f"NA_value: {obj.NA_value}\n"
        f"is_confocal: {obj.is_confocal}\n"
        "------------------------------------\n"
        f"Kn_value: {obj.Kn_value}\n"
        f"Kp_value: {obj.Kp_value}\n"
        f"beta_value: {obj.beta_value}\n"
        f"Pl_value: {obj.Pl_value}\n"
        f"voltage_value: {obj.voltage_value}\n"
        f"noise_percentage: {obj.noise_percentage}\n"
        "------------------------------------\n"
        f"patch_counter: {obj.patch_counter}\n"
        f"scale_up: {obj.scale_up}\n"
        f"selected_area: {obj.selected_area}\n"
        f"selected_patch_size: {obj.selected_patch_size}\n"
        f"vpi_extraction: {obj.vpi_extraction}\n"
    )

    print(info_str)


def update_variable(obj, prompt):
    try:
        _, variable, value = prompt.split(' ', 2)
        variable = variable.strip()
        value = value.strip()

        if hasattr(obj, variable):

            if variable == "cell_name" or variable == "state_list":
                obj.def_file = None

            elif variable == "is_confocal":
                value = bool(value)

            elif variable == "patch_counter":
                value = list(value)

            else:
                value = float(value)

            setattr(obj, variable, value)

            print(f"Updated {variable} to: {value}")
        else:
            print(f"Variable {variable} does not exist in the object.")
    except ValueError:
        print("Invalid input format. Please use 'variable value'.")


def plot(image, obj, prompt):
    try:
        if prompt == "lps":
            plt.imshow(image, cmap='Reds', origin='lower')
        else:
            plt.imshow(image, cmap='gist_gray', origin='lower')

        if obj.scale_up is not None:
            scale = obj.scale_up
            scalebar = ScaleBar(1 / scale, units="um", location="lower left", label=f"1:{scale}")
            plt.gca().add_artist(scalebar)
            plt.grid(True, which='both', linestyle='-', linewidth=0.5, color='darkgrey')
            plt.gca().xaxis.set_major_locator(MultipleLocator(scale))
            plt.gca().yaxis.set_major_locator(MultipleLocator(scale))

        plt.title(prompt)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()

    except ValueError:
        print("An error occurred during plotting")
