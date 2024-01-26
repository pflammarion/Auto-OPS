import numpy as np
from scipy.signal import fftconvolve
import cv2


def get_fwhm(lam, NA):
    return 1.22 / np.sqrt(2) * lam / NA


def std_dev(std_lam, std_na):
    return 0.37 * std_lam / std_na


class Simulation:
    def __init__(self):
        self.nm_scale = 2
        self.lam_value = 1300
        self.NA_value = 0.75
        self.is_confocal = True

    def print_EOFM_image(self, propagation_object):
        L, psf_label = self.get_psf(FOV=3000)
        R = fftconvolve(propagation_object, L, mode='same')

        return R, psf_label

    def overlay_psf_rcv(self, propagation_object, x_position=1500, y_position=1500):

        points = np.where(propagation_object != 0, 1, 0)

        # X and y are reversed because we are using the matrix with origin lower
        mask, _, value, rcv_label = self.calc_RCV(propagation_object, offset=[y_position, x_position])

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

    def calc_RCV(self, propagation_object, offset=None):

        L, _ = self.get_psf(offset, FOV=3000)

        amp_abs = np.sum(propagation_object * L)

        num_pix_under_laser = np.sum(L > 0)

        amp_rel = amp_abs / num_pix_under_laser

        rcv_label = "RCV (per nm²) = %.6f" % amp_rel

        return np.where(L > 0, 1, 0), L, amp_rel, rcv_label
