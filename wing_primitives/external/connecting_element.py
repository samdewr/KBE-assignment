import math

import numpy as np
from parapy.core import *
from parapy.geom import *


class ConnectingElement(LoftedSurface, SweptSurface):
    """ Returns a connecting surface element between two airfoils. For
    example, between the main wing and a connected winglet. Essentially,
    a ConnectingElement is a combination of a LoftedSurface and a
    SweptSurface in that it linearly interpolates profiles, but that it also
    draws this interpolation along a circular arc.
    """

    airfoil1 = Input()
    airfoil2 = Input()

    __initargs__ = ['airfoil1', 'airfoil2']

    # Optional inputs
    radius = Input(0.3)
    n_profiles = Input(5)

    @Attribute
    def cant_angle(self):
        """ The angle (in degrees) between the two airfoils that are to be
        connected (:any:`airfoil1` and :any:`airfoil2`).

        :rtype: float
        """
        return math.degrees(self.airfoil1.orientation.rotation_angle(
            self.airfoil2.orientation
        ))

    @Attribute
    def rotation_axis(self):
        """ The axis of rotation corresponding to the :any:`cant_angle`
        between the two airfoils (:any:`airfoil1` and :any:`airfoil2` that
        are connected).

        :rtype: parapy.geom.generic.positioning.Vector
        """
        return self.airfoil1.plane_normal.cross(self.airfoil2.plane_normal)

    @Attribute
    def rotation_line(self):
        """ The line on the intersections of the two planes containing
        :any:`airfoil1` and :any:`airfoil2`.

        :rtype: parapy.geom.occ.curve.Line_
        """
        return self.airfoil1.plane.intersection_curves(self.airfoil2.plane)[0]

    @Attribute
    def plane_cutter(self):
        plane_binormal1 = self.airfoil1.position - self.airfoil2.position
        plane_binormal2 = self.airfoil1.plane_normal
        plane_normal = plane_binormal1.cross(plane_binormal2)
        plane = Plane(self.airfoil1.position, plane_normal, plane_binormal1)
        return plane

    @Attribute
    def centre_of_curvature(self):
        """ Returns the centre of curvature (the centre of the :any:`path`
        arc). This centre of is taken as the potential centre of curvature
        nearest to the :any:`rotation_line`, because there are two
        theoretical centres of curvature possible. However, one of these is
        physically non-sensical.

        :rtype: parapy.geom.generic.positioning.Point
        """
        plane_binormal1 = self.airfoil1.position - self.airfoil2.position
        plane_binormal2 = self.airfoil1.plane_normal
        plane_normal = plane_binormal1.cross(plane_binormal2)
        plane = Plane(self.airfoil1.position, plane_normal, plane_binormal1)

        curves = self.spheres[0].intersection_curves(self.spheres[1])
        if not curves:
            raise Exception('The ConnectingElement {} radius is set too '
                            'small.'.format(self))

        centres = [plane.intersection_points(crv) for crv in curves]
        centres = [centre for lst in centres for centre in lst]

        return min(centres,
                   key=lambda p: self.rotation_line.minimum_distance(p))

    @Attribute
    def spheres(self):
        """ Two spheres that serve as a helper in determining the centre of
        curvature of the :any:`path` along which the profiles are mapped.

        :rtype: list[parapy.geom.occ.surface.SphericalSurface]
        """
        return [SphericalSurface(radius=self.radius,
                                 position=self.airfoil1.position),
                SphericalSurface(radius=self.radius,
                                 position=self.airfoil2.position)]

    @Attribute
    def path(self):
        """ Returns the path (an arc) along which the profile is drawn. The
        positions of the two airfoils (:any:`airfoil1` and :any:`airfoil2`)
        that are connected always lie on this arc.

        :rtype: parapy.geom.occ.curve.Arc2P
        """
        return Arc2P(self.centre_of_curvature,
                     self.airfoil1.position, self.airfoil2.position)

    @Attribute
    def profiles(self):
        """ Return the profiles that serve as an input to the
        ConnectingElement LoftedSurface. First, the mixing factors are
        determined by making a linear range from 0 to 1, based on
        :any:`n_profiles`. Then, the angles and orientations are obtained by
        linearly interpolating, based on the profile's position in the
        sequence. The position is obtained by mapping the point along the
        :any:`path` curve.

        :rtype: list[parapy.geom.occ.curve.BSplineCurve_]
        """
        mixing_factors = np.linspace(0, 1, self.n_profiles)
        angles = [self.cant_angle * factor for factor in mixing_factors]
        orientations = [rotate(self.airfoil1.orientation, self.rotation_axis,
                               angle, deg=True) for angle in angles]
        points = [self.path.point(factor * self.path.u_max)
                  for factor in mixing_factors]
        return [self.mix_airfoils(mixing_factors[i]).transformed(
            Position(points[i], orientations[i]),
            self.airfoil1.position)
            for i in range(self.n_profiles)]

    def mix_airfoils(self, mixing_factor):
        """ Linearly interpolates two airfoils that may have a different
        orientation with respect to each other. :any:`airfoil2` is transformed
        onto the position of :any:`airfoil1`, and attains the same
        orientation. Then, the mixing factor interpolates towards one of the
        two airfoils. A factor of 1 will yield the original :any:`airfoil2`,
        while a factor of 0 will yield the original :any:`airfoil1`.

        :param mixing_factor:
        :type mixing_factor: float
        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        airfoil2 = self.airfoil2.transformed(
            new_position=self.airfoil1.position,
            old_position=self.airfoil2.position
        )
        pnts1 = self.airfoil1.equispaced_points(100)
        pnts2 = airfoil2.equispaced_points(100)
        mixed_points = [pt1.interpolate(pt2, frac=mixing_factor)
                        for pt1, pt2 in zip(pnts1, pnts2)]

        return FittedCurve(mixed_points)


if __name__ == '__main__':
    from parapy.gui import display
    obj3 = ConnectingElement()
    display(obj3)
