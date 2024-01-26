#include <fmd.h>

fmd_handle_t timer1, timer2;

void handleEvents(fmd_t *md, fmd_event_t event, void *usp, fmd_params_t *params)
{
    if (event == FMD_EVENT_TIMER_TICK)
    {
        fmd_handle_t timer = ((fmd_event_params_timer_tick_t *)params)->timer;

        if (timer == timer1)
            fmd_io_printf(md, "%f\t%f\t%e\n", fmd_dync_getTime(md),
                                              fmd_matt_getTemperature(md),
                                              fmd_matt_getTotalEnergy(md));
        else if (timer == timer2)
            fmd_matt_saveConfiguration(md);
    }
}

void main()
{
    fmd_t *md;

    md = fmd_create();

    fmd_setEventHandler(md, &md, handleEvents);

    timer1 = fmd_timer_makeSimple(md, 0.0, 0.05, -1.0);
    timer2 = fmd_timer_makeSimple(md, 0.0, 0.04, -1.0);

    fmd_real_t LP = 5.26;
    fmd_box_setSize(md, 10*LP, 10*LP, 10*LP);

    fmd_box_setPBC(md, true, true, true);

    fmd_box_setSubdomains(md, 1, 2, 1);

    fmd_string_t name[1] = {"Ar"};
    fmd_real_t mass[1] = {39.948};
    fmd_matt_setAtomKinds(md, 1, name, mass);

    fmd_real_t sigma = 3.4, epsilon = 0.0104;
    fmd_real_t cutoff = 2.5 * sigma;
    fmd_pot_lj_apply(md, 0, 0, sigma, epsilon, cutoff);

    fmd_matt_makeCuboidFCC(md, 0.0, 0.0, 0.0, 10, 10, 10, LP, 0, 0, 100.0);

    fmd_dync_equilibrate(md, 0, 1.0, 2e-3, 2e-2, 100.0);

    fmd_io_saveState(md, "state0.stt");

    fmd_io_printf(md, "The run took about %.3f seconds to finish.\n", fmd_proc_getWallTime(md));

    fmd_free(md);
}
