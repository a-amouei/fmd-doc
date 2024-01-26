Installation
============

Preparing the system
--------------------

Before compiling and installing FMD, a small number of libraries and tools must be installed. FMD depends on a few libraries:

* an MPI implementatin, e.g. MPICH or Open MPI
* HDF5
* GNU Scientific Library

There are various ways to install these libraries. For example, in a Linux distribution, one can install them by using the package manager of the distribution or install them from source code. In Ubuntu [#]_, all the dependencies can be installed by entering one of the following two commands in a terminal emulator:

.. code-block:: console
    :caption: Use this if you prefer MPICH

    sudo apt install libgsl-dev libhdf5-mpich-dev

.. code-block:: console
    :caption: Use this if you prefer Open MPI

    sudo apt install libgsl-dev libhdf5-openmpi-dev

To compile and install FMD you also need Make, which can be installed in Ubuntu with the following command:

.. code-block:: console

    sudo apt install make

Getting the source code of FMD
------------------------------

To get the source code of the latest release of FMD, you can either go to https://github.com/a-amouei/fmd in a web browser and download the ZIP file of the code and then uncompress it, or download it in a Linux terminal with a tool like GNU Wget:

.. code-block:: console

    wget -O FMD.zip https://github.com/a-amouei/fmd/archive/refs/tags/v0.2.0.zip

The downloaded file can be uncompressed by entering the command

.. code-block:: console

    unzip FMD.zip

If you are familiar with the Git version control system and prefer to have a copy of the whole Git repository of FMD, you can use the following command:

.. code-block:: console

    git clone https://github.com/a-amouei/fmd.git

.. note::

   The *master* branch of the Git repository points to the latest release of FMD.

Compiling and installing FMD
----------------------------

Once you have the source code of FMD and have installed the prerequisite libraries and tools, you are ready to compile and install it. In Linux this can be done by changing the current directory of the terminal emulator to ``src`` directory of the source code and entering the following command:

.. code-block:: console

    sudo make install

In Linux distributions other than Ubuntu, some small modifications to ``makefile`` might be needed before entering the command above.

Similarly, FMD can be removed from the system by entering

.. code-block:: console

    sudo make uninstall

.. [#] All commands have been tested on Ubuntu 22.04. They should also work on all other not-too-old versions of Ubuntu.