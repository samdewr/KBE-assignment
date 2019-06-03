from os.path import dirname, join

import pandas as pd
import numpy as np
from parapy.core import *
from parapy.core.globs import Undefined
from parapy.geom import *


class Fuel(SubtractedSolid):

        # Class constants
    CONSTANTS = pd.read_excel(
        join(dirname(dirname(dirname(dirname(__file__)))),
             'input', 'aircraft_config.xlsx'),
        sheet_name='fuel', index_col=0
    )

    DENSITY = CONSTANTS.loc['density']['Value']
    DENSITY_UNITS = CONSTANTS.loc['density']['Units']

    # Inputs
    tank_solid = Input()
    fill_rate = Input(1., validator=val.Range(0, 1))

    # Optional inputs
    color = Input('red')
    transparency = Input(0.75)
    # fuel_burn_plane_increment_distance = Input(0.01)
    on_invalid = Input('warn')
    convergence_tol = 1e-5

    __initargs__ = ['tank_solid']

    @Input
    def initial_volume(self):
        """ Sets the initial volume of the fuel to the maximum volume
        fittable in the fuel tank.

        :rtype: float
        """
        return abs(self.tank_solid.volume) * self.fill_rate

    @Input
    def mass(self):
        """ Calculates the fuel mass initially by multiplying the
        :any:`initial_volume` and the fuel :any:`DENSITY`. However,
        by :any:`burn` ing fuel, the mass is changed. This is an in-place
        operation, such that the mass is only equal to the
        :any:`initial_volume` times the fuel :any:`DENSITY` before burning
        fuel.

        :rtype: float
        """
        mass = self.initial_volume * self.DENSITY
        return mass if mass > 0. else 0.

    @Attribute
    def initial_mass(self):
        """ Sets the initial mass of the fuel according to the initial
        volume specified in :any:`initial_volume`.

        :rtype: float
        """
        return abs(self.tank_solid.volume * self.DENSITY) * self.fill_rate

    @Attribute
    def volume(self):
        """ Calculates the current volume of the fuel as a function of the
        remaining fuel :any:`mass` and the fuel :any:`DENSITY`. This volume
        generally changes over time due to fuel burning.

        :rtype: float
        """
        volume = self.mass / self.DENSITY
        return volume if volume > 0. else 0.

    # Inputs to the SubtractedSolid class
    @Attribute
    def shape_in(self):
        return self.tank_solid

    @Attribute
    def tool(self):
        """ This tool calculates the required position of the half space
        solid that is used to generate the fuel geometry, modelled with a
        solid. The half space solid is set at the midpoint of the interval
        containing all the fuel. When intersecting the fuel at the midpoint
        of this interval, it returns a certain fuel solid and corresponding
        volume. If this volume is too large for how much it should be,
        the halfspace solid is lowered (put at the middle of the previous
        midpoint and lower boundary. This process is repeated until the
        convergence criterion is met.
        Note that if the wing is canted, the tool is still kept horizontal
        with respect to the global axis system, such that fuel is burnt and
        redistributed as would be expected due to gravity.

        :rtype: parapy.geom.occ.halfspace.HalfSpaceSolid
        """
        max_iter = 50
        i = 0
        # Take the uppermost and lowermost points and set those as the
        # initial interval bounds
        ref_point1 = max(self.tank_solid.bbox.box.vertices,
                         key=lambda v: v.point.z).point
        ref_point2 = min(self.tank_solid.bbox.box.vertices,
                         key=lambda v: v.point.z).point
        interval = [ref_point1.interpolate(ref_point2, 1.2),
                    ref_point2.interpolate(ref_point1, 1.2)]

        convergence_error = np.inf
        while abs(convergence_error) > self.convergence_tol and i < max_iter:
            i += 1
            # Take the reference point as the middle of the interval.
            ref_point = interval[0].midpoint(interval[1])

            half_space_solid = HalfSpaceSolid(Plane(ref_point, 'z', 'y'))
            fuel_solid = SubtractedSolid(self.tank_solid, half_space_solid)

            try:
                volume = fuel_solid.volume
            except:
                volume = 0

            if self.volume > 0:
                convergence_error = (volume - self.volume) / self.volume
            else:
                convergence_error = volume - self.volume

            # Reset interval boundaries
            if convergence_error < 0:
                interval = [ref_point, interval[-1]]
            elif convergence_error > 0:
                interval = [interval[0], ref_point]

        return half_space_solid

    @Attribute
    def orientation(self):
        return self.tank_solid.orientation

    def burn(self, time_step):
        """ Burn fuel during a specified time step. This operation is an
        in-place operation; it changes the :any:`mass` of the fuel, but returns
        nothing (None), except for when the time interval supplied would
        yield a negative fuel mass. In this case, the function returns the
        maximum time step during which this tank can be used.

        :param time_step: time step during which fuel is burnt.
        :type time_step: float
        :rtype: None | float
        """
        wing = self.parent.parent

        if wing.engines is Undefined:
            aircraft = wing.parent
            if wing.name.startswith('vertical'):
                engines = aircraft.main_wing_starboard.engines + \
                          aircraft.main_wing_port.engines
            else:
                engines = aircraft.main_wing_starboard.engines
        else:
            engines = wing.engines

        fuel_flow_tot = sum(engine.thrust * engine.specific_fuel_consumption
                            for engine in engines)

        if self.mass >= time_step * fuel_flow_tot:
            # print 'mass: {}, time_step: {}, fuel_flow_tot: {}'.format(
            #     self.mass, time_step, fuel_flow_tot
            # )
            self.mass -= time_step * fuel_flow_tot

        else:
            # print 'mass: {}, time_step: {}, fuel_flow_tot: {}'.format(
            #     self.mass, time_step, fuel_flow_tot
            # )
            time_step = self.mass / fuel_flow_tot
            self.mass -= time_step * fuel_flow_tot

            return time_step
