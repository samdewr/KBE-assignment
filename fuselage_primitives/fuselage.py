from math import tan, radians

from parapy.core import *
from parapy.geom import *

from fuselage_primitives.cabin import Cabin
from fuselage_primitives.nose import NoseCone
from fuselage_primitives.tail import TailCone


class Fuselage(FusedShell):

    """" This program gives the entire fuselage of the system, it uses 3
    seperate classes: cabin, tail and nose. These represent what the name
    suggests. The input is mainly based on the lengths of each section
    It combines the 3 parts and attaches them together. """

    __initargs__ = ['diameter', 'tail_angle', 'tail_length', 'cockpit_length',
                    'cabin_length', 'nose_length']

    # Required inputs
    diameter = Input()
    tail_angle = Input()
    tail_length = Input()
    cockpit_length = Input()
    cabin_length = Input()
    nose_length = Input()

    # Optional inputs
    color = 'orange'
    transparency = 0.6

    @Attribute
    def tail_height_ratio(self):
        """ The ratio of the height of the fuselage. This attribute shifts
        the angle of the tail into the height of the end of the tail
        accordingly.

        :rtype: float
        """

        return self.tail_length * tan(radians(self.tail_angle)) / \
               self.diameter - 0.5

    @Attribute
    def fuselage_length_total(self):
        return self.cabin_length+self.nose_length+self.cockpit_length+\
               self.tail_length

    @Attribute
    def nose(self):
        """ Returns the nose class

        :rtype: parapy.geom.boolean.FusedShell
        """
        return NoseCone(length=self.nose_length,
                        final_diameter=self.diameter,
                        cockpit_length=self.cockpit_length)

    @Attribute
    def cabin(self):
        """ Returns the Cabin class

            :rtype: parapy.geom.occ.Lofting
        """
        return Cabin(length=self.cabin_length,
                     diameter_fuselage=self.diameter, n_circles=10,
                     position=rotate(
                         self.nose.circles_cockpit[-1].position,
                         'y', radians(270)))


    @Attribute
    def tail(self):
        """ Returns the Tail class

            :rtype: parapy.geom.occ.Lofting
        """
        return TailCone(length=self.tail_length,
                        fuselage_diameter=self.diameter * 1.0,
                        height_ratio=self.tail_height_ratio,
                        position=rotate(
                            self.cabin.profiles[-1].position,
                            'y',radians(-90.)))
    @Attribute
    def shape_in(self):
        return self.nose


    @Attribute
    def tool(self):
        """ Builds a Compound of all different parts of the fuselage

        :rtype: parapy.geom.Compound
        """
        return [self.cabin, self.tail]

    # @Attribute
    # def centre_gravity_x(self):
    #     return (self.tail.cog.x + self.nose.surface_cockpit.cog.x +
    #             self.nose.surface_nose.cog.x + self.cabin.cog.x) / 4.
    #
    # @Attribute
    # def centre_gravity_y(self):
    #     return (self.tail.cog.y * 0.05 + self.nose.surface_cockpit.cog.y * 0.05 +
    #             self.nose
    #             .surface_nose.cog.y * 0.05 + self.cabin.cog.y * 0.9)
    #
    # @Attribute
    # def centre_gravity_z(self):
    #     return (self.tail.cog.z + self.nose.surface_cockpit.cog.z + self.nose
    #             .surface_nose.cog.z + self.cabin.cog.z) / 4.

    @Attribute
    def solid(self):
        # TODO: hangt af van of de tail goed aan kan sluiten aan de fuselage.
        return CloseSurface(self)

    # @Attribute
    # def centre_of_gravity_total(self):
    #     return Point(self.centre_gravity_x, self.centre_gravity_y,
    #                  self.centre_gravity_z)

    @Attribute
    def length(self):
        lengths = [segment.length for segment in self.tool + [self.nose]]
        return sum(length for length in lengths)

    @Attribute
    def end(self):
        return self.tail.profiles[-1].position.location

    @Attribute
    def center_line(self):
        """ Return the line that is the center of the fuselage.

        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        return Wire([segment.center_line
                     if segment.center_line.direction_vector.x > 0
                     else segment.center_line.reversed
                     for segment in [self.nose, self.cabin, self.tail]])


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage(diameter=3.0, cabin_length=20., cockpit_length=3.0,
                   nose_length=1.0, tail_length=5.0, tail_angle=10.)

    display(obj)
