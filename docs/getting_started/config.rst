.. _Configuration:
=====================
Configuration
=====================

.. contents::
    :local:

Laser
=======

.. code-block:: json

  "laser_config": {
    "lambda": 1300,
    "NA": 1,
    "is_confocal": false,
    "x_position": 1500,
    "y_position": 1500
  }

By default, the laser wavelength (`lambda`) is set to 1300 nm. In practical applications, reducing 𝜆 below 1100 nm is challenging due to silicon's opacity to light in this range.

`NA` refers to the numerical aperture of the microscope system. The highest achievable `NA` with a conventional air-based microscope lens is 1.

Optical resolution can be improved by either decreasing 𝜆 or increasing `NA`. This follows a formulation based on Fourier optics and Abbe’s criterion:

.. math::
    R = \frac{0.5\lambda}{NA}

For further details, refer to `Understanding spatial resolution of laser voltage imaging <https://doi.org/10.1016/j.microrel.2018.07.051>`_ by Venkat Krishnan Ravikumar et al.

The laser can be switched to confocal mode using a boolean value. The laser position can also be adjusted in both `x` and `y` coordinates within the range `[0, 3000]`.


Gates
===================

.. code-block:: json

  "gate_config": {
    "technology": 45,
    "Kn": 1,
    "Kp": 1.3,
    "beta": 1,
    "Pl": 1,
    "voltage": 1,
    "noise_percentage": 5
  }

The `technology` parameter is for UI purposes only and does not affect the configuration.

Please refer to the :ref:`Reflection Caliber Value` section for more details on RCV calculations.

- `Kp` and `Kn` are the transistor amplification constants, where 𝐾 (𝐾𝑃𝑀𝑂𝑆 = 1.3 𝐾𝑁𝑀𝑂𝑆).
- `beta` represents a fabrication-related transistor parameter.
- `Pl` defines the power of the incident laser light.
- `voltage` is the applied voltage at the transistor’s terminals.
- `noise_percentage` represents noise added as a Gaussian distribution in the RCV calculations.


Optical Probing
===================

The default configuration file for the 45nm open-source standard-cell library `FreePDK: An open-source variation-aware design kit <https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=4231502>`_.

.. code-block:: json

    "op_config": {
    "std_file": "input/stdcells.gds",
    "lib_file": "input/stdcells.lib",
    "def_file": "input/hide_inv.def",
    "vpi_file": "input/inputs.vpi",
    "selected_area": "0",
    "selected_patch_size": "1000000",
    "layer_list": [[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]]
  }

- `std_file` contains the standard cell library for Auto-OPS extraction.
- `lib_file` is the Liberty file that Auto-OPS parses to extract cell inputs and outputs.
- `def_file` describes the circuit layout, including cell positioning and orientation.
- `vpi_file` provides Auto-OPS with input and output states based on DEF file identifiers.

  - Each line corresponds to a cell and follows this format: `cell_name, input_index, output_index`.
  - Example: `inv_cell_1,0,1` (output is optional unless the cell is a flip-flop).

- `selected_area` defines patches based on design size. A higher value results in a single patch, but larger patches may increase processing time.

- `layer_list` defines the following layer types:

  - Diffusion layer
  - N-well layer
  - Polysilicon layer
  - Via layers
  - Metal layers
  - Label layers
   These layers are used for Auto-OPS extraction labeling.
