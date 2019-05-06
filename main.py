import os
import time

import matplotlib.pyplot as plt
import numpy as np

from classes.aircraft import Aircraft
from tools.read import import_aircraft_data


class Main:

    path = os.path.join(os.getcwd(), 'input', 'aircraft_config.xlsx')

    def __init__(self):
        self.fig, self.ax = plt.subplots()

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

    def show_geometry(self):
        from parapy.gui import display
        display(self.aircraft)

    def minimize_tail_area(self, pos_min=0.3, pos_max=0.5, pos_step=0.1,
                           plot_graph=True):
        """ Minimise the tail area of this aircraft, by shifting the main
        wing position from :any:`pos_min` to :any:`pos_max` with increments
        of :any:`pos_step`.

        :param pos_min: The minimum (most forward) position of the main wing
            that is checked.
        :type pos_step: float
        :param pos_max: The maximum (most rearward) position of the main wing
            that is checked.
        :type pos_max: float
        :param pos_step: The amount by which the wing position is increased
            between :any:`pos_min` and :any:`pos_max`
        :type pos_step: float

        :param plot_graph: Show the graph, showing the variation of
            horizontal tail area with main wing position?
        :type plot_graph: bool
        :return: the minimum attainable tail area.
        :rtype: float
        """
        positions = np.arange(pos_min, pos_max, pos_step)
        self.tail_areas = {}
        t0 = time.time()
        for position in positions:
            self.main_wing_data.pop('main_wing_long_pos')
            self.main_wing_data['main_wing_long_pos'] = position

            all_data = {}
            for dictionary in [self.aircraft_data, self.main_wing_data,
                               self.horizontal_tail_data,
                               self.vertical_tail_data, self.fuselage_data]:
                all_data.update(dictionary)

            aircraft = Aircraft(**all_data)
            self.tail_areas[position] = {
                'aircraft': aircraft,
                'tail_area': aircraft.scissor_plot.tail_area
            }
        min_dict = min(self.tail_areas.items(),
                       key=lambda i: i[1]['tail_area'])
        self.aircraft = min_dict[1]['aircraft']
        print 'Minimum tail area of {:.2f} found for a longitudinal main ' \
              'wing position of {:.2f} in {:.1f} s.'.format(
               min_dict[1]['tail_area'], min_dict[0], time.time() - t0
               )

        plt.plot(positions,
                 [self.tail_areas[pos]['tail_area'] for pos in positions])
        plt.xlim([0, 1])
        plt.xlabel('Long. wing pos. as a fraction of fuselage length [-]')
        plt.ylabel('Horizontal tail area [m2]')
        plt.title('Tail area as a function of main wing location.')
        if plot_graph:
            plt.show()

        return min_dict[1]['tail_area']

    def write_geometry_step(self):
        # TODO: write step file for geometry output.
        pass


if __name__ == '__main__':
    main = Main()
    main.minimize_tail_area()

