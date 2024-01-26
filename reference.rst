API reference manual
====================

General notes
-------------

The following sections describe the various components of the API one by one. There are some common aspects among many of those components, which are explained in the present section.

Unless otherwise stated, the physical units for time, length, mass, energy and temperature are picosecond (ps), angstrom (Å), dalton (Da), electronvolt (eV) and kelvin (K) respectively.

Each atom in FMD has a group-ID, which determines to which group it belongs. Groups make it possible to perform certain actions on specific groups of atoms without other atoms being affected. For example, the functions :c:func:`fmd_matt_translate` and :c:func:`fmd_matt_addVelocity` can be used to translate the atoms of a single group in position space and velocity space, respectively. These functions have a ``GroupID`` parameter, specifying on what group the functions act. This parameter can take the special value ``FMD_GROUP_ALL``. In that case, the functions act on all atoms, regardless of the groups to which they belong.

At each moment, either all or one of atom groups is dynamically *active*, which means time integrators update the positions and velocities of the atoms belonging to it, and physical quantities such as kinetic and potential energy are calculated for it. A function like :c:func:`fmd_matt_getKineticEnergy` returns the physical quantity of the active group only. Initially, all groups are active. Time integration functions :c:func:`fmd_dync_equilibrate` and :c:func:`fmd_dync_integrate` can change the active group. Passing ``FMD_GROUP_ALL`` to the time integrator functions makes all groups active.

When the size of the simulation box is set to be :math:`l_x`, :math:`l_y` and :math:`l_z` in the three directions by calling :c:func:`fmd_box_setSize`, the three coordinates of any point inside the box lie in the intervals :math:`\left[0, l_x\right)`, :math:`\left[0, l_y\right)` and :math:`\left[0, l_z\right)`, respectively. Please keep this in mind when translating a group of atoms by :c:func:`fmd_matt_translate` or adding matter to the box by :c:func:`fmd_matt_makeCuboidSC`, :c:func:`fmd_matt_makeCuboidSC_mix`, :c:func:`fmd_matt_makeCuboidBCC`, :c:func:`fmd_matt_makeCuboidBCC_mix`, :c:func:`fmd_matt_makeCuboidFCC` and :c:func:`fmd_matt_makeCuboidFCC_mix`.

FMD utilizes `MPI <https://en.wikipedia.org/wiki/Message_Passing_Interface>`_ for parallel computation. Users of the library do not need to call any MPI subroutine directly. The parallelization strategy used in FMD is called *spatial decomposition*: the simulation box is partitioned into a number of subdomains (set by :c:func:`fmd_box_setSubdomains`) and each subdomain together with everything inside it is assigned to a distinct MPI process. Therefore, the number of processes is not allowed to be less than the number of subdomains. Usually, the number of processes is determined when launching an MPI program. For example, with the command ``mpirun -n 4 ./program.x`` in a terminal emulator, four processes are created from the executable file ``program.x``.

Many functions deal with special kinds of grids called *turies*, and fields defined on them. Temperature and density are examples of fields. Turies and fields can be used either to obtain physical quantities like temperature as functions of position or to combine molecular dynamics with finite difference solvers of partial differential equations representing continuum models. All cells of a turi are of the same size, which is determined by the dimensions of the turi and simulation box. A turi-cell may completely lie within a single subdomain or span two or more subdomains. A turi-cell can even be as large as the simulation box and span all of the subdomains (that is when the dimensions of the turi is :math:`1\times 1\times 1`). In a simulation, each turi together with its fields is treated as independent from other turies, but different fields of the same turi may be dependent on each other. For instance, temperature field is dependent on center-of-mass velocity field. The dependencies are managed automatically by the library. For example, when a temperature field is added to a turi by a call to :c:func:`fmd_field_add`, the library also adds a center-of-mass velocity field, if not already added.

The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This character is either 'r' or 'd', where 'r' stands for *release* and 'd' stands for *development*. Versions of the latter kind are for development and testing by the developers of the library, so here we limit our discussion to release versions. A program written for version X1.Y1.Z1 of the library must also work properly with version X2.Y2.Z2 if X1 = X2 and X1 ≠ 0 and Y1 ≯ Y2. In other cases, it may or may not work. The values of X, Y, Z, and c can be get by :c:func:`fmd_version_getMajor`, :c:func:`fmd_version_getMinor`, :c:func:`fmd_version_getRevision`, and :c:func:`fmd_version_getType`, respectively. The function :c:func:`fmd_version_getString` returns X.Y.Z as a string.

Types and values
----------------

**fmd_array3_t**

.. c:type:: void ***fmd_array3_t

    The data type for a three-dimensional array.

-----

**fmd_array3s_t**

.. c:type:: struct _fmd_array3s fmd_array3s_t

    A variable of this data type is only used for freeing a three-dimensional array with :c:func:`fmd_array3s_free`.

-----

**fmd_EventHandler_t**

.. c:type:: void (*fmd_EventHandler_t)(fmd_t *md, fmd_event_t event, void *usp, fmd_params_t *params)

    This type specifies the prototype of any function which can be accepted as an event-handler. In an event-handler, the value of :c:var:`event` indicates what event has occurred. It also determines the number and types of the extra parameters sent to the event-handler. :c:var:`usp` is a user-given pointer which is passed to the event-handler whenever any event occurs. If the event-handler needs to have access to data from outside of the scope of the event-handler, :c:var:`usp` provides a way in addition to global variables. :c:var:`params` points to an object of `struct` type :c:type:`fmd_params_t` containing the extra parameters. :c:type:`fmd_params_t` is an *incomplete* type, so the library user must typecast :c:var:`params` properly before accessing its members. The following table shows the different events that may occur and the typecast that must be done to access the extra parameters for each event.

    .. list-table:: 
       :widths: 35 35 80
       :header-rows: 1

       * - event
         - value of :c:var:`event`
         - typecast
       * - a user-defined timer ticks
         - :c:enumerator:`FMD_EVENT_TIMER_TICK`
         - :c:expr:`(fmd_event_params_timer_tick_t *)params`
       * - a turi-field is updated
         - :c:enumerator:`FMD_EVENT_FIELD_UPDATE`
         - :c:expr:`(fmd_event_params_field_update_t *)params`

    See also :c:func:`fmd_setEventHandler`.

-----

**fmd_event_params_field_update_t**

.. c:type:: struct _fmd_event_params_field_update fmd_event_params_field_update_t

.. c:struct:: _fmd_event_params_field_update

    .. c:var:: \
        fmd_handle_t turi
        fmd_handle_t field

    When an event-handler is called due to a turi-field update event, the :c:var:`params` parameter of the event-handler contains an :c:type:`fmd_event_params_field_update_t`. The pair of :c:var:`turi` and :c:var:`field` determines which turi-field was updated. See also :c:type:`fmd_EventHandler_t`.

-----

**fmd_event_params_timer_tick_t**

.. c:type:: struct _fmd_event_params_timer_tick fmd_event_params_timer_tick_t

.. c:struct:: _fmd_event_params_timer_tick

    .. c:var:: \
        fmd_handle_t timer

    When a user-defined timer ticks, the event-handler is called, assuming that it exists. In this case, the :c:var:`params` parameter of the event-handler contains an :c:type:`fmd_event_params_timer_tick_t`. :c:var:`timer` is the handle of the timer producing the event. See also :c:type:`fmd_EventHandler_t`.

-----

**fmd_event_t**

.. c:type:: enum _fmd_event fmd_event_t

.. c:enum:: _fmd_event

    .. c:enumerator:: \
        FMD_EVENT_TIMER_TICK
        FMD_EVENT_FIELD_UPDATE

    The type of one of the input parameters of an event-handler, which specifies the occurred event. See also :c:type:`fmd_EventHandler_t`.

-----

**fmd_field_t**

.. c:type:: enum _fmd_field fmd_field_t

.. c:enum:: _fmd_field

    .. c:enumerator:: \
        FMD_FIELD_MASS
        FMD_FIELD_VCM
        FMD_FIELD_TEMPERATURE
        FMD_FIELD_NUMBER
        FMD_FIELD_NUMBER_DENSITY
        FMD_FIELD_TTM_TE
        FMD_FIELD_TTM_XI

    This type is used to specify the *category* of a field. The following table describes each field category.

    .. list-table:: 
       :widths: 35 80
       :header-rows: 1

       * - field category
         - description
       * - :c:enumerator:`FMD_FIELD_MASS`
         - total mass of all atoms in turi-cell
       * - :c:enumerator:`FMD_FIELD_VCM`
         - center-of-mass velocity of the atoms in turi-cell
       * - :c:enumerator:`FMD_FIELD_TEMPERATURE`
         - temperature of the atoms in turi-cell
       * - :c:enumerator:`FMD_FIELD_NUMBER`
         - number of atoms in turi-cell
       * - :c:enumerator:`FMD_FIELD_NUMBER_DENSITY`
         - number of atoms in turi-cell divided by its volume
       * - :c:enumerator:`FMD_FIELD_TTM_TE`
         - electron temperature in TTM turies (*)
       * - :c:enumerator:`FMD_FIELD_TTM_XI`
         - quantity :math:`\xi` in TTM turies (*)

    Categories marked with an asterisk (*) in their descriptions should not be added manually to a turi. They are automatically added when certain categories of turies are added to a simulation. Fields can be manually added by calling :c:func:`fmd_field_add`. Turies and fields are introduced in `General notes`_.

-----

**fmd_handle_t**

.. c:type:: int fmd_handle_t

    An :c:type:`fmd_handle_t` is a handle to some objects within an :c:type:`fmd_t`, like turies, turi-fields, and user-defined timers. API functions creating such objects return an :c:type:`fmd_handle_t`. These handles are used to refer to the objects in subsequent API calls. They are also used in event-handlers to recognize to what object an event is related.

-----

**fmd_params_t**

.. c:type:: struct _fmd_params fmd_params_t

    One of the parameters of an event-handler is of this type. FMD uses that parameter to send any extra event-specific parameters to the event-handler. Its actual contents depend on what event has occurred. Since :c:type:`fmd_params_t` is an *incomplete* type, a typecast is required for accessing its contents. See also :c:type:`fmd_EventHandler_t`.

-----

**fmd_pot_t**

.. c:type:: struct _fmd_pot fmd_pot_t

    The data type for interatomic potential functions.

-----

**fmd_real_t**

.. c:type:: double fmd_real_t

    The floating-point data type in FMD. By default, the library is compiled with double precision.

-----

**fmd_rtriple_t**

.. c:type:: fmd_real_t fmd_rtriple_t[3]

    The data type for a `triple (3-tuple) <https://en.wikipedia.org/wiki/Tuple>`_ of :c:type:`fmd_real_t` values.

-----

**fmd_SaveConfigMode_t**

.. c:type:: enum _fmd_SaveConfigMode fmd_SaveConfigMode_t

.. c:enum:: _fmd_SaveConfigMode

    .. c:enumerator:: \
        FMD_SCM_XYZ_ATOMSNUM
        FMD_SCM_XYZ_SEPARATE
        FMD_SCM_CSV
        FMD_SCM_VTF

    This type is used to specify the mode of configuration saving. The following table shows what each value means. The word *snapshot* refers to the data saved with a single call to :c:func:`fmd_matt_saveConfiguration`.

    .. list-table:: 
       :widths: 22 30 12 30
       :header-rows: 1

       * - value
         - file naming
         - format
         - No. of snapshots per file
       * - :c:enumerator:`FMD_SCM_XYZ_ATOMSNUM`
         - No. of existing atoms + ``.xyz``
         - `XYZ <https://en.wikipedia.org/wiki/XYZ_file_format>`_
         - 1 or more
       * - :c:enumerator:`FMD_SCM_XYZ_SEPARATE`
         - ``00000.xyz``, ``00001.xyz``, ...
         - `XYZ <https://en.wikipedia.org/wiki/XYZ_file_format>`_
         - 1
       * - :c:enumerator:`FMD_SCM_CSV`
         - ``00000.csv``, ``00001.csv``, ...
         - `CSV <https://en.wikipedia.org/wiki/Comma-separated_values>`_
         - 1
       * - :c:enumerator:`FMD_SCM_VTF`
         - ``00000.vtf``, ``00001.vtf``, ...
         - `VTF <https://github.com/olenz/vtfplugin/wiki/VTF-format>`_
         - 1

-----

**fmd_string_t**

.. c:type:: char *fmd_string_t

   The string data type.

-----

**fmd_t**

.. c:type:: struct _fmd fmd_t

    This is the main type in FMD. An :c:type:`fmd_t` is associated with each simulation. It contains the state of a simulation and all objects related to it. :c:func:`fmd_create` creates an :c:type:`fmd_t` object and :c:func:`fmd_free` frees it.

-----

**fmd_ttm_coupling_factor_constant_t**

.. c:type:: struct _fmd_ttm_coupling_factor_constant fmd_ttm_coupling_factor_constant_t

.. c:struct:: _fmd_ttm_coupling_factor_constant

    .. c:var:: \
        fmd_real_t value

    Either this data type or :c:type:`fmd_real_t` must be used to set the coupling factor for a TTM turi of category :c:enumerator:`FMD_TURI_TTM_TYPE1`. In this case, the coupling factor is a constant. The physical unit of :c:var:`value` is W/(:math:`\mathrm{m}^3`.K), where W, m and K are watt, meter and kelvin, respectively. See :c:func:`fmd_turi_add` and :c:func:`fmd_ttm_setCouplingFactor` for more information.

-----

**fmd_ttm_heat_capacity_linear_t**

.. c:type:: struct _fmd_ttm_heat_capacity_linear fmd_ttm_heat_capacity_linear_t

.. c:struct:: _fmd_ttm_heat_capacity_linear

    .. c:var:: \
        fmd_real_t gamma

    This data type must be used to set the electron heat capacity for a TTM turi of category :c:enumerator:`FMD_TURI_TTM_TYPE1`. In this case, the electron heat capacity is a linear function of electron temperature, i.e. :math:`C_\mathrm{e}=\gamma T_\mathrm{e}`, where :math:`\gamma` (:c:var:`gamma`) is a constant with physical unit of J/(:math:`\mathrm{m}^3\mathrm{K}^2`). Here, J, m and K are joule, meter and kelvin, respectively. See :c:func:`fmd_turi_add` and :c:func:`fmd_ttm_setHeatCapacity` for more information.

-----

**fmd_ttm_heat_conductivity_constant_t**

.. c:type:: struct _fmd_ttm_heat_conductivity_constant fmd_ttm_heat_conductivity_constant_t

.. c:struct:: _fmd_ttm_heat_conductivity_constant

    .. c:var:: \
        fmd_real_t value

    Either this data type or :c:type:`fmd_real_t` must be used to set the electron heat conductivity for a TTM turi of category :c:enumerator:`FMD_TURI_TTM_TYPE1`. In this case, the electron heat conductivity is a constant. The physical unit of :c:var:`value` is W/(m.K), where W, m and K are watt, meter and kelvin, respectively. See :c:func:`fmd_turi_add` and :c:func:`fmd_ttm_setHeatConductivity` for more information.

-----

**fmd_ttm_laser_gaussian_t**

.. c:type:: struct _fmd_ttm_laser_gaussian fmd_ttm_laser_gaussian_t

.. c:struct:: _fmd_ttm_laser_gaussian

    .. c:var:: \
        fmd_real_t fluence
        fmd_real_t reflectance
        fmd_real_t t0
        fmd_real_t duration
        fmd_real_t AbsorptionDepth

    This data type must be used to set the laser source term for a TTM turi of category :c:enumerator:`FMD_TURI_TTM_TYPE1`. In this case, the laser source term has the following spatio-temporal dependence:

    .. math ::

        S(z,t)=I_0 (1-R) L_\mathrm{a}^{-1} \exp\left(-\frac{z}{L_\mathrm{a}}\right) \exp\left[-\frac{(t-t_0)^2}{2\sigma_\mathrm{L}^2}\right].

    Here, :math:`z` is the difference between the third coordinate of any point in the simulation box and the least third coordinate of all atoms. The latter is calculated just before time integration is started. Also, in the equation above, :math:`R` is the reflectance of the target, :math:`L_\mathrm{a}` is the absorption depth, and :math:`t_0` is the time when laser intensity reaches its peak. The quantity :math:`\sigma_\mathrm{L}` is related to the FWHM duration of the pulse, :math:`\tau_\mathrm{L}`, by :math:`\tau_\mathrm{L}=\sigma_\mathrm{L}\sqrt{8\ln 2}`, and the peak intensity, :math:`I_0`, is related to the laser fluence, :math:`F`, by :math:`F=I_0 \tau_\mathrm{L}\sqrt{\pi/4\ln 2}`. The parameters :c:var:`fluence`, :c:var:`reflectance`, :c:var:`t0`, :c:var:`duration` and :c:var:`AbsorptionDepth` correspond with :math:`F`, :math:`R`, :math:`t_0`, :math:`\tau_\mathrm{L}` and :math:`L_\mathrm{a}`, respectively. The physical units of :c:var:`fluence`, :c:var:`t0`, :c:var:`duration` and :c:var:`AbsorptionDepth` are J/:math:`\mathrm{m}^2`, s, s and m, respectively. Reflectance is dimensionless. See :c:func:`fmd_turi_add` and :c:func:`fmd_ttm_setLaserSource` for more information.

-----

**fmd_turi_t**

.. c:type:: enum _fmd_turi fmd_turi_t

.. c:enum:: _fmd_turi

    .. c:enumerator:: \
        FMD_TURI_CUSTOM
        FMD_TURI_TTM_TYPE1

    This type is used to specify the *category* of a turi. See :c:func:`fmd_turi_add` for more information.

-----

**fmd_utriple_t**

.. c:type:: unsigned fmd_utriple_t[3]

    The data type for a `triple (3-tuple) <https://en.wikipedia.org/wiki/Tuple>`_ of ``unsigned int`` values.

Functions
---------

**fmd_array3s_free()**

.. c:function:: void fmd_array3s_free(fmd_array3s_t *array)

    :param array: the array to be freed

    Frees a three-dimensional array.

-----

**fmd_box_setPBC()**

.. c:function:: void fmd_box_setPBC(fmd_t *md, bool PBCx, bool PBCy, bool PBCz)

    :param md: an :c:type:`fmd_t`
    :param PBCx: the desired state of PBC in x direction
    :param PBCy: the desired state of PBC in y direction
    :param PBCz: the desired state of PBC in z direction

    Sets periodic boundary conditions (PBC) in different directions. A value of ``true`` for any of the PBC state parameters causes PBC to be applied in the associated direction. In contrast, a value of ``false`` for any direction means that PBC is NOT to be applied in that direction. By default, PBC is not applied in any direction.

-----

**fmd_box_setSize()**

.. c:function:: void fmd_box_setSize(fmd_t *md, fmd_real_t sx, fmd_real_t sy, fmd_real_t sz)

    :param md: an :c:type:`fmd_t`
    :param sx: the size in x direction
    :param sy: the size in y direction
    :param sz: the size in z direction

    Sets the size of the simulation box.

-----

**fmd_box_setSubdomains()**

.. c:function:: bool fmd_box_setSubdomains(fmd_t *md, int dimx, int dimy, int dimz)

    :param md: an :c:type:`fmd_t`
    :param dimx: dimension of the subdomain grid in x direction
    :param dimy: dimension of the subdomain grid in y direction
    :param dimz: dimension of the subdomain grid in z direction
    :returns: ``true``, if the current process is associated with a subdomain; ``false``, otherwise.

    Defines how the simulation box is partitioned into subdomains. The dimensions of the subdomain grid are :c:var:`dimx` :math:`\times` :c:var:`dimy` :math:`\times` :c:var:`dimz`. If the returned value is neglected, it can later be get by :c:func:`fmd_proc_hasSubdomain`.

-----

**fmd_create()**

.. c:function:: fmd_t *fmd_create()

    :returns: a pointer to the created :c:type:`fmd_t` object

    Creates an :c:type:`fmd_t` object and initializes it with default values for various parameters.

-----

**fmd_dync_equilibrate()**

.. c:function:: void fmd_dync_equilibrate(fmd_t *md, int GroupID, fmd_real_t duration, fmd_real_t timestep, fmd_real_t tau, fmd_real_t temperature)

    :param md: an :c:type:`fmd_t`
    :param GroupID: the group to become active
    :param duration: the duration of time integration
    :param timestep: the timestep used in time integration (:math:`\delta t`)
    :param tau: the parameter :math:`\tau` of Berendsen thermostat
    :param temperature: the desired temperature (:math:`T_0`)

    Uses Berendsen thermostat and velocity Verlet algorithm to equilibrate an atom group to the desired temperature. At each time step, the atom velocities are scaled from :math:`\mathbf{v}` to :math:`\lambda\mathbf{v}`, where :math:`\lambda` is calculated by

    .. math::

        \lambda = \left[1+\frac{\delta t}{\tau}\left(\frac{T_0}{T}-1\right)\right]^{1/2}.

    Here, :math:`T` is the instantaneous temperature. Other quantities in the equation are defined above. If :c:var:`GroupID` is equal to ``FMD_GROUP_ALL``, all groups become active. Otherwise, that particular group becomes active. The concept of active group is explained in `General notes`_. This function first sets the simulation time to zero, but finally, when the time integration is done, restores the initial time. The function may not work properly in certain situations (for example, when the active group has non-zero center-of-mass velocity).

-----

**fmd_dync_getTime()**

.. c:function:: fmd_real_t fmd_dync_getTime(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the current simulation time

-----

**fmd_dync_getTimestep()**

.. c:function:: fmd_real_t fmd_dync_getTimestep(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the timestep used in MD time integration

    The timestep is set by the last :c:func:`fmd_dync_integrate` or :c:func:`fmd_dync_equilibrate` call.

-----

**fmd_dync_integrate()**

.. c:function:: void fmd_dync_integrate(fmd_t *md, int GroupID, fmd_real_t duration, fmd_real_t timestep)

    :param md: an :c:type:`fmd_t`
    :param GroupID: the group to become active
    :param duration: the duration of time integration
    :param timestep: the timestep used in time integration

    Integrates the Newton's equations of motion for all atoms of group :c:var:`GroupID` for a duration equal to :c:var:`duration` with a timestep of :c:var:`timestep`. If a TTM turi is defined over :c:var:`md`, semi-implicit Euler integration method is used (See :c:func:`fmd_turi_add` for more information). Otherwise, velocity Verlet algorithm is used for time integration. If :c:var:`GroupID` is equal to ``FMD_GROUP_ALL``, all groups become active. Otherwise, that particular group becomes active. The concept of active group is explained in `General notes`_.

-----

**fmd_field_add()**

.. c:function:: fmd_handle_t fmd_field_add(fmd_t *md, fmd_handle_t turi, fmd_field_t cat, fmd_real_t interval)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the turi to which the field is to be added
    :param cat: the category of the field
    :param interval: the simulation-time interval between two subsequent field updates
    :returns: the handle to the field

    Adds a field of category :c:var:`cat` and its dependencies to the given turi, if not already added. It also makes sure that the field and its dependencies are updated with the given time interval between any two subsequent updates. A particular field can have multiple update time-intervals. The following table shows the different field categories a user can manually add to a turi and their immediate dependencies.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - field category
         - dependencies
       * - :c:enumerator:`FMD_FIELD_MASS`
         - 
       * - :c:enumerator:`FMD_FIELD_VCM`
         - :c:enumerator:`FMD_FIELD_MASS`
       * - :c:enumerator:`FMD_FIELD_TEMPERATURE`
         - :c:enumerator:`FMD_FIELD_VCM`, :c:enumerator:`FMD_FIELD_NUMBER`
       * - :c:enumerator:`FMD_FIELD_NUMBER`
         - 
       * - :c:enumerator:`FMD_FIELD_NUMBER_DENSITY`
         - :c:enumerator:`FMD_FIELD_NUMBER`

    Turies and fields are introduced in `General notes`_. See also :c:type:`fmd_field_t`, :c:func:`fmd_field_find` and :c:func:`fmd_turi_add`.

-----

**fmd_field_find()**

.. c:function:: fmd_handle_t fmd_field_find(fmd_t *md, fmd_handle_t turi, fmd_field_t cat)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the turi in which the search takes place
    :param cat: the category of the field to search for
    :returns: the handle to the field, if found; a negative number, otherwise.

    Searches for a field of category :c:var:`cat` in the turi specified by :c:var:`turi`.

-----

**fmd_field_getArray()**

.. c:function:: fmd_array3s_t *fmd_field_getArray(fmd_t *md, fmd_handle_t turi, fmd_handle_t field, fmd_array3_t *array, fmd_utriple_t dims)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the turi where the field exists
    :param field: the handle to the field
    :param array: the output array
    :param dims: the dimensions of the output array
    :returns: a pointer which should be used for freeing the array

    .. note:: This function must be called by all processes, but its outputs (i.e. the parameters :c:var:`array` and :c:var:`dims`) are valid only on the root process. To identify the root process, use :c:func:`fmd_proc_isRoot`.

    Makes a three-dimensional array from the field specified by :c:var:`turi` and :c:var:`field`. This function can be called in a event-handler when a field-update event has occurred. The parameters :c:var:`array` and :c:var:`dims` are used to output the array and its dimensions. The dimensions of the array are written in :c:expr:`dims[0]`, :c:expr:`dims[1]` and :c:expr:`dims[2]`. As the following table shows, the data type of each element of the output array depends on the field category.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - field category
         - element type
       * - :c:enumerator:`FMD_FIELD_MASS`
         - :c:type:`fmd_real_t`
       * - :c:enumerator:`FMD_FIELD_VCM`
         - :c:type:`fmd_rtriple_t`
       * - :c:enumerator:`FMD_FIELD_TEMPERATURE`
         - :c:type:`fmd_real_t`
       * - :c:enumerator:`FMD_FIELD_NUMBER`
         - ``unsigned int``
       * - :c:enumerator:`FMD_FIELD_NUMBER_DENSITY`
         - :c:type:`fmd_real_t`
       * - :c:enumerator:`FMD_FIELD_TTM_TE`
         - :c:type:`fmd_real_t`
       * - :c:enumerator:`FMD_FIELD_TTM_XI`
         - :c:type:`fmd_real_t`

Once the user has nothing more to do with the output array, it should be freed by passing the returned value to :c:func:`fmd_array3s_free`.

-----

**fmd_field_save_as_hdf5()**

.. c:function:: void fmd_field_save_as_hdf5(fmd_t *md, fmd_handle_t turi, fmd_handle_t field, fmd_string_t filename)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the turi where the field exists
    :param field: the handle to the field to be saved to disk
    :param filename: the name of the file on disk

    Saves the field specified by :c:var:`turi` and :c:var:`field` as an HDF5 file with the given name on disk. The file will include VizSchema metadata describing the data. It can be opened with visualization tools such as VisIt and ParaView. This function can be called in a event-handler when a field-update event has occurred. The path to the directory where the file is saved can be changed with :c:func:`fmd_io_setSaveDirectory`.

-----

**fmd_free()**

.. c:function:: void fmd_free(fmd_t *md)

    :param md: an :c:type:`fmd_t`

    Frees :c:var:`md` and all associated resources.

-----

**fmd_io_loadState()**

.. c:function:: void fmd_io_loadState(fmd_t *md, fmd_string_t path, bool UseTime)

    :param md: an :c:type:`fmd_t`
    :param path: the path to the state file on disk
    :param UseTime: specifies whether to change the simulation time to the time inside the file

    Loads a state file. If :c:var:`UseTime` is equal to ``true``, the simulation time is changed to the time value read from the file, which is the simulation time when the file was saved. If the dimensions of the simulation box are not already set (e.g. with a previous :c:func:`fmd_box_setSize` call), they are set with values read from the state file. Similarly, if the states of periodic boundary conditions (PBC) are not already set (e.g. with a previous :c:func:`fmd_box_setPBC`), they are set with values read from the file. All atoms inside the state file are added to the simulation box. Any atoms already existing in the simulation box are not affected. See also :c:func:`fmd_io_saveState`. Groups are explained in `General notes`_.

-----

**fmd_io_printf()**

.. c:function:: void fmd_io_printf(fmd_t *md, const fmd_string_t restrict format, ...)

    :param md: an :c:type:`fmd_t`
    :param format: the format string passed to :c:func:`printf`
    :param ...: the other parameters passed to :c:func:`printf`

    Calls :c:func:`printf` of the C standard library on the *root* MPI process only. See also :c:func:`fmd_proc_isRoot`.

-----

**fmd_io_saveState()**

.. c:function:: void fmd_io_saveState(fmd_t *md, fmd_string_t filename)

    :param md: an :c:type:`fmd_t`
    :param filename: the name of the state file

    Saves the state of a simulation to a file on disk. The saved data include the simulation time when the state was saved, the number of atoms, the dimensions of the simulation box, the state of periodic boundary conditions in the three directions, and the name, group-ID, position and velocity of each atom. The path to the directory where the file is saved can be changed with :c:func:`fmd_io_setSaveDirectory`. A state file can later be loaded with :c:func:`fmd_io_loadState` in order to, for example, continue a simulation. Groups are explained in `General notes`_.

-----

**fmd_io_setSaveConfigMode()**

.. c:function:: void fmd_io_setSaveConfigMode(fmd_t *md, fmd_SaveConfigMode_t mode)

    :param md: an :c:type:`fmd_t`
    :param mode: the new mode of configuration saving

    Changes the mode of configuration saving. See :c:type:`fmd_SaveConfigMode_t` for a description of the available modes.

-----

**fmd_io_setSaveDirectory()**

.. c:function:: void fmd_io_setSaveDirectory(fmd_t *md, fmd_string_t directory)

    :param md: an :c:type:`fmd_t`
    :param directory: the path of the directory

    Sets the path of the directory in which FMD saves all output files. The string :c:var:`directory` must either be empty or end with the path separator character of the operating system (e.g. slash ("/") in Unix-like operating systems). If the directory does not exist, it is NOT created by FMD.

-----

**fmd_matt_addVelocity()**

.. c:function:: void fmd_matt_addVelocity(fmd_t *md, int GroupID, fmd_real_t vx, fmd_real_t vy, fmd_real_t vz)

    :param md: an :c:type:`fmd_t`
    :param GroupID: specifies the group on which the function acts
    :param vx: the velocity change in x direction
    :param vy: the velocity change in y direction
    :param vz: the velocity change in z direction

    Adds the same amount to the velocities of all atoms in group :c:var:`GroupID`. Groups are explained in `General notes`_.

-----

**fmd_matt_changeGroupID()**

.. c:function:: void fmd_matt_changeGroupID(fmd_t *md, int old, int new)

    :param md: an :c:type:`fmd_t`
    :param old: the old group-ID
    :param new: the new group-ID

    Changes the group-ID of atoms with group-ID :c:var:`old` to :c:var:`new`. The parameter :c:var:`old` can take ``FMD_GROUP_ALL`` as a special value. In that case, the group-ID of any atom in the simulation box is changed. :c:var:`new` must be a non-negative integer. Groups are explained in `General notes`_.

-----

**fmd_matt_findLimits()**

.. c:function:: void fmd_matt_findLimits(fmd_t *md, int GroupID, fmd_rtriple_t LowerLimit, fmd_rtriple_t UpperLimit)

    :param md: an :c:type:`fmd_t`
    :param GroupID: specifies the group on which the function acts
    :param LowerLimit: the output for lower limits
    :param UpperLimit: the output for upper limits

    Writes in :c:expr:`LowerLimit[i]` the smallest :c:expr:`i`-th coordinate of all atoms from the specified group, and writes in :c:expr:`UpperLimit[i]` the largest :c:expr:`i`-th coordinate of all atoms from that group. Here :c:expr:`i` (:math:`=0,1,2`) denotes any of the three directions. Groups are explained in `General notes`_.

-----

**fmd_matt_getKineticEnergy()**

.. c:function:: fmd_real_t fmd_matt_getKineticEnergy(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the sum of the kinetic energies of all atoms of the active group

    The concept of active group is explained in `General notes`_.

-----

**fmd_matt_getMomentum()**

.. c:function:: void fmd_matt_getMomentum(fmd_t *md, fmd_rtriple_t out)

    :param md: an :c:type:`fmd_t`
    :param out: the output of the function

    Writes the three components of the momentum vector of the active group in :c:expr:`out[0]`, :c:expr:`out[1]` and :c:expr:`out[2]`. The concept of active group is explained in `General notes`_.

-----

**fmd_matt_getTemperature()**

.. c:function:: fmd_real_t fmd_matt_getTemperature(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the instantaneous temperature of the active group, assuming that it is in thermodynamic equilibrium and its center-of-mass velocity is zero

    The concept of active group is explained in `General notes`_.

-----

**fmd_matt_getTotalEnergy()**

.. c:function:: fmd_real_t fmd_matt_getTotalEnergy(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the sum of kinetic energies and potential energies of all atoms in the active group

    The concept of active group is explained in `General notes`_.

    .. warning::

        In the current version of the library, this function can be used in an event-handler when a timer has ticked. It can also be used in an event-handler when a turi-field update has occurred, but only if there is no TTM turi in the simulation. If called in other circumstances, whether inside or outside an event-handler, the returned value is unreliable. This can be regarded as a known bug.

-----

**fmd_matt_giveMaxwellDistribution()**

.. c:function:: void fmd_matt_giveMaxwellDistribution(fmd_t *md, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param GroupID: specifies the group on which the function acts
    :param temp: the desired temperature

    Gives the atoms of the group specified by :c:var:`GroupID` velocities that have a Maxwell-Boltzmann distribution corresponding to the temperature :c:var:`temp`. The atoms may need to be equilibrated with :c:func:`fmd_dync_equilibrate` to reach the desired temperature. Groups are explained in `General notes`_.

-----

**fmd_matt_makeCuboidBCC()**

.. c:function:: void fmd_matt_makeCuboidBCC(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, unsigned atomkind, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param atomkind: the index of the atom-kind in the array of atom-kinds
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    The same as :c:func:`fmd_matt_makeCuboidBCC_mix`, except that all created atoms are of the same atom-kind.

-----

**fmd_matt_makeCuboidBCC_mix()**

.. c:function:: void fmd_matt_makeCuboidBCC_mix(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, fmd_real_t *ratio, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param ratio: the ratio of the mixture
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    Creates a structure of atoms with cuboid outline by adding a single atom of random atom-kind to any point of a *finite* body-centered cubic (BCC) lattice. A conventional cell indexed by :math:`i`, :math:`j` and :math:`k`, where :math:`i=0,\dots,\mathrm{dimx}-1` and :math:`j=0,\dots,\mathrm{dimy}-1` and :math:`k=0,\dots,\mathrm{dimz}-1`, will have two atoms placed at

    .. math::

        x_1=\mathrm{x}+\left(i+\frac{1}{4}\right)\times\mathrm{lp},\quad y_1=\mathrm{y}+\left(j+\frac{1}{4}\right)\times\mathrm{lp},\quad z_1=\mathrm{z}+\left(k+\frac{1}{4}\right)\times\mathrm{lp},

    and

    .. math::

        x_2=\mathrm{x}+\left(i+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad y_2=\mathrm{y}+\left(j+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad z_2=\mathrm{z}+\left(k+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp}.

    A total of 2 :math:`\times` :c:var:`dimx` :math:`\times` :c:var:`dimy` :math:`\times` :c:var:`dimz` atoms are added to the simulation box. The probability that any single atom in the created structure is of p-th atom-kind is equal to

    .. math::

        \frac{\text{ratio[p]}}{{\displaystyle\sum_{\text{q}=0}^{N-1} \text{ratio[q]}}},

    where :math:`N` is the number of atom-kinds set by :c:func:`fmd_matt_setAtomKinds`. :c:var:`GroupID` must be a non-negative integer value. The atoms are given velocities that have a Maxwell-Boltzmann distribution corresponding to the temperature :c:var:`temp`. The created structure must be equilibrated with :c:func:`fmd_dync_equilibrate` to reach the desired temperature. Groups are explained in `General notes`_.

-----

**fmd_matt_makeCuboidFCC()**

.. c:function:: void fmd_matt_makeCuboidFCC(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, unsigned atomkind, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param atomkind: the index of the atom-kind in the array of atom-kinds
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    The same as :c:func:`fmd_matt_makeCuboidFCC_mix`, except that all created atoms are of the same atom-kind.

-----

**fmd_matt_makeCuboidFCC_mix()**

.. c:function:: void fmd_matt_makeCuboidFCC_mix(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, fmd_real_t *ratio, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param ratio: the ratio of the mixture
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    Creates a structure of atoms with cuboid outline by adding a single atom of random atom-kind to any point of a *finite* face-centered cubic (FCC) lattice. A conventional cell indexed by :math:`i`, :math:`j` and :math:`k`, where :math:`i=0,\dots,\mathrm{dimx}-1` and :math:`j=0,\dots,\mathrm{dimy}-1` and :math:`k=0,\dots,\mathrm{dimz}-1`, will have four atoms placed at

    .. math::

        x_1=\mathrm{x}+\left(i+\frac{1}{4}\right)\times\mathrm{lp},\quad y_1=\mathrm{y}+\left(j+\frac{1}{4}\right)\times\mathrm{lp},\quad z_1=\mathrm{z}+\left(k+\frac{1}{4}\right)\times\mathrm{lp},

    and

    .. math::

        x_2=\mathrm{x}+\left(i+\frac{1}{4}\right)\times\mathrm{lp},\quad y_2=\mathrm{y}+\left(j+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad z_2=\mathrm{z}+\left(k+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},

    and

    .. math::

        x_3=\mathrm{x}+\left(i+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad y_3=\mathrm{y}+\left(j+\frac{1}{4}\right)\times\mathrm{lp},\quad z_3=\mathrm{z}+\left(k+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},

    and

    .. math::

        x_4=\mathrm{x}+\left(i+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad y_4=\mathrm{y}+\left(j+\frac{1}{2}+\frac{1}{4}\right)\times\mathrm{lp},\quad z_4=\mathrm{z}+\left(k+\frac{1}{4}\right)\times\mathrm{lp}.

    A total of 4 :math:`\times` :c:var:`dimx` :math:`\times` :c:var:`dimy` :math:`\times` :c:var:`dimz` atoms are added to the simulation box. The probability that any single atom in the created structure is of p-th atom-kind is equal to

    .. math::

        \frac{\text{ratio[p]}}{{\displaystyle\sum_{\text{q}=0}^{N-1} \text{ratio[q]}}},

    where :math:`N` is the number of atom-kinds set by :c:func:`fmd_matt_setAtomKinds`. :c:var:`GroupID` must be a non-negative integer value. The atoms are given velocities that have a Maxwell-Boltzmann distribution corresponding to the temperature :c:var:`temp`. The created structure must be equilibrated with :c:func:`fmd_dync_equilibrate` to reach the desired temperature. Groups are explained in `General notes`_.

-----

**fmd_matt_makeCuboidSC()**

.. c:function:: void fmd_matt_makeCuboidSC(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, unsigned atomkind, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param atomkind: the index of the atom-kind in the array of atom-kinds
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    The same as :c:func:`fmd_matt_makeCuboidSC_mix`, except that all created atoms are of the same atom-kind.

-----

**fmd_matt_makeCuboidSC_mix()**

.. c:function:: void fmd_matt_makeCuboidSC_mix(fmd_t *md, fmd_real_t x, fmd_real_t y, fmd_real_t z, int dimx, int dimy, int dimz, fmd_real_t lp, fmd_real_t *ratio, int GroupID, fmd_real_t temp)

    :param md: an :c:type:`fmd_t`
    :param x: the starting position (x component)
    :param y: the starting position (y component)
    :param z: the starting position (z component)
    :param dimx: the dimension of the lattice in x direction
    :param dimy: the dimension of the lattice in y direction
    :param dimz: the dimension of the lattice in z direction
    :param lp: the lattice parameter
    :param ratio: the ratio of the mixture
    :param GroupID: the group-ID of the created atoms
    :param temp: the desired temperature

    Creates a structure of atoms with cuboid outline by adding a single atom of random atom-kind to any point of a *finite* simple cubic (SC) lattice. A conventional cell indexed by :math:`i`, :math:`j` and :math:`k`, where :math:`i=0,\dots,\mathrm{dimx}-1` and :math:`j=0,\dots,\mathrm{dimy}-1` and :math:`k=0,\dots,\mathrm{dimz}-1`, will have one atom placed at

    .. math::

        x_1=\mathrm{x}+\left(i+\frac{1}{4}\right)\times\mathrm{lp},\quad y_1=\mathrm{y}+\left(j+\frac{1}{4}\right)\times\mathrm{lp},\quad z_1=\mathrm{z}+\left(k+\frac{1}{4}\right)\times\mathrm{lp}.

    A total of :c:var:`dimx` :math:`\times` :c:var:`dimy` :math:`\times` :c:var:`dimz` atoms are added to the simulation box. The probability that any single atom in the created structure is of p-th atom-kind is equal to

    .. math::

        \frac{\text{ratio[p]}}{{\displaystyle\sum_{\text{q}=0}^{N-1} \text{ratio[q]}}},

    where :math:`N` is the number of atom-kinds set by :c:func:`fmd_matt_setAtomKinds`. :c:var:`GroupID` must be a non-negative integer value. The atoms are given velocities that have a Maxwell-Boltzmann distribution corresponding to the temperature :c:var:`temp`. The created structure must be equilibrated with :c:func:`fmd_dync_equilibrate` to reach the desired temperature. Groups are explained in `General notes`_.

-----

**fmd_matt_saveConfiguration()**

.. c:function:: void fmd_matt_saveConfiguration(fmd_t *md)

    :param md: an :c:type:`fmd_t`

    Saves the positions of all atoms to a configuration file on disk. File format and file naming depend on the mode of configuration saving, which can be changed with :c:func:`fmd_io_setSaveConfigMode`. The default mode is :c:enumerator:`FMD_SCM_XYZ_ATOMSNUM`. The path to the directory where the file is saved can be changed with :c:func:`fmd_io_setSaveDirectory`.

-----

**fmd_matt_setAtomKinds()**

.. c:function:: void fmd_matt_setAtomKinds(fmd_t *md, unsigned number, const fmd_string_t names[], const fmd_real_t masses[])

    :param md: an :c:type:`fmd_t`
    :param number: the number of atom-kinds
    :param names: an array of strings, where each element is the name of an atom-kind
    :param masses: the array of the masses of the atom-kinds

    Sets the number of atom-kinds, their names and their masses. :c:expr:`names[i]` and :c:expr:`masses[i]` are respectively the name (e.g. "Ar", "Cu") and mass of the :c:expr:`i`-th atom-kind (:math:`\mathrm{i}=0,\dots,\mathrm{number}-1`).

-----

**fmd_matt_translate()**

.. c:function:: void fmd_matt_translate(fmd_t *md, int GroupID, fmd_real_t dx, fmd_real_t dy, fmd_real_t dz)

    :param md: an :c:type:`fmd_t`
    :param GroupID: specifies the group on which the function acts
    :param dx: the x component of displacement vector
    :param dy: the y component of displacement vector
    :param dz: the z component of displacement vector

    Translates all atoms in group :c:var:`GroupID` by the given displacement vector. When periodic boundary conditions are not applied, if all or some of the atoms are translated to positions outside the boundaries of the simulation box, the departed atoms are removed from the simulation. Groups are explained in `General notes`_.

-----

**fmd_pot_apply()**

.. c:function:: void fmd_pot_apply(fmd_t *md, unsigned atomkind1, unsigned atomkind2, fmd_pot_t *pot)

    :param md: an :c:type:`fmd_t`
    :param atomkind1: the index of an atom-kind in the array of atom-kinds
    :param atomkind2: the index of an atom-kind in the array of atom-kinds
    :param pot: an :c:type:`fmd_pot_t`, the interatomic potential to be applied

    Applies :c:var:`pot` for the computation of the interactions among atoms of atom-kinds specified with the parameters :c:var:`atomkind1` and :c:var:`atomkind2`.

    Important note concerning EAM potentials: A DYNAMO *setfl* file contain chemical symbols (e.g. Cu, Al) of elements for which it was created. When such a potential file is loaded by calling :c:func:`fmd_pot_eam_alloy_load`, those chemical symbols are loaded along with other data into memory. On the other hand, in FMD every atom-kind has a name, set by :c:func:`fmd_matt_setAtomKinds`. In case :c:var:`pot` is an EAM potential, the call to :c:func:`fmd_pot_apply` is successful only if the names of the atom-kinds indexed by :c:var:`atomkind1` and :c:var:`atomkind2` are among the chemical symbols inside :c:var:`pot`.

-----

**fmd_pot_eam_alloy_load()**

.. c:function:: fmd_pot_t *fmd_pot_eam_alloy_load(fmd_t *md, fmd_string_t path)

    :param md: an :c:type:`fmd_t`
    :param path: the path to the file on disk
    :returns: a pointer to the loaded potential

    Loads an `EAM potential <https://en.wikipedia.org/wiki/Embedded_atom_model>`_ from a file with DYNAMO *setfl* format. One website that distributes such potential files for different materials is https://www.ctcms.nist.gov/potentials. Files with DYNAMO *setfl* format usually, if not always, have ``.eam.alloy`` extension on that website. Once a potential file is loaded into memory, it must be applied by using :c:func:`fmd_pot_apply`.

-----

**fmd_pot_eam_getCutoffRadius()**

.. c:function:: fmd_real_t fmd_pot_eam_getCutoffRadius(fmd_t *md, fmd_pot_t *pot)

    :param md: an :c:type:`fmd_t`
    :param pot: an :c:type:`fmd_pot_t`, the loaded EAM potential
    :returns: the cut-off radius of the EAM potential

-----

**fmd_pot_eam_getLatticeParameter()**

.. c:function:: fmd_real_t fmd_pot_eam_getLatticeParameter(fmd_t *md, fmd_pot_t *pot, fmd_string_t element)

    :param md: an :c:type:`fmd_t`
    :param pot: an :c:type:`fmd_pot_t`, the loaded EAM potential
    :param element: the chemical symbol of the element
    :returns: the lattice parameter for the specified element

    If an element with chemical symbol specified with :c:var:`element` exists in the EAM potential :c:var:`pot`, this function returns its lattice parameter.

-----

**fmd_pot_lj_apply()**

.. c:function:: fmd_pot_t *fmd_pot_lj_apply(fmd_t *md, unsigned atomkind1, unsigned atomkind2, fmd_real_t sigma, fmd_real_t epsilon, fmd_real_t cutoff)

    :param md: an :c:type:`fmd_t`
    :param atomkind1: the index of an atom-kind in the array of atom-kinds
    :param atomkind2: the index of an atom-kind in the array of atom-kinds
    :param sigma: the parameter :math:`\sigma` of the Lennard-Jones potential
    :param epsilon: the parameter :math:`\epsilon` of the Lennard-Jones potential
    :param cutoff: the cut-off radius of the potential function
    :returns: a pointer to the created Lennard-Jones potential

    Creates a Lennard-Jones potential with the parameters :c:var:`sigma`, :c:var:`epsilon` and :c:var:`cutoff` and applies it for the computation of the interactions among atoms of atom-kinds specified with the parameters :c:var:`atomkind1` and :c:var:`atomkind2`. The mathematical relation for Lennard-Jones potential is

    .. math::

        V_\text{LJ}(r) = 4 \epsilon \left[ \left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^{6} \right],

    in which :math:`r` is the distance between two interacting atoms.

-----

**fmd_pot_morse_apply()**

.. c:function:: fmd_pot_t *fmd_pot_morse_apply(fmd_t *md, unsigned atomkind1, unsigned atomkind2, fmd_real_t D0, fmd_real_t alpha, fmd_real_t r0, fmd_real_t cutoff)

    :param md: an :c:type:`fmd_t`
    :param atomkind1: the index of an atom-kind in the array of atom-kinds
    :param atomkind2: the index of an atom-kind in the array of atom-kinds
    :param D0: the parameter :math:`D_0` of the Morse potential
    :param alpha: the parameter :math:`\alpha` of the Morse potential
    :param r0: the parameter :math:`r_0` of the Morse potential
    :param cutoff: the cut-off radius of the potential function
    :returns: a pointer to the created Morse potential

    Creates a Morse potential with the parameters :c:var:`D0`, :c:var:`alpha`, :c:var:`r0` and :c:var:`cutoff` and applies it for the computation of the interactions among atoms of atom-kinds specified with the parameters :c:var:`atomkind1` and :c:var:`atomkind2`. The mathematical relation for Morse potential is

    .. math::

        V_\text{Morse}(r) = D_0 \left[ \exp\left(-2\alpha (r-r_0)\right) - 2\exp\left(-\alpha(r-r_0)\right)\right],

    in which :math:`r` is the distance between two interacting atoms.

-----

**fmd_proc_getWallTime()**

.. c:function:: fmd_real_t fmd_proc_getWallTime(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: the wall time in seconds elapsed since :c:var:`md` was created and initialized by :c:func:`fmd_create`

-----

**fmd_proc_hasSubdomain()**

.. c:function:: bool fmd_proc_hasSubdomain(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: ``true``, if the current process is associated with a subdomain; ``false``, otherwise.

    This function is used to recognize if the current MPI process is associated with a subdomain of the simulation box. If called before :c:func:`fmd_box_setSubdomains`, the returned value is always ``false``. When the number of subdomains set by :c:func:`fmd_box_setSubdomains` is smaller than the number of launched MPI processes, :c:func:`fmd_box_setSubdomains` returns ``false`` on any extra processes.

-----

**fmd_proc_isRoot()**

.. c:function:: bool fmd_proc_isRoot(fmd_t *md)

    :param md: an :c:type:`fmd_t`
    :returns: ``true``, if called on the root process; ``false``, otherwise.

    This function is used to recognize if the current MPI process is the root process. Exactly one process is chosen to be the root by FMD.

-----

**fmd_proc_setNumThreads()**

.. c:function:: void fmd_proc_setNumThreads(fmd_t *md, int num)

    :param md: an :c:type:`fmd_t`
    :param num: the desired number of threads

    FMD can utilize OpenMP for parallel computation on systems with shared memory. This ability can be used instead of MPI-based parallel computation or in combination with it. By default, FMD requests one single thread any time it uses OpenMP for parallel computation. This means that, by default, OpenMP has no effect in practice. However, the requested number of OpenMP threads for the current process and the simulation instance specified by the parameter :c:var:`md` can be changed using this function. There is no other way to alter the requested number of threads. For example, calling the OpenMP function ``omp_set_num_threads()`` in a program linked to FMD has no effect on the number of threads that FMD requests.

    .. note::
      If you set the requested number of threads to a value larger than 1, make sure that when running your program with *mpirun* it does not bind all threads to one single CPU core.


-----

**fmd_setEventHandler()**

.. c:function:: void fmd_setEventHandler(fmd_t *md, void *usp, fmd_EventHandler_t func)

    :param md: an :c:type:`fmd_t`
    :param usp: an object passed to event-handler whenever any event occurs
    :param func: the callback function to be used as event-handler

    Sets an event handler for the simulation associated with :c:var:`md`. See also :c:type:`fmd_EventHandler_t`.

-----

**fmd_timer_makeSimple()**

.. c:function:: fmd_handle_t fmd_timer_makeSimple(fmd_t *md, fmd_real_t start, fmd_real_t interval, fmd_real_t stop)

    :param md: an :c:type:`fmd_t`
    :param start: the simulation time when the timer starts to tick
    :param interval: the time interval between two subsequent timer ticks
    :param stop: the simulation time when the timer stops ticking
    :returns: the handle to the timer

    Makes a *simple* timer and returns the handle to it. In a *simple* timer, the time interval between subsequent ticks is constant. To have a timer that never stops ticking, choose :c:var:`stop` to be smaller than :c:var:`start`.

-----

**fmd_ttm_setCellActivationFraction()**

.. c:function:: void fmd_ttm_setCellActivationFraction(fmd_t *md, fmd_handle_t turi, fmd_real_t value)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param value: the value of cell-activation fraction

    Sets the cell-activation fraction for the specified TTM turi. Its value is 0.1 by default. See :c:func:`fmd_turi_add` for more information.

-----

**fmd_ttm_setCouplingFactor()**

.. c:function:: void fmd_ttm_setCouplingFactor(fmd_t *md, fmd_handle_t turi, g)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param g: the coupling factor

    Sets the coupling factor for the specified TTM turi. The parameter :c:var:`g` is a struct. Its type must match the category of the turi according to the following table.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - turi category
         - data type of :c:var:`g`
       * - :c:enumerator:`FMD_TURI_TTM_TYPE1`
         - :c:type:`fmd_real_t` or :c:type:`fmd_ttm_coupling_factor_constant_t`

    See :c:func:`fmd_turi_add` for more information.

-----

**fmd_ttm_setElectronTemperature()**

.. c:function:: void fmd_ttm_setElectronTemperature(fmd_t *md, fmd_handle_t turi, fmd_real_t Te)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param Te: the initial electron temperature

    Sets the initial electron temperature of the specified TTM turi.

-----

**md_ttm_setHeatCapacity()**

.. c:function:: void fmd_ttm_setHeatCapacity(fmd_t *md, fmd_handle_t turi, c)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param c: the electron heat capacity

    Sets the electron heat capacity for the specified TTM turi. The parameter :c:var:`c` is a struct. Its type must match the category of the turi according to the following table.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - turi category
         - data type of :c:var:`c`
       * - :c:enumerator:`FMD_TURI_TTM_TYPE1`
         - :c:type:`fmd_ttm_heat_capacity_linear_t`

    See :c:func:`fmd_turi_add` for more information.

-----

**fmd_ttm_setHeatConductivity()**

.. c:function:: void fmd_ttm_setHeatConductivity(fmd_t *md, fmd_handle_t turi, k)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param k: the electron heat conductivity

    Sets the electron heat conductivity for the specified TTM turi. The parameter :c:var:`k` is a struct. Its type must match the category of the turi according to the following table.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - turi category
         - data type of :c:var:`k`
       * - :c:enumerator:`FMD_TURI_TTM_TYPE1`
         - :c:type:`fmd_real_t` or :c:type:`fmd_ttm_heat_conductivity_constant_t`

    See :c:func:`fmd_turi_add` for more information.

-----

**fmd_ttm_setLaserSource()**

.. c:function:: void fmd_ttm_setLaserSource(fmd_t *md, fmd_handle_t turi, laser)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param laser: a struct defining the laser

    Sets the laser source term of the TTM equation. The parameter :c:var:`laser` is a struct. Its type must match the category of the turi according to the following table.

    .. list-table:: 
       :widths: 45 55
       :header-rows: 1

       * - turi category
         - data type of :c:var:`laser`
       * - :c:enumerator:`FMD_TURI_TTM_TYPE1`
         - :c:type:`fmd_ttm_laser_gaussian_t`

    See :c:func:`fmd_turi_add` for more information.

-----

**fmd_ttm_setTimestepRatio()**

.. c:function:: void fmd_ttm_setTimestepRatio(fmd_t *md, fmd_handle_t turi, int ratio)

    :param md: an :c:type:`fmd_t`
    :param turi: the handle to the TTM turi
    :param ratio: the ratio of MD time step to FD time step

    Sets the ratio of the time step used for MD time integration to the time step used for FD time integration. See also :c:func:`fmd_turi_add`.

-----

**fmd_turi_add()**

.. c:function:: fmd_handle_t fmd_turi_add(fmd_t *md, fmd_turi_t cat, int dimx, int dimy, int dimz, fmd_real_t starttime, fmd_real_t stoptime)

    :param md: an :c:type:`fmd_t`
    :param cat: the category of the turi
    :param dimx: the dimension of the turi in x direction
    :param dimy: the dimension of the turi in y direction
    :param dimz: the dimension of the turi in z direction
    :param starttime: the simulation time when the turi is activated
    :param stoptime: the simulation time when the turi is deactivated
    :return: the handle to the turi

    Adds a new turi to the simulation. Turies are introduced in `General notes`_. The parameter :c:var:`cat` specifies the category of the turi. If it is equal to :c:enumerator:`FMD_TURI_CUSTOM`, no field is added and the library user can add fields later with :c:func:`fmd_field_add`. If it is equal to :c:enumerator:`FMD_TURI_TTM_TYPE1`, the library adds to the turi the fields of categories :c:enumerator:`FMD_FIELD_NUMBER`, :c:enumerator:`FMD_FIELD_VCM`, :c:enumerator:`FMD_FIELD_TEMPERATURE`, :c:enumerator:`FMD_FIELD_TTM_TE` and :c:enumerator:`FMD_FIELD_TTM_XI`. See :c:type:`fmd_field_t` for information about these field categories. The handle to any added field, including the automatically added fields, can be found with :c:func:`fmd_field_find`. When a turi of :c:enumerator:`FMD_TURI_TTM_TYPE1` category exists in a simulation, :c:func:`fmd_dync_integrate` integrates the Newton's equations of motion coupled with the following generalized heat equation describing the evolution of electron temperature:

    .. math::

        C_\mathrm{e}\frac{\partial T_\mathrm{e}}{\partial t}=\frac{\partial}{\partial z}\left(K_\mathrm{e}\frac{\partial T_\mathrm{e}}{\partial z}\right)-G\cdot(T_\mathrm{e}-T_\mathrm{l})+S(z,t),

    where :math:`C_\mathrm{e}`, :math:`T_\mathrm{e}` and :math:`K_\mathrm{e}` are the heat capacity, temperature and heat conductivity of the electron subsystem at time :math:`t` and position :math:`z`, respectively. The electron-phonon coupling factor, :math:`G`, determines how fast thermal energy is transferred between the electron and phonon subsystems, and :math:`T_\mathrm{l}` is the lattice temperature. The laser source term :math:`S(z,t)` is the laser energy absorbed by the electron subsystem per time unit per volume unit at a depth of :math:`z` from the surface of the target. The heat equation above is solved numerically with finite difference (FD) method. The quantities :math:`C_\mathrm{e}`, :math:`K_\mathrm{e}`, :math:`G` and :math:`S(z,t)` must be set by :c:func:`fmd_ttm_setHeatCapacity`, :c:func:`fmd_ttm_setHeatConductivity`, :c:func:`fmd_ttm_setCouplingFactor` and :c:func:`fmd_ttm_setLaserSource`, respectively. The initial electron temperature is set by :c:func:`fmd_ttm_setElectronTemperature`. Usually, the time step for molecular dynamics (MD) time integration is many tens of times larger than the time step used for FD time integration. The ratio is an integer, set by the function :c:func:`fmd_ttm_setTimestepRatio`. When the number of atoms in a turi-cell becomes smaller than a certain fraction of the initial average number of atoms per non-empty turi-cell, that turi-cell is deactivated, which basically means the coupling between MD and FD is neglected for atoms inside it. The fraction by default is one-tenth (0.1) and can be changed by :c:func:`fmd_ttm_setCellActivationFraction`. More details about this so-called MD-TTM scheme can be found in [`D.S. Ivanov and L. V. Zhigilei, Phys. Rev. B 68, 064114 (2003) <https://doi.org/10.1103/PhysRevB.68.064114>`_].

    .. warning::

        Do not add more than one TTM turi to a simulation.

    Each of the parameters :c:var:`dimx`, :c:var:`dimy` and :c:var:`dimz` can be equal to or larger than 1. When the simulation time reaches :c:var:`starttime`, the turi is activated, i.e. the fields on it start to get updated. And when the simulation time passes :c:var:`stoptime`, the fields do not get updated any longer. If :c:var:`stoptime` is less than :c:var:`starttime`, the turi is never deactivated.`

-----

**fmd_version_getMajor()**

.. c:function:: int fmd_version_getMajor()

    The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This function returns X. See `General notes`_ for more information about the versioning scheme.

-----

**fmd_version_getMinor()**

.. c:function:: int fmd_version_getMinor()

    The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This function returns Y. See `General notes`_ for more information about the versioning scheme.

-----

**fmd_version_getRevision()**

.. c:function:: int fmd_version_getRevision()

    The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This function returns Z. See `General notes`_ for more information about the versioning scheme.

-----

**fmd_version_getString()**

.. c:function:: int fmd_version_getString()

    The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This function returns X.Y.Z as a string. See `General notes`_ for more information about the versioning scheme.

-----

**fmd_version_getType()**

.. c:function:: int fmd_version_getType()

    The version format is X.Y.Z.c, where X, Y, Z are non-negative integers and c is a character. This function returns c, which can be either 'r' or 'd', standing for *release* and *development*, respectively. See `General notes`_ for more information about the versioning scheme.