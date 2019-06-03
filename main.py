import os
import time

import matplotlib.pyplot as plt
import numpy as np

from classes.aircraft import Aircraft
from tools.read import import_aircraft_data


class Main:

    path = os.path.join(os.getcwd(), 'input', 'aircraft_config.xlsx')

    def __init__(self, name):
        """ The constructor function of the main class. Upon initialisation,
        an aircraft is instantiated as well, by reading the input data as
        provided in the `aircraft_config.xlsx` excel file in the input folder.

        :param name: the name that is given to this analysis session. Only
            used for saving files with this name.
        :type name: str
        """
        self.name = name

        self.aircraft_data = import_aircraft_data('aircraft',
                                                  self.path)
        self.main_wing_data = import_aircraft_data('main_wing',
                                                   self.path)
        self.horizontal_tail_data = import_aircraft_data('horizontal_tail',
                                                         self.path)
        self.vertical_tail_data = import_aircraft_data('vertical_tail',
                                                       self.path)
        self.fuselage_data = import_aircraft_data('fuselage',
                                                  self.path)

        self.all_data = {}

        for dictionary in [self.aircraft_data, self.main_wing_data,
                           self.horizontal_tail_data, self.vertical_tail_data,
                           self.fuselage_data]:
            self.all_data.update(dictionary)

        self.aircraft = Aircraft(**self.all_data)

        self.tail_areas = {
            self.main_wing_data['main_wing_long_pos']:
                {'tail_area': self.aircraft.scissor_plot.tail_area,
                 'aircraft': self.aircraft}
        }

        self.time_histories = {}

    def show_geometry(self):
        """ Display the geometry in the ParaPy GUI.

        :rtype: None
        """
        from parapy.gui import display
        display(self.aircraft)

    def minimize_tail_area(self, pos_min=0.3, pos_max=0.51, pos_step=0.05,
                           show_plot=True, save_plot=True):
        """ Minimise the tail area of this aircraft, by shifting the main
        wing position from pos_min to pos_max with increments
        of pos_step.

        :param pos_min: The minimum (most forward) position of the main wing
            that is checked.
        :type pos_step: float
        :param pos_max: The maximum (most rearward) position of the main wing
            that is checked.
        :type pos_max: float
        :param pos_step: The amount by which the wing position is increased
            between pos_min and pos_max
        :type pos_step: float

        :param show_plot: Show the graph, showing the variation of
            horizontal tail area with main wing position?
        :type show_plot: bool

        :param save_plot: should this plot be saved?
        :type save_plot: bool

        :return: the minimum attainable tail area.
        :rtype: float
        """
        positions = np.arange(pos_min, pos_max, pos_step)
        self.tail_areas = {}
        t0 = time.time()

        for position in positions:
            print 'Position: {} \n' \
                  '_______________________________ \n' \
                  '_______________________________ \n' \
                  '_______________________________'.format(position)
            self.aircraft.main_wing_long_pos = position
            # self.converge_tail_area()
            self.tail_areas[position] = {
                'aircraft': self.aircraft,
                # 'tail_area':
                #     self.aircraft.horizontal_tail_port.reference_area * 2.
                'tail_area': self.aircraft.scissor_plot.tail_area
            }

        min_dict = min(self.tail_areas.items(),
                       key=lambda i: i[1]['tail_area'])
        self.aircraft = min_dict[1]['aircraft']
        print 'Minimum tail area of {:.2f} m2 found for a longitudinal main ' \
              'wing position of {:.2f} in {:.1f} s.'.format(
               min_dict[1]['tail_area'], min_dict[0], time.time() - t0
               )

        plt.plot(positions,
                 [self.tail_areas[pos]['tail_area'] for pos in positions])
        plt.xlim([0, 1])
        plt.grid(which='both')
        plt.xlabel('Long. wing pos. as a fraction of fuselage length [-]')
        plt.ylabel('Horizontal tail area [m2]')
        plt.title('Tail area as a function of main wing location.')

        if save_plot:
            plt.savefig(os.path.join('output',
                                     '{}_tail_areas.pdf'.format(self.name)))
        if show_plot:
            plt.show(block=False)

        return min_dict[1]['tail_area']

    def converge_tail_area(self, convergence_error=1e-4):
        """ Make sure that for an aircraft configuration, the tail area as
        suggested by the scissor plot does not deviate more than the
        convergence_error from the actual tail area.

        :param convergence_error: the amount by which the scaling factor is
            allowed to differ from 1.
        :type convergence_error: float

        :rtype: None
        """
        scale_factor = np.inf

        while abs(scale_factor - 1.) > convergence_error:

            suggested_area = self.aircraft.scissor_plot.tail_area
            current_area = \
                self.aircraft.horizontal_tail_starboard.reference_area * 2.

            scale_factor = (suggested_area / current_area) ** 0.5

            self.aircraft.ht_chords = [scale_factor * chord
                                       for chord in self.aircraft.ht_chords]
            self.aircraft.ht_semi_span *= scale_factor

            print 'Convergence error: {:.5f} \n' \
                  'Tail area: {:.2f} \n' \
                  '_______________________________'.format(scale_factor - 1.,
                                                           current_area)

    def burn_symmetrically(self, tank_type, tank_no, delta_t):
        """ Burn fuel in the fuel tanks symmetrically. That is, burning from
        the main tank, with index 0 will cause fuel to be burnt from both
        starboard and port sides, whereas burning from the vertical tank
        causes the vertical tank to be used for engines hanging on either side.

        :param tank_type: tank type indicator (main, vertical or trim tank).
        :type tank_type: str

        :param tank_no: tank number (0 for inboard, -1 for outboard).
        :type tank_no: int

        :param delta_t: time interval during which the fuel is burnt
        :type delta_t: float

        :raises NameError: if the tank_type is not recognised.

        :rtype: float
        """
        if tank_type == 'main':
            tank1 = self.aircraft.main_wing_starboard.fuel_tanks[tank_no]
            tank2 = self.aircraft.main_wing_port.fuel_tanks[tank_no]
            tanks = [tank1, tank2]
        elif tank_type == 'trim':
            tank1 = self.aircraft.horizontal_tail_starboard.fuel_tanks[tank_no]
            tank2 = self.aircraft.horizontal_tail_port.fuel_tanks[tank_no]
            tanks = [tank1, tank2]
        elif tank_type == 'vert':
            tank1 = self.aircraft.vertical_tail.fuel_tanks[tank_no]
            tanks = [tank1]
        else:
            msg = '{} is not recognised as a valid input for this function.'
            raise NameError(msg.format(tank_type))

        # If the burn function returns a different time interval, use that.
        for tank in tanks:
            t = tank.fuel.burn(time_step=delta_t)

        t = delta_t if t is None else t

        return t

    def optimize_fuel_usage(self, delta_t, end_condition='fuel_empty',
                            end_time=np.inf, show_plot=True, save_plot=True):
        """ The function that optimizes the fuel tank usage to minimize
        (induced) trim drag. The function works in the following way.

        #. The aircraft in its initial (full fuel) condition is trimmed at the
            CL for which lift equals weight, by setting the elevator such that
            the pitching moment is zero.
        #. Fuel is burnt *virtually* from each of the tanks (symmetrically)
            and the corresponding elevator deflection for trim, and the
            subsequent induced drag are calculated.
        #. The option yielding the least induced drag is chosen. That is,
            the tank, for which the lowest induced drag is
            calculated is tapped.
        #. Fuel is burnt from this optimum tank. Repeat to first step,
            but now for a non-initial condition and corresponding weight.

        :param delta_t: the courseness of the time discretisation (the time
            step used for the analysis).
        :type delta_t: float

        :param end_condition: word indicating whether the end condition
            should be 'empty_fuel' or a 'time' limit. If 'time' is chosen,
            a corresponding end_time should be set as well.
        :type end_condition: str

        :param end_time: if the end condition is set as a certain end time,
            the corresponding end_time should be set here, in seconds.
        :type end_time: float

        :param show_plot: should the plot be shown?
        :type show_plot: bool

        :param save_plot: should the plot be saved to the output folder?
            Note that the file receives the name according to the name that is
            passed upon instantiating this Main object.
        :type save_plot: bool

        :rtype: None
        """
        def calculate_values():
            """ Wrapper function for calculation operations.

            :rtype: tuple[float]
            """
            CL = self.aircraft.CL
            delta_e = self.aircraft.trim()
            CDi = self.aircraft.get_CD(CL, delta_e)
            alpha = self.aircraft.get_alpha(CL, delta_e)
            Cm = self.aircraft.get_Cm(CL, delta_e)
            cog = self.aircraft.cog.x
            return CL, delta_e, CDi, alpha, Cm, cog

        def append_values():
            """ Wrapper function for the append operations.

            :rtype: None
            """
            self.time_histories['CL'].append(CL)
            self.time_histories['delta_e'].append(delta_e)
            self.time_histories['CDi'].append(CDi)
            self.time_histories['alpha'].append(alpha)
            self.time_histories['Cm'].append(Cm)
            self.time_histories['cog'].append(cog)

        t = 0

        # Clear and set up the time history lists.
        self.time_histories = {'t': [0.], 'CL': [], 'delta_e': [], 'CDi': [],
                               'alpha': [], 'Cm': [], 'tank': [], 'cog': []}

        # Group the different sorts of tanks.
        tanks = {
            'main': range(len(self.aircraft.main_wing_port.fuel_tanks)),
            'trim': range(len(
                self.aircraft.horizontal_tail_starboard.fuel_tanks)),
            'vert': range(len(self.aircraft.vertical_tail.fuel_tanks))
        }
        main_tanks = self.aircraft.main_wing_starboard.fuel_tanks + \
            self.aircraft.main_wing_port.fuel_tanks
        trim_tanks = self.aircraft.horizontal_tail_port.fuel_tanks + \
            self.aircraft.horizontal_tail_starboard.fuel_tanks
        vertical_tanks = self.aircraft.vertical_tail.fuel_tanks
        all_tanks = main_tanks + trim_tanks + vertical_tanks

        n = 0

        while (not all(tank.is_empty for tank in all_tanks) and
               end_condition == 'fuel_empty') or \
                (t < end_time and end_condition == 'time'):
            n += 1
            print '________________ n_iter = {} _________________'.format(n)
            print 't = {}'.format(t)
            tank_types = [
                'main' * (not all(tank.is_empty for tank in main_tanks)),
                'trim' * (not all(tank.is_empty for tank in trim_tanks)),
                'vert' * (not all(tank.is_empty for tank in vertical_tanks))
            ]

            [tank_types.remove('') for _ in range(tank_types.count(''))]

            CL, delta_e, CDi, alpha, Cm, cog = calculate_values()
            append_values()

            print 'CL: {},\ndelta_e: {},\nCDi: {},\nalpha: {},\nCm: {}'.format(
                CL, delta_e, CDi, alpha, Cm
            )

            # Determine tapping from which tank gives the lowest drag
            min_drag = np.inf
            for tank_type in tank_types:
                for tank_no in tanks[tank_type]:

                    # Burn fuel from each tank and calculate required
                    # elevator deflection and resulting induced drag.
                    time = self.burn_symmetrically(tank_type, tank_no, delta_t)
                    delta_e = self.aircraft.trim()
                    drag = self.aircraft.get_CD(self.aircraft.CL, delta_e)

                    # If burning from this tank results in the least amount
                    # of drag, store its value
                    if drag < min_drag:
                        min_drag = drag
                        min_tank_no = tank_no
                        min_tank_type = tank_type

                    # 'Refuel' the tank, in case burning fuel from this tank
                    # does not deliver the minimum induced drag.
                    self.burn_symmetrically(tank_type, tank_no, -time)

            # Store the tank from which the fuel is eventually tapped as the
            # tank that is used in this time interval.
            self.time_histories['tank'].append('{}_{}'.format(min_tank_type,
                                                              min_tank_no))

            print 'next best tank: {} {}'.format(min_tank_type, min_tank_no)

            t += self.burn_symmetrically(min_tank_type, min_tank_no, delta_t)

            self.time_histories['t'].append(t)

        calculate_values()
        append_values()
        print t
        if show_plot:
            self.plot_time_histories(delta_t, save_plot=save_plot)

    def plot_time_histories(self, delta_t, save_plot=True):
        """ A function used to plot the most important time histories of the
        aircraft in terms of fuel usage and trim performance on one sheet.

        :param save_plot: parameter indicating whether the plot should be
            saved.
        :type save_plot: bool

        :param delta_t: the time step that has been used in doing this
        analysis.
        :type delta_t: float

        :rtype: None
        """
        time = self.time_histories['t']

        fig, axes = plt.subplots(7, 1, True)
        fig.set_size_inches(8.3, 11.7)
        plt.xlabel('time [s]')
        fig.suptitle('Aircraft top-level characteristics')

        axes[0].plot(time, self.time_histories['CL'])
        axes[0].set_title('$C_L vs. time$')
        axes[0].set_ylabel('$C_L [-]$')
        axes[0].grid(which='both')

        axes[1].plot(time, self.time_histories['delta_e'])
        axes[1].set_title(r'$\delta_e vs. time$')
        axes[1].set_ylabel(r'$\delta_e [^\circ]$')
        axes[1].grid(which='both')

        axes[2].plot(time, self.time_histories['CDi'])
        axes[2].set_title('$C_{D_{i}} vs. time$')
        axes[2].set_ylabel('$C_{D_{i}} [-]$')
        axes[2].grid(which='both')

        axes[3].plot(time, self.time_histories[r'alpha'])
        axes[3].set_title(r'$\alpha vs. time$')
        axes[3].set_ylabel(r'$\alpha [^\circ]$')
        axes[3].grid(which='both')

        axes[4].plot(time, self.time_histories['Cm'])
        axes[4].set_title('$C_m vs. time$')
        axes[4].set_ylabel('$C_m [-]$')
        axes[4].grid(which='both')

        labels = sorted(set(self.time_histories['tank']),
                        key=lambda s: self.format_func(s))
        y_ticks = sorted({self.format_func(s)
                          for s in self.time_histories['tank']})

        for t1, t2, tank in zip(time[:-1], time[1:],
                                self.time_histories['tank']):
            axes[5].plot([t1, t2],
                         [self.format_func(tank), self.format_func(tank)],
                         color='C0')
        axes[5].set_title('Tank used vs. time')
        axes[5].set_ylabel('Tank used [-]')
        axes[5].set_yticks(y_ticks)
        axes[5].set_yticklabels(labels)
        axes[5].grid(which='both')

        axes[6].plot(time, self.time_histories['cog'])
        axes[6].set_title('$x_{cog} vs. time$')
        axes[6].set_ylabel('$x_{cog} [m]$')
        axes[6].grid(which='both')

        if save_plot:
            fig.savefig(os.path.join('output',
                                     '{}_delta_t_{}_performance.pdf'
                                     .format(self.name, delta_t)))
        plt.show(block=False)

    def format_func(self, tank_designation):
        """ A function that translates a tank_designation, such as
        'main_1' (a tank in the main wing, with index 1), to a value,
        such that the tank usage history over time can be plotted.

        :param tank_designation: a tank designation, such as 'main_1' or
            'trim_0', used to designate the second main tank or the first trim
            tank, respectively.
        :type tank_designation: str

        :rtype: int
        """
        type_distances = [
            len(self.aircraft.main_wing_starboard.fuel_tanks),
            len(self.aircraft.horizontal_tail_starboard.fuel_tanks),
            len(self.aircraft.vertical_tail.fuel_tanks)
        ]
        tank_type = tank_designation.split('_')[0]
        tank_no = int(tank_designation.split('_')[-1])

        type_value = ['main', 'trim', 'vert'].index(tank_type)

        return sum(type_distances[:type_value]) + tank_no


if __name__ == '__main__':
    t0 = time.time()
    main = Main('conv-mid-wing')
    main.minimize_tail_area(.4, .5, .1, show_plot=True)
    main.converge_tail_area()
    main.optimize_fuel_usage(50., show_plot=True)
    # main.plot_time_histories()
    main.show_geometry()
    print 'Elapsed time: {}'.format(time.time() - t0)
