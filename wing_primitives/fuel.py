from os.path import dirname, join

import pandas as pd
from parapy.core import *
from parapy.geom import *


class Fuel(SubtractedSolid):

    # Class constants
    CONSTANTS = pd.read_excel(
        join(dirname(dirname(__file__)), 'input', 'constants.xlsx'),
        sheet_name='fuel', index_col=0
    )

    DENSITY = CONSTANTS.loc['density']['value']
    DENSITY_UNITS = CONSTANTS.loc['density']['units']
    SPECIFIC_FUEL_CONSUMPTION = CONSTANTS.loc['SFC']['value']
    SPECIFIC_FUEL_CONSUMPTION_UNITS = CONSTANTS.loc['SFC']['units']

    # Inputs
    tank_solid = Input()

    # Optional inputs
    color = Input('red')
    transparency = Input(0.75)
    fuel_burn_plane_increment_distance = Input(0.01)

    __initargs__ = ['tank_solid']

    @Input
    def initial_volume(self):
        """ Sets the initial volume of the fuel to the maximum volume
        fittable in the fuel tank.

        :rtype: float
        """
        return abs(self.tank_solid.volume)

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
        return self.initial_volume * self.DENSITY

    @Attribute
    def volume(self):
        """ Calculates the current volume of the fuel as a function of the
        remaining fuel :any:`mass` and the fuel :any:`DENSITY`. This volume
        generally changes over time due to fuel burning.

        :rtype: float
        """
        return self.mass / self.DENSITY

    # Inputs to the SubtractedSolid class
    @Attribute
    def shape_in(self):
        return self.tank_solid

    @Attribute
    def tool(self):
        """ This tool calculates the required position of the half space
        solid that is used to generate the fuel geometry, modelled with a
        solid. The half space solid is lowered by small increments delta_z,
        based on the parameter :any:`fuel_burn_plane_increment_distance`,
        such that at some point the volume of the SubtractedSolid is
        slightly smaller than the current fuel :any:`volume`. This halfspace
        solid at this position is then returned.

        Note that if the wing is canted, the tool is still kept horizontal
        with respect to the global axis system, such that fuel is burnt and
        redistributed as would be expected due to gravity.

        :rtype: parapy.geom.occ.halfspace.HalfSpaceSolid
        """
        # Q: how can I fix ref_point, such that the ref_point is taken as
        #  the uppermost point on the entire fuel tank.
        ref_point = max(self.tank_solid.bbox.box.vertices,
                        key=lambda v: v.point.z).point
        half_space_solid = HalfSpaceSolid(Plane(ref_point, 'z', 'y'))
        fuel_solid = SubtractedSolid(self.tank_solid, half_space_solid)
        while abs(fuel_solid.volume) > self.volume:
            delta_z = self.fuel_burn_plane_increment_distance
            half_space_solid = half_space_solid.translated('z_', delta_z)
            fuel_solid = SubtractedSolid(self.tank_solid, half_space_solid)
        return half_space_solid

    @Attribute
    def orientation(self):
        return self.tank_solid.orientation

    @Attribute
    def fuel_expansion_factor(self):
        return

    def burn(self, time_step):
        """ Burn fuel during a specified time step. This operation is an
        in-place operation; it changes the :any:`mass` of the fuel, but returns
        nothing (None).

        :param time_step: time step during which fuel is burnt.
        :type time_step: float
        :rtype: None
        """
        # TODO replace 1. with the thrust of the engine(s) this fuel tank
        #  delivers to.
        self.mass -= self.SPECIFIC_FUEL_CONSUMPTION * time_step * 1.
