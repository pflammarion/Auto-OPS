.. Auto-OPS documentation master file, created by
   sphinx-quickstart on Wed Oct 25 16:45:47 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Auto-OPS: A Framework For Automated Optical Probing Simulation on GDS-II
========================================================================

.. image:: /assets/logo.png
   :align: center
   :alt: Logo

.. raw:: html

   <br/><br/>

.. Add the link to the repository and add a section for the def file and their usage

Optical Probing attacks have proven to be a powerful Side Channel analysis attack for bypassing protection mechanisms in integrated circuits. These attacks can extract sensitive information, like security keys or intellectual property (IP).

Researchers have proposed several layout-level countermeasures that designers can use to strengthen their circuits against OP attacks.

Designers need an evaluation environment for OP attacks during the design phase. However, the existing evaluation methods require designers to manually extract the OP-relevant layers from the layouts of logic cells for every possible input combination. This process is complex and error-prone.



The Auto-OPS project
-------------------------

.. image:: /assets/auto-ops.png
   :align: center
   :alt: Auto-OPS project
   :width: 70%

.. raw:: html

   <br/><br/>


In our work, we introduce Auto-OPS, an automated security evaluation framework for OP attacks that can be easily integrated into the ASIC design flow.

We designed and developed Auto-OPS, to automate the process of performing OP in simulation on a full chip design file.


Read the Paper
--------------

You can find the paper at the following link:
`Auto-OPS on IEEE Xplore <https://ieeexplore.ieee.org/document/10793101>`_

This paper have been published in the 7th International Workshop on Secure Hardware, Architectures, and Software, Barcelona, Spain (**SeHAS 2025**) in
collaboration with IEEE Embedded Systems Letters Journal (**IEEE ESL**) and received the **Best Paper Award**.

Abstract
--------

In this work, for the first time, we propose a security evaluation framework, namely **Auto-OPS**, that automates performing the Optical Probing (OP) attack in simulation on a full GDS-II design file. Auto-OPS empowers designers by automatically extracting the active regions' geometry model of each logic cell in the standard cell library or custom-designed logic cells to evaluate the security robustness of a design. Auto-OPS enables scaling up of the current OP evaluation environments, which rely on manual extraction of active regions—an error-prone and cumbersome procedure. Additionally, we evaluated and demonstrated the performance of our framework on several benchmark circuit GDS-II files designed using an open-source 45nm standard cell library.

Citing this Work
----------------

To cite this work, use the following BibTeX entry:

.. code-block:: bibtex

   @ARTICLE{10793101,
      author={Flammarion, Paul and Parvin, Sajjad and Torres, Frank Sill and Drechsler, Rolf},
      journal={IEEE Embedded Systems Letters},
      title={Auto-OPS: A Framework For Automated Optical Probing Simulation on GDS-II},
      year={2024},
      doi={10.1109/LES.2024.3513638}
   }

Acknowledgment
--------------

The work described in this paper has been supported by the **Deutsche Forschungsgemeinschaft (DFG – German Research Foundation)** under the priority programme SPP 2253 – 439918011 in project DR 287/38-1 and SPP 2253 - 535696594 in project DR 287/43-1.


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: GETTING STARTED

   getting_started/installation
   getting_started/quick-start
   getting_started/config

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: THE Auto-OPS PROJECT

   auto-ops/propagation
   auto-ops/user-interface
   auto-ops/gui-cli



