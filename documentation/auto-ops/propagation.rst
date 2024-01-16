=============================
Auto-OPS propagation library
=============================

To build the Auto-OPS framework we started by the automation of the body voltage propagation over a cell and then compute a complete design from it.

The usage of the Auto-OPS propagation has been explained in the section :ref:`Start Auto-OPS`

Auto-OPS automates the process of performing OP in simulation on a large design’s GDS-II file.

The complete flow of the Auto-OPS framework can be partitioned into six stages and is shown in the following figure:

.. image:: /assets/auto-ops-flow.png
   :align: center
   :alt: Auto-OPS Flow
   :width: 100%

.. raw:: html

   <br/><br/>



In the initial stage (**Stage #1: Design Entry**), a GDS-II file of a design is provided as input to Auto-OPS framework.

Subsequently, in the second stage (**Stage #2: Model Initialization**), the focus shifts to extracting the layout geometry of each distinct logic cell used in the design into node representation.

In the third stage (**Stage #3: Propagation**), Auto-OPS determines voltage propagation across the nodes of the logic cell’s layout geometry based on the applied input pattern.

In the fourth stage (**Stage #4: Extraction**), the extraction process involves identifying the active regions of the logic cell’s layout. It should be noted that Auto-OPS initially identifies distinct logic cells used in the GDS-II file of a design. Next, Auto-OPS passes all the used logic cells’ layouts through the Stages #1-4 of the flow separately. At the end of the Stage #4, Auto-OPS has extracted all the active regions of the used logic cells in the GDS-II file of the design.

The fifth stage (**Stage #5: Composition**) composes the active regions extracted geometry model of each logic cell in the design and creates a new representation of GDS-II file for OP simulation.

Finally, in the sixth stage (**Stage #6: OP Simulation**), the entire design is prepared to perform OP simulation.

The OP simulation is done by the Graphical User Interface. Please refers to :ref:`Reflection Caliber Value`


For more information about the Auto-OPS propagation stages please refer to the paper "Auto-OPS: A Framework For Automated Optical Probing Simulation on GDS-II"



