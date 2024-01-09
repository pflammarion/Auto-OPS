def parse_info(obj):
    info_str = (
        "Information:\n\n"
        f"Selected cell: {obj.cell_name}\n"
        f"Selected layer: {obj.selected_layer}\n"
        f"State list: {obj.state_list}\n"
        "------------------------------------\n"
        f"X position: {obj.x_position}\n"
        f"Y position: {obj.y_position}\n"
        f"Lam value: {obj.lam_value}\n"
        f"NA value: {obj.NA_value}\n"
        f"Is confocal: {obj.is_confocal}\n"
        "------------------------------------\n"
        f"Kn value: {obj.Kn_value}\n"
        f"Kp value: {obj.Kp_value}\n"
        f"Beta value: {obj.beta_value}\n"
        f"Pl value: {obj.Pl_value}\n"
        f"Voltage value: {obj.voltage_value}\n"
        f"Noise percentage: {obj.noise_pourcentage}\n"
        "------------------------------------\n"
        f"Patch counter: {obj.patch_counter}\n"
        f"Scale up: {obj.scale_up}\n"
        f"Selected area: {obj.selected_area}\n"
        f"Selected patch size: {obj.selected_patch_size}\n"
        f"VPI extraction: {obj.vpi_extraction}\n"
    )

    print(info_str)

