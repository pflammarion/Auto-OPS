from PyQt6.QtWidgets import QFileDialog
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Controller:
    def __init__(self, view):
        self.view = view

        self.technology_value = 45
        self.voltage_value = 1.2

        lam, G1, G2, Gap = self.parameters_init()
        self.image_matrix = self.draw_layout(lam, G1, G2, Gap)
        points = np.where(self.image_matrix != 0, 1, 0)
        mask = self.calc_and_plot_RCV()

        result = cv2.addWeighted(points, 1, mask, 0.5, 0)

        self.view.display_image(result)

    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # TODO check if only one file is selected or more
                image_path = selected_files[0]
                image_matrix = cv2.imread(image_path)
                self.view.display_image(image_matrix)
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

    def parameters_init(self):
        Kn = 1
        Kp = -1.3
        lam = self.technology_value / 2

        Gate_N = self.voltage_value * Kn * 1E7
        lam3_N = 4 * 3 * self.voltage_value * Kn
        lam4_N = 4 * 4 * self.voltage_value * Kn
        lam6_N = 4 * 6 ** self.voltage_value * Kn

        Gate_P = self.voltage_value * Kp * 1E7
        lam3_P = 4 * 3 * self.voltage_value * Kp
        lam4_P = 4 * 4 * self.voltage_value * Kp
        lam6_P = 4 * 6 * self.voltage_value * Kp

        G1 = Gate_N
        G2 = Gate_P
        D1 = lam4_N
        D2 = lam4_P
        Gap = 0
        return lam, G1, G2, Gap

    def update_physics_values(self):
        self.technology_value = int(self.view.get_input_tech())
        self.voltage_value = int(self.view.get_input_voltage())

        lam, G1, G2, Gap = self.parameters_init()
        self.image_matrix = self.draw_layout(lam, G1, G2, Gap)
        self.view.display_image(self.image_matrix)

        print("Physic info were updated ", self.technology_value, " ", self.voltage_value)

    def calc_and_plot_RCV(self, lam=1300, NA=0.75, is_confocal=True, offset=None):
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
        print("RCV (per nm²) = %.6f" % amp_rel)

        return np.where(L > 0, 1, 0)
