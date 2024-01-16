==================================
Graphical User Interface Overview
==================================

The Graphical User Interface (GUI) is split in 5 main windows.

.. contents::
    :local:

For each window there are some parameters that always stays such as the cell, the physical and the laser parameters.

When the values are submitted, all off them get updated and the plot reload with the new values.

To select a cell of the loaded standard cell library, there is a research bar to filter the cell names.

The state list is required to validate the cell. The input pattern is processed as A-Z/0-9 input name order. For example if the cell has 2 inputs A1 and A2, then the entered value has to be 00 (or 01, 10, 11) with the first number for A1 and the second one for A2.

The selected cell and state can be updated or merged. Merging a cell state means a new matrix is generated and copying the new state to it. If another cell state was stored in it, both will me merged. To reset the merged matrix, the reset button set every matrix value to zero. Note: the update has to be saved before clicking on the merge button.

.. image:: /assets/research_bar.png
   :align: center
   :alt: Research bar image
   :width: 200px

.. raw:: html

   <br/><br/>

.. _gui_lps:

Laser Point Spread
==================

The Laser Point Spread is a view where you can see the laser configuration.

The laser has three parameters: Lambda, NA and Confocal.

The optical resolution is given by the following formula:

.. math::
   R = 0.5 \lambda /NA

where 𝜆 denotes the light’s wavelength and Numerical Aperture (NA) represents the Numerical Aperture of the microscope system.

Additionally, the laser spot's intensity follows a Gaussian distribution `as shown here <https://www.sciencedirect.com/science/article/pii/S0026271418306012>`_ as:

.. math::
   p(r) = \frac{1}{\sqrt{2 \pi \sigma^2}} e^\frac{-(r)^2}{2\sigma^2} \label{equ:spread_funct}


where 𝑟 symbolizes the distance measured from the beam’s center, and 𝜎 represents the standard deviation, which can be computed as 𝜎 = 0.37𝜆/NA specifically for a confocal microscope.

The optical resolution can be improved by either reducing 𝜆 or increasing NA.

.. image:: /assets/lps_view.png
   :align: center
   :alt: Laser Point Spread view
   :width: 100%

.. raw:: html

   <br/><br/>

.. _gui_home:

Original Output
=================

The original output view is the preview of the cell with active regions based on the applied input.

This image may change when the physics values are updated: 𝐾𝑁𝑀𝑂𝑆, 𝐾𝑃𝑀𝑂𝑆, 𝛽, 𝑃𝐿, 𝑉.

We approximates the reflected light from an active region of a transistor as a linear function of the voltage applied to transistor’s terminals (𝑉), amplification constant of transistor 𝐾 (𝐾𝑃𝑀𝑂𝑆, 𝐾𝑁𝑀𝑂𝑆), transistor’s fabrication related parameter (𝛽), power of incident laser light (𝑃𝐿), and the area of transistor’s active regions.

This parameters are then stored in the active regions area to compute Optical Probing (OP) later on.

.. math::
   ActiveRegionValue =  K \times \beta \times P_L \times V


.. image:: /assets/GUI.png
   :align: center
   :alt: Original Ouput view
   :width: 100%

.. raw:: html

   <br/><br/>

.. _gui_rcv:

Reflection Caliber Value (RCV)
==============================

In `Toward Optical Probing Resistant Circuits: A Comparison of Logic Styles and Circuit Design Techniques <https://ieeexplore.ieee.org/abstract/document/9712518>`_ , a model is proposed for the transistor’s reflection under OP.

The RCV model approximates the reflected light from an active region of a transistor as a linear function of the voltage applied to transistor’s terminals (𝑉 ), amplification constant of transistor 𝐾 (𝐾𝑃𝑀𝑂𝑆 = 1.3𝐾𝑁𝑀𝑂𝑆), transistor’s fabrication related parameter (𝛽), power of incident laser light (𝑃𝐿), and the area of transistor’s active regions. The RCV value is expressed as follows:

.. math::
   RCV = V \times K \times \beta \times P_L \int_{0}^{2\pi}\int_{0}^{r_{spot}} p(r) \times A(r,\theta) \,drd\theta


where 𝑝(𝑟) and 𝐴(𝑟,𝜃) represent the laser’s Gaussian power distribution and the active region’s area under the laser spot in polar coordinates, respectively. Additionally, this equation can be expanded to include a logic cell consisting of multiple transistors.

While the RCV value is also based on the position of the laser, Auto-OPS has the possibility to change the laser position in the 3000x3000 area.

.. image:: /assets/rcv_view.png
   :align: center
   :alt: Reflection Caliber Value view
   :width: 100%

.. raw:: html

   <br/><br/>

.. _gui_eofm:

Electro-Optical Frequency Mapping (EOFM)
========================================

To localize periodical signals on the chip, the laser can be scanned over the chip and feed the detector’s output into a narrow-width bandpass filter set to the frequency of interest. The measurement results in a gray-scale encoded image of the scanned area, where bright spots indicate areas of switching activity. The corresponding technique is called Electro-Optical Frequency Mapping (EOFM).

Both EOFM and absolute EOFM are shown to the user based on the laser and the physical parameters values.

.. image:: /assets/eofm_view.png
   :align: center
   :alt: Electro-Optical Frequency Mapping view
   :width: 100%

.. raw:: html

   <br/><br/>

.. _gui_csv:

Cell Voltage Modulation
=======================

To go further in the simluation Auto-OPS includs a voltage modulation for the selected cell.

This mode is calucalting, based on a csv file which store the voltage in function of time, the RCV value with  all the set parametters.

To have a more realistic output, Auto-OPS embbed a gaussian distributed noise which can be attapted in the physics parametters.

The csv file can contains multiple columns and they can be selected and updated direclty from the GUI.

This feature can take more or less time based on the lenght of the csv file because it calculate all the RCV values for each modulation of the voltage.

.. image:: /assets/csv_view.png
   :align: center
   :alt: Cell Voltage Modulation view
   :width: 100%

.. raw:: html

   <br/><br/>


