import kbeutils.avl as avl

from parapy.core import *
from parapy.geom import *
import math

from fuselage_primitives.cabin import Cabin
from fuselage_primitives.nose import NoseCone
from fuselage_primitives.tail import TailCone


class Fuselage(SewnShell):

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
    tolerance = Input(1e-2)

    @Attribute
    def built_from(self):
        return [self.cabin, self.nose, self.tail]

    @Attribute
    def tail_height_ratio(self):
        """ The ratio of the height of the fuselage. This attribute shifts
        the angle of the tail into the height of the end of the tail
        accordingly.

        :rtype: float
        """

        return self.tail_length * math.tan(math.radians(self.tail_angle)) / \
               self.diameter - 0.5

    @Part(in_tree=False)
    def nose(self):
        """ Returns the nose class

        :rtype: parapy.geom.boolean.FusedShell
        """
        return NoseCone(length=self.nose_length,
                        final_diameter=self.diameter,
                        cockpit_length=self.cockpit_length)

    @Part(in_tree=False)
    def cabin(self):
        """ Returns the Cabin class

            :rtype: parapy.geom.occ.Lofting
        """
        return Cabin(length=self.cabin_length,
                     diameter_fuselage=self.diameter, n_circles=10,
                     position=rotate(
                         self.nose.circles_cockpit[-1].position,
                         'y', math.radians(270)))

    @Part(in_tree=False)
    def tail(self):
        """ Returns the Tail class

            :rtype: parapy.geom.occ.Lofting
        """
        return TailCone(length=self.tail_length,
                        fuselage_diameter=self.diameter * 1.0,
                        height_ratio=self.tail_height_ratio,
                        position=rotate(
                            self.cabin.profiles[-1].position,
                            'y', math.radians(-90.)))
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
    def solid(self):
        # TODO: hangt af van of de tail goed aan kan sluiten aan de fuselage.
        return CloseSurface(self)

    @Attribute
    def length(self):
        vector = self.end - self.position
        return vector.x

    @Attribute
    def end(self):
        return self.tail.profiles[-1].position.location

    @Attribute
    def center_line(self):
        """ Return the line that is the center of the fuselage.

        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        return ComposedCurve(
            [segment.center_line if segment.center_line.direction_vector.x > 0
             else segment.center_line.reversed
             for segment in [self.nose, self.cabin, self.tail]]
        )

    @Attribute
    def upper_line(self):
        """ Return the :attr:`center_line` projected onto the upper fuselage
        surface (onto the 'ceiling').

        :rtype: parapy.geom.occ.projection.ProjectedCurve
        """
        return ProjectedCurve(self.center_line, self, self.position.Vz)
    #
    # @Attribute
    # def avl_body(self):
    #     points = [Point()]
    #     return avl.Body()

    @Attribute
    def sample_points(self):
        profiles = [profile for segment in [obj.nose, obj.cabin, obj.tail]
                    for profile in segment.profiles]
        plne = Plane(self.position, self.position.Vy, self.position.Vx)
        points = [[max(profile.intersection_points(plne),
                       key=lambda pt: pt.z) for profile in profiles],
                  [min(profile.intersection_points(plne),
                       key=lambda pt: pt.z) for profile in profiles]]
        return points

    def point_at_fractions(self, f_long, f_trans, f_lat):
        """ Return a point at a certain longitudinal, transverse,
        and lateral fraction of the fuselage. The point that is returned is
        first placed longitudinally, then transversely, and then laterally.
        This means that if a value of :any:`f_trans` of 1 is passed,
        the value of f_lat does not matter anymore, because there is no
        'room' to move the point laterally anymore.

        :param f_long: the longitudinal fraction of the fuselage at which
            the point is placed. Has a value between 0 and 1. A value of 0
            corresponds to the fuselage nose.
        :type f_long: float
        :param f_trans: the transverse fraction of the fuselage at which
            the point is placed. Has a value between 0 and 1. A value of 0
            corresponds to the fuselage bottom.
        :type f_trans: float
        :param f_lat: the lateral fraction of the fuselage at which
            the point is placed. Has a value between 0 and 1. A value of 0
            corresponds to the fuselage center.
        :type f_lat: float

        :rtype: float
        """
        f_trans = -1. + f_trans * 2.
        cutting_plane = Plane(
            translate(self.position, 'x', self.length * f_long),
            self.position.Vx, self.position.Vz
        )
        circle = IntersectedShapes(cutting_plane, self).edges[0]
        radius = circle.start.distance(circle.cog)
        angle = math.asin(f_trans)
        dz = f_trans * radius
        dy = radius * math.cos(angle)

        point1 = translate(circle.cog, 'z', dz)
        point2 = translate(circle.cog, 'z', dz, 'y', dy)

        return point1.interpolate(point2, f_lat)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage(diameter=3.0, cabin_length=20., cockpit_length=3.0,
                   nose_length=1.0, tail_length=5.0, tail_angle=10.)

    display(obj)
