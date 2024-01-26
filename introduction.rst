Introduction
============

Free Molecular Dynamics (FMD) is a library for performing classical
molecular dynamics (MD) simulations on different kinds of computers,
from personal computers to computer clusters. It is written in C.

FMD is a growing project. At the moment, its features and capabilities
include:

- It can run on personal computers, workstations, clusters and supercomputers;
   * uses MPI for distributed-memory message-passing parallelism;
   * uses OpenMP for shared-memory parallelism.
- It provides tools for performing combined atomistic-continuum simulations, where MD is combined with finite-difference-based solvers of PDEs [#]_;
   * An example is simulations which use TTM-MD model (see [#]_ & [#]_, for instance).
- It utilizes *events* and event-handlers to interact with calling programs;
   * Events are created when something significant occurs, e.g. when a user-defined *timer* ticks;
   * FMD calls the event-handler set by the calling program to handle those events.
- It can save atomic coordinates in `XYZ <https://en.wikipedia.org/wiki/XYZ_file_format>`_, `VTF <https://github.com/olenz/vtfplugin/wiki/VTF-format>`_ and `CSV <https://en.wikipedia.org/wiki/Comma-separated_values>`_ formats.
- It supports EAM, Morse, and Lennard-Jones potentials.
- It provides Berendsen thermostat.
- It provides microcanonical NVE ensemble.
- It can save *state files* for continuing simulations.

.. [#] Partial Differential Equations
.. [#] https://doi.org/10.1103/PhysRevB.68.064114
.. [#] https://doi.org/10.1016/j.apsusc.2020.147775