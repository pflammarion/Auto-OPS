.. Opti-Sim-Plus documentation master file, created by
   sphinx-quickstart on Wed Oct 25 16:45:47 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Opti-Sim-Plus: Logical Gate Reflection's Simulation
===================================================

.. image:: /assets/logo.png
   :align: center
   :alt: Logo

.. raw:: html

   <br/><br/>

In computer security, Intellectual Property (IP) leakage can be performed by Side-Channel Analysis (SCA) attacks on modern chips.

A side-channel attack refers to a security breach which allows the attacker to collect information by measuring indirect impacts of the system or its hardware, rather than directly targeting the program or its code. These SCA attacks and their countermeasures have been studied in literature.

However, in recent years, Optical Probing Attack (OPA), has emerged as a non-invasive and laser-based SCA attack through the backside of chips. OPA can retrieve the chip’s IP by reading out the transistors’ terminal voltage.

Nevertheless, in the literature, there are some countermeasures to mitigate OPA, which are too expensive to implement because they require a significant change in the fabrication process. These existing methods require a whole redesign of logic cells layout, characterization, synthesis, and place and route techniques which can be quite challenging.


.. warning::

   This documentation is a work in progress. We are actively writing it, but if there are things you'd like to be documented in priority, feel free to request in on the `GitHub Repo <https://github.com/pflammarion/Opti-Sim-Plus>`_.



The Opti-Sim-Plus project
-------------------------

.. image:: /assets/opti-sim-plus.png
   :align: center
   :alt: Opti-Sim-Plus project
   :width: 600

.. raw:: html

   <br/><br/>

Currently, conducting optical probing demonstrations can be both challenging and expensive.

The Opti-Sim-Plus project introduces a user-friendly graphical interface designed to simplify and streamline optical probing simulations.

Opti-Sim-Plus is engineered for speed and efficiency, ensuring minimal resource consumption, and is tailored for use by designers and security engineers.


Getting started
---------------------------

Wanna try Opti-Sim-Plus ? You need to install
Wanna try Exegol and join our great community? You need to :ref:`install requirements <install_requirements>` first, then proceed to the :ref:`install requirements <install_requirements>` instructions.



The future of Opti-Sim-Plus
---------------------------

We want this tool to be integrated into the ASIC design flow to provide a high security standard to modern chips.

We also want to connect this tool to the Verilog Procedural Interface (VPI) to provide a security test to designers during their chip creation.


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: GETTING STARTED

   getting_started/introduction
   getting_started/installation
   getting_started/quick-start

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: THE OPTI-SIM-PLUS PROJECT

   the-opti-sim-plus-project/user-interface
   the-opti-sim-plus-project/simulation-workflow
   the-opti-sim-plus-project/advanced-features

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: CONTRIBUTION

   contribution/references


