from parapy.core import *
from parapy.geom import *
from cabin import Cabin
import numpy as np
from math import sqrt


class NoseCone(FusedShell):
    length = Input(2.)
    cockpit_length = Input(5.)
    final_diameter = Input(5.)

    # list of scaling factors for the nose diameter
    @Attribute
    def list_scaling(self):
        """ Generates an array with the scaling factors, this will help with
        the scaling for the nose part of the nosecone.
                        :rtype array
                        """
        numbers = np.arange(0.0001, .5 ** 2, 0.01)
        numbers2 = [sqrt(i) for i in numbers]
        return numbers2

    @Attribute
    def nose_steps(self):
        return self.length / (len(self.list_scaling) - 1)

    @Attribute
    def length_nosecone(self):
        return self.length + self.cockpit_length

    @Part(in_tree=False)
    def circles_nose(self):
        """ Builds the circles that lay the foundation for the nose. The
        circles change radius each time.
        :rtype: parapy.geom.occ.curve.Circle
        """
        return Circle(quantify=len(self.list_scaling),
                      position=rotate90(translate(self.position,
                                        'x', child.index * self.nose_steps)
                                        ,'y'),
                      radius=self.list_scaling[child.index]
                             * self.final_diameter / 2.)

    @Attribute  # The Lofted surface for the first part of the nose, afterwards
    # comes the cockpit
    def surface_nose(self):
        """ Generates the shell based on the circles that govern the shape
        of the nose.
        :rtype: parapy.geom.occ.lofting.LoftedSurface
        """
        return LoftedSurface(profiles=self.circles_nose)

    @Attribute
    def steps_cockpit(self):
        """ Gives the spacing between the circles for the cockpit.
        :rtype: float
        """
        return self.cockpit_length / (len(self.scaling_cockpit) - 1)

    @Attribute
    def scaling_cockpit(self):
        """ The same for the nose part. This generates an array that will
        help shape the cockpit.
        :rtype: array
        """

        numbers = np.arange(self.list_scaling[-1] ** 2, 1. ** 2, 0.01)
        numbers2 = [sqrt(j) for j in numbers]
        return numbers2

    @Part(in_tree=False)
    def circles_cockpit(self):
        """ Generates a number of circles to make the shell of the cockpit.
        The circles start at the position where the nose ends. The part is
        also shifted upwards, because the pilots have to fit.

        :rtype: parapy.geom.occ.curve.Circle
        """
        return Circle(quantify=len(self.scaling_cockpit),
                      position=rotate90(
                          translate(self.circles_nose[-1].position,
                                    'z',child.index * self.steps_cockpit,
                                    'x',-self.final_diameter / 2. *
                                        (self.scaling_cockpit[child.index] -
                                        self.list_scaling[-1])),
                                    'z'),
                      radius=self.scaling_cockpit[child.index] *
                                         self.final_diameter / 2.)

    @Attribute
    def surface_cockpit(self):
        """ Generates a shell around the circles to give the cockpit a shape
        and a shell.

        :rtype: parapy.geom.occ.lofting.LoftedSurface
        """
        return LoftedSurface(profiles=self.circles_cockpit)

    @Attribute
    def center_line(self):
        """ Return the line that is the center of the nose cone.

        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        profiles = self.circles_nose + self.circles_cockpit
        return FittedCurve([profile.center for profile in profiles])

    @Attribute
    def upper_line(self):
        """ Return the :attr:`center_line` projected onto the upper half of
        the surface (onto the 'ceiling').

        :rtype: parapy.geom.occ.projection.ProjectedCurve
        """
        return ProjectedCurve(self.center_line, self, self.position.Vz)

    @Attribute
    def profiles(self):
        return self.circles_nose + self.circles_cockpit

    @Attribute
    def shape_in(self):
        return self.surface_cockpit

    @Attribute
    def tool(self):
        return self.surface_nose


if __name__ == '__main__':
    from parapy.gui import display

    obj = NoseCone(length=3.0, cockpit_length=3., final_diameter=5.)
    display(obj)
