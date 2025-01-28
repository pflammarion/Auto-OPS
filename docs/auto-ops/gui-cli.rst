===============================================
Graphical User Interface Command line Overview
===============================================

.. contents::
    :local:

The Auto-OPS GUI embed a Command Line Interface to give the user the possibility to automate experiments.

Not all the GUI features are implemented yet. Please refer to :ref:`Start Auto-OPS GUI CLI` section to see available command.

Here is an example of bash script to save the RCV value of a laser position in a CSV file

.. code-block:: bash

   echo "update cell_name INV_X1"

    for x in {0..1}; do
      echo "update state_list $x"
      for i in {0..30}; do
        position_x=$((100*i))
        echo "update x_position $position_x"
        for j in {0..30}; do
          position_y=$((100*j))
          echo "update y_position $position_y"
          echo "rcv save"
        done
      done
    done





