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
        """ <<< Hier typ je je verhaal over wat een attribute doet. In dit
        geval is dat misschien niet nodig, aangezien "height_ratio"
        heel erg voor zich spreekt. Bij andere, minder duidelijke attributes
        zou je het wel kunnen doen. Je krijgt zo'n docstring makkelijk door
        drie keer op dubbele apostrof (") te drukken tussen "def" en je
        functie, dan op spatie en dan op enter te drukken. >>>

        :rtype: <<< Hier typ je wat voor een type variabele door je
        functie/attribute gereturnd wordt. Bijvoorbeeld, als ik een lijst
        van parapy punten return, zeg ik hier:
        "list[list[parapy.geom.generic.positioning.Point]"
        Stel je voor je weet niet wat voor een type een bepaald attribute
        is, dan kan je natuurlijk gewoon in je python console met
        type(obj.attribute_dat_je_wil_checken) kijken wat voor een type het is.
        Als ik een dictionary van strings naar integers return zeg ik hier:
        "dict[str: int]">>>
        """
        # This atribute converts the angle into a height ratio which is used
        # for the height positioning of the tail.

        #  Generates the placement of the aft tail. The angle is used to
        # convert it to a height ratio.
        # :rtype: float

        return self.tail_length * tan(radians(
            self.tail_angle)) / self.diameter - 0.5

    @Attribute
    # Returns the Nosecone section of the fuselage and is oriented in the
    # direction in order to make it coherent with the reference frame
    def nose(self):
        return NoseCone(length=self.nose_length,
                        final_diameter=self.diameter,
                        cockpit_length=self.cockpit_length)

    @Attribute
    # Returns cabin. This just consist of a few circular parts that are
    # connected by a LoftedSurfae.
    def cabin(self):
        return Cabin(length=self.cabin_length,
                     diameter_fuselage=self.diameter, n_circles=10,
                     position=translate(rotate90(
                         self.nose.circles_cockpit[-1].position, 'y'), 'x',
                         -self.cabin_length))

    @Attribute
    # Returns the tail segment. This is variable by the angle. The angle
    # calculates a height ratio, which  is used to position the aft position
    # of the tail itself.
    def tail(self):
        return TailCone(length=self.tail_length,
                        fuselage_diameter=self.diameter * 1.0,
                        height_ratio=self.tail_height_ratio,
                        position=rotate(translate(
                            self.position,
                            'x',
                            self.cabin_length + self.nose_length +
                            self.cockpit_length,
                            'z',
                            self.nose.scaling_cockpit[0] * self.diameter / 2.),
                            'x', radians(90)))

    #                     rotate(
    #                         Position(max(self.cabin.profiles,
    #                                      key=lambda p: p.center.x).center),
    #                         'x', radians(90))
    #                     )
    #
    # translate(
    #     self.position,
    #     'x',
    #     self.cabin_length + self.nose_length +
    #     self.cockpit_length, 'z',
    #     self.nose.scaling_cockpit[0] *
    #     self.diameter / 2.), 'x', radians(90))
    @Attribute
    def shape_in(self):
        return self.nose

    @Attribute
    def tool(self):
        """ Builds a Compound of all different parts of the fuselage

        :rtype: parapy.geom.Compound
        """
        return [self.cabin, self.tail]

    @Attribute
    def centre_gravity_x(self):
        return (self.tail.cog.x + self.nose.surface_cockpit.cog.x +
                self.nose.surface_nose.cog.x + self.cabin.cog.x) / 4.

    @Attribute
    def centre_gravity_y(self):
        return (self.tail.cog.y * 0.05 + self.nose.surface_cockpit.cog.y * 0.05 +
                self.nose
                .surface_nose.cog.y * 0.05 + self.cabin.cog.y * 0.9)

    @Attribute
    def centre_gravity_z(self):
        return (self.tail.cog.z + self.nose.surface_cockpit.cog.z + self.nose
                .surface_nose.cog.z + self.cabin.cog.z) / 4.

    @Attribute
    def centre_of_gravity_total(self):
        return Point(self.centre_gravity_x, self.centre_gravity_y,
                     self.centre_gravity_z)

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
