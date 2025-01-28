=====================
Install Auto-OPS
=====================


.. contents::
    :local:

.. _install_requirements:

Requirements
=============

Before using Auto-OPS, the following components are necessary, regardless of the host's operating system:

* Git (`Linux <https://github.com/git-guides/install-git#install-git-on-linux>`__ | `macOS <https://github.com/git-guides/install-git#install-git-on-mac>`__ | `Windows <https://github.com/git-guides/install-git#install-git-on-windows>`__)
* Python3 (`Linux <https://docs.python.org/3/using/unix.html#on-linux>`__ | `macOS <https://www.python.org/downloads/macos/>`__ | `Windows <https://www.python.org/downloads/windows/>`__)
* At least 500MB of free storage


Installation of Auto-OPS
=========================

You can download Auto-OPS from sources with Git:

.. code-block:: bash

   git clone "https://github.com/pflammarion/Auto-OPS"


After the download completed, you can install Auto-OPS with ont of the following methods:

1. Auto-OPS in Python environment
---------------------------------

.. code-block:: bash

   python3 -m pip install --user --requirement "Auto-OPS/requirements.txt"



2. Auto-OPS in Docker environment
---------------------------------

* docker (`Linux <https://docs.docker.com/engine/install/debian/>`__) or Docker Desktop (`macOS <https://docs.docker.com/desktop/install/mac-install/>`__ | `Windows <https://docs.docker.com/desktop/install/windows-install/>`__)

.. code-block:: bash

    make build
    make start
    # or for winpty environment
    make start-winpty


Once the installation is done you can then :doc:`Start Auto-OPS </getting_started/quick-start>`

