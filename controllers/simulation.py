import numpy as np
from scipy.signal import fftconvolve
import cv2

from controllers.GDS_Object.type import ShapeType
from controllers.gds_drawing import vpi_object_extractor


class Simulation:
    def __init__(self):
        self.nm_scale = 2
        self.lam_value = 1300
        self.NA_value = 0.75
        self.is_confocal = True

        self.FOV = 3000

    def print_EOFM_image(self, simulation_object):
        L, psf_label = self.get_psf(FOV=self.FOV)
        R = fftconvolve(simulation_object, L, mode='same')

        return R, psf_label

    def overlay_psf_rcv(self, simulation_object, x_position=1500, y_position=1500):

        points = np.where(simulation_object != 0, 1, 0)

        # X and y are reversed because we are using the matrix with origin lower
        mask, _, value, rcv_label = self.calc_RCV(simulation_object, offset=[y_position, x_position])

        result = cv2.addWeighted(points, 1, mask, 1, 0)

        return result, value, rcv_label

    def get_psf(self, offset=None, FOV=3000):

        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal

        FWHM = get_fwhm(lam, NA)

        label = "FWHM = %.02f, is_confocal = %s" % (FWHM, is_confocal)

        s_x, s_y = (FOV, FOV)  # mat.shape

        # Setting up the position of the laser in the matrix
        if offset is not None:
            xc = offset[0]
            yc = offset[1]
        else:
            xc = s_x // 2
            yc = s_y // 2

        x, y = np.mgrid[0:s_x, 0:s_y]

        # Calculating the r^2 of the laser radius and scale it to nm
        r_squared = (np.square(x - xc) + np.square(y - yc)) * np.square(self.nm_scale)

        # Applying the laser spot’s intensity which follows a Gaussian distribution
        y = 1 / np.sqrt(2 * np.pi * np.square(std_dev(lam, NA))) * np.exp(
            -r_squared / (2 * np.square(std_dev(lam, NA))))

        r = np.sqrt(r_squared)

        if is_confocal:
            radius_max = FWHM
        else:
            radius_max = np.inf

        ind = r <= radius_max

        # Clear values outside of radius_max
        L = y * ind

        return L, label

    def calc_RCV(self, simulation_object, offset=None):

        L, _ = self.get_psf(offset, self.FOV)

        amp_abs = np.sum(simulation_object * L)

        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser

        rcv_label = "RCV (per nm²) = %.6f" % amp_rel

        return np.where(L > 0, 1, 0), L, amp_rel, rcv_label


def get_fwhm(lam, NA):
    return 1.22 / np.sqrt(2) * lam / NA


def std_dev(std_lam, std_na):
    return 0.37 * std_lam / std_na


def rcv_parameter(K, voltage, beta, Pl):
    return voltage * K * beta * Pl


def export_simulation_object(propagation_object, G1, G2, FOV, nm_scale=None):
    if nm_scale is not None:
        scale_up = int(1000 / nm_scale)
    else:
        scale_up = 500

    width = int(propagation_object.get_width() * scale_up)
    height = int(propagation_object.get_height() * scale_up)

    if width > FOV:
        width = FOV

    if height > FOV:
        height = FOV

    layout = np.zeros((height, width))
    x_m, y_m = np.meshgrid(np.arange(width), np.arange(height))

    for reflection in propagation_object.reflection_list:
        for zone in reflection.zone_list:
            x, y = zone.coordinates

            x = tuple([int(element * scale_up) for element in x])
            y = tuple([int(element * scale_up) for element in y])

            state = zone.state
            value = None
            if state is None:
                state = False
            if reflection.shape_type == ShapeType.PMOS:
                if not state:
                    value = G2
            else:
                if state:
                    value = G1

            if value is not None:
                mask = (x_m >= min(x)) & (x_m <= max(x)) & (y_m >= min(y)) & (y_m <= max(y))
                layout[mask] = value

    large_matrix_rows, large_matrix_columns = FOV, FOV
    simulation_object = np.zeros((large_matrix_rows, large_matrix_columns))
    start_row = (large_matrix_rows - height) // 2
    start_col = (large_matrix_columns - width) // 2
    simulation_object[start_row:start_row + height, start_col:start_col + width] = layout

    nm_scale = int(1000 / scale_up)

    return simulation_object, nm_scale


def benchmark_simulation_object(object_list, def_extract, G1, G2, FOV, vpi_extraction=None, area=0, nm_scale=None):
    patch_size = def_extract[0]["patch_size"]

    def_zone = def_extract[1][area]

    ur_x = def_extract[0]["ur_x"]
    ll_x = def_extract[0]["ll_x"]
    ur_y = def_extract[0]["ur_y"]
    ll_y = def_extract[0]["ll_y"]

    width = ur_x - ll_x
    height = ur_y - ll_y

    if width > patch_size:
        width = patch_size
    if height > patch_size:
        height = patch_size

    origin_x = def_zone['position_x']
    origin_y = def_zone['position_y']

    if nm_scale is not None:
        scale_up = int(1000 / nm_scale)
    else:
        scale_up = int(FOV / max(width, height))

    width = int(width * scale_up)
    height = int(height * scale_up)

    if width > FOV:
        width = FOV

    if height > FOV:
        height = FOV

    x_m, y_m = np.meshgrid(np.arange(width), np.arange(height))
    layout = np.zeros((height, width))
    for cell_name, cell_place in def_zone['gates'].items():
        if cell_name in object_list.keys():
            for position in cell_place:
                if vpi_extraction:
                    propagation_object = vpi_object_extractor(object_list[cell_name], cell_name, vpi_extraction,
                                                              position)
                else:
                    key_list = list(object_list[cell_name].keys())
                    key = key_list[0]
                    propagation_object = object_list[cell_name][key]

                for zone in propagation_object.orientation_list[position['Orientation']]:
                    x, y = zone["coords"]
                    x_adder, y_adder = position['Coordinates']
                    x = tuple([int(((element + x_adder) - origin_x) * scale_up) for element in x])
                    y = tuple([int(((element + y_adder) - origin_y) * scale_up) for element in y])

                    state = zone["state"]

                    value = None
                    if state is None:
                        state = False
                    if zone["diff_type"] == ShapeType.PMOS:
                        if not state:
                            value = G2
                    else:
                        if state:
                            value = G1

                    if value is not None:
                        mask = (x_m >= min(x)) & (x_m <= max(x)) & (y_m >= min(y)) & (y_m <= max(y))
                        layout[mask] = value

    large_matrix_rows, large_matrix_columns = FOV, FOV
    simulation_object = np.zeros((large_matrix_rows, large_matrix_columns))
    start_row = (large_matrix_rows - height) // 2
    start_col = (large_matrix_columns - width) // 2
    simulation_object[start_row:start_row + height, start_col:start_col + width] = layout

    nm_scale = int(1000 / scale_up)

    return simulation_object, nm_scale
