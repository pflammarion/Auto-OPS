from PyQt6.QtWidgets import QFileDialog
import cv2
import numpy as np
from scipy.signal import fftconvolve


class Controller:
    def __init__(self, view):
        self.view = view

        self.technology_value = 45
        self.Kn_value = 1
        self.Kp_value = -1.3
        self.alpha_value = 0
        self.beta_value = 0
        self.Pl_value = 0
        self.voltage_value = 1.2

        # to initialize the value and the rcv mask
        self.main_label_value = ""
        self.x_position = 1500
        self.y_position = 1500

        self.lam_value = 1300
        self.NA_value = 0.75
        self.is_confocal = True

        lam, G1, G2, Gap = self.parameters_init(self.Kn_value, self.Kp_value, self.voltage_value)
        self.image_matrix = self.draw_layout(lam, G1, G2, Gap)

        self.print_original_image()

    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # TODO check if only one file is selected or more
                image_path = selected_files[0]
                image_read = cv2.imread(image_path)

                if image_read is None:
                    print("Failed to load the image")
                    return

                original_height, original_width, _ = image_read.shape

                # Calculate the center of the image
                center_x, center_y = original_width // 2, original_height // 2

                target_size = (3000, 3000)

                # Calculate the cropping area
                crop_x1 = max(0, center_x - target_size[0] // 2)
                crop_x2 = min(original_width, center_x + target_size[0] // 2)
                crop_y1 = max(0, center_y - target_size[1] // 2)
                crop_y2 = min(original_height, center_y + target_size[1] // 2)

                # Crop and resize the image to the target size
                cropped_resized_image = image_read[crop_y1:crop_y2, crop_x1:crop_x2]
                cropped_resized_image = cv2.resize(cropped_resized_image, target_size)

                gray_image = cv2.cvtColor(cropped_resized_image, cv2.COLOR_BGR2GRAY)
                self.image_matrix = gray_image

                self.view.display_image(self.image_matrix)
                print("Image loaded as a matrix")

    def psf_xy(self, lam, na, x, y, xc, yc, radius_max=np.inf):

        def std_dev(std_lam, std_na):
            return 0.37 * std_lam / std_na

        r = np.sqrt(np.square(x - xc) + np.square(y - yc))
        ind = r <= radius_max

        y = 1 / np.sqrt(2 * np.pi * np.square(std_dev(lam, na))) * np.exp(
            -(np.square(x - xc) + np.square(y - yc)) / (2 * np.square(std_dev(lam, na))))

        # Clear values outside of radius_max
        y = y * ind

        return y

    def psf_2d_pos(self, fov, lam, na, xc, yc, clear_radius=np.inf):
        s_x, s_y = (fov, fov)  # mat.shape
        x, y = np.mgrid[0:s_x, 0:s_y]
        mat = self.psf_xy(lam, na, x, y, xc, yc, clear_radius)
        return mat

    def psf_2d(self, fov, lam, na, clear_radius=np.inf):
        s_x, s_y = (fov, fov)  # mat.shape
        xc = s_x // 2
        yc = s_y // 2
        return self.psf_2d_pos(fov, lam, na, xc, yc, clear_radius)

    def round(self, i):
        return int(np.rint(i))

    def draw_layout(self, lam, G1, G2, Gap):
        layout = np.empty(shape=(1000, 1000))
        layout.fill(0)

        x = self.round(2 * lam)
        y = self.round(4 * lam)
        layout[0:x - 1, 0:y - 1].fill(0)

        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(G1)

        x = x + self.round(4 * lam)
        y = self.round(4 * lam)
        layout[x:x + self.round(12 * lam), 1:self.round(4 * lam)].fill(Gap)

        x = x + self.round(12 * lam)
        y = self.round(4 * lam)
        layout[x:x + self.round(4 * lam), 1:self.round(4 * lam)].fill(0)
        x = x + self.round(4 * lam)
        layout[x:x + self.round(2 * lam), 1:self.round(4 * lam)].fill(G2)

        # Try to center it in a larger field of view
        layout_full = np.empty(shape=(3000, 3000))
        layout_full.fill(0)
        offset = [1250, 1450]
        layout_full[offset[0]:offset[0] + layout.shape[0], offset[1]:offset[1] + layout.shape[1]] = layout

        return layout_full

    def parameters_init(self, Kn, Kp, voltage):
        lam = self.technology_value / 2

        Gate_N = voltage*Kn*1E7
        lam3_N = 4*3*voltage*Kn
        lam4_N = 4*4*voltage*Kn
        lam6_N = 4*6**voltage*Kn

        Gate_P = voltage*Kp*1E7
        lam3_P = 4*3*voltage*Kp
        lam4_P = 4*4*voltage*Kp
        lam6_P = 4*6*voltage*Kp

        G1 = Gate_N
        G2 = Gate_P
        D1 = lam4_N
        D2 = lam4_P
        Gap = 0
        return lam, G1, G2, Gap

    # TODO handle no input number
    def update_physics_values(self):

        self.Kn_value = float(self.view.get_input_Kn())
        self.Kp_value = float(self.view.get_input_Kp())
        self.alpha_value = float(self.view.get_input_alpha())
        self.beta_value = float(self.view.get_input_beta())
        self.Pl_value = float(self.view.get_input_Pl())
        self.voltage_value = float(self.view.get_input_voltage())

        lam, G1, G2, Gap = self.parameters_init(self.Kn_value, self.Kp_value, self.voltage_value)
        self.image_matrix = self.draw_layout(lam, G1, G2, Gap)
        self.view.display_image(self.image_matrix)

        print("Physic info were updated ", self.technology_value, " ", self.voltage_value)

    def calc_and_plot_RCV(self, offset=None):

        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal

        FWHM = 1.22 / np.sqrt(2) * lam / NA
        FOV = 3000
        if not offset:
            L = self.psf_2d(FOV, lam, NA, FWHM // 2 if is_confocal else np.inf)
        else:
            L = self.psf_2d_pos(FOV, lam, NA, offset[0], offset[1], FWHM // 2 if is_confocal else np.inf)

        amp_abs = np.sum(self.image_matrix * L)

        # This is only correct if the full laser spot is in L (if it is not truncated)
        # if is_confocal:
        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser
        self.main_label_value = "RCV (per nm²) = %.6f" % amp_rel

        return np.where(L > 0, 1, 0)

    def update_rcv_position(self):
        self.update_settings()
        self.x_position = 3000 - int(self.view.get_input_x())
        self.y_position = int(self.view.get_input_y())
        self.print_rcv_image()

    def print_original_image(self):
        self.view.display_image(self.image_matrix)

    def print_rcv_image(self):
        self.update_settings()
        points = np.where(self.image_matrix != 0, 1, 0)
        mask = self.calc_and_plot_RCV(offset=[self.y_position, self.x_position])

        result = cv2.addWeighted(points, 1, mask, 0.5, 0)

        self.view.display_image(result)
        self.view.update_main_label_value(self.main_label_value)

    def calc_and_plot_EOFM(self):
        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal
        FWHM = 1.22 / np.sqrt(2) * lam / NA
        FOV = 3000

        self.main_label_value = "FWHM = %.02f, is_confocal = %s" % (FWHM, is_confocal)

        return self.psf_2d(FOV, lam, NA, FWHM // 2 if is_confocal else np.inf)

    def print_EOFM_image(self):
        self.update_settings()
        L = self.calc_and_plot_EOFM()
        R = fftconvolve(self.image_matrix, L, mode='same')

        self.view.display_image(R, True)
        self.view.update_main_label_value(self.main_label_value)

    def update_settings(self):
        self.lam_value = float(self.view.get_input_lam())
        self.NA_value = float(self.view.get_input_NA())
        self.is_confocal = bool(self.view.get_input_confocal())

    def print_psf(self):
        self.update_settings()
        lam = self.lam_value
        NA = self.NA_value
        is_confocal = self.is_confocal

        FWHM = 1.22/np.sqrt(2) * lam/NA
        FOV = 2000
        self.main_label_value = "FWHM = %.02f, is_confocal = %s" % (FWHM, is_confocal)
        L = self.psf_2d(FOV, lam, NA, FWHM//2 if is_confocal else np.inf)
        self.view.display_image(L)
        self.view.update_main_label_value(self.main_label_value)

