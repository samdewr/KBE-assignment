from parapy.core import *
from parapy.geom import *


class Cabin(LoftedSurface):

    length = Input()
    diameter_fuselage = Input()
    n_circles = Input(validator=val.is_number)

    @Attribute
    def length_sections(self):
        return self.length / (self.n_circles - 1)


    @Part(in_tree=False)
    def profiles(self):
        """ Builds the circles necessary for the Cabin part of the fuselage.
        These are also input for the LoftedSurface and thus the shell is
        generated.

                        :rtype: parapy.geom.occ.lofting.
                        """
        return Circle(quantify=self.n_circles,
                      radius=self.diameter_fuselage / 2.,
                      position=rotate90(translate(self.position,
                                        'x',child.index * self.length_sections)
                                        , 'y'))

    @Attribute
    def center_line(self):
        """ Return the line that is the center of the cabin.

        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        return FittedCurve([profile.center for profile in self.profiles])

    @Attribute
    def upper_line(self):
        """ Return the :attr:`center_line` projected onto the upper half of
        the surface (onto the 'ceiling').

        :rtype: parapy.geom.occ.projection.ProjectedCurve
        """
        return ProjectedCurve(self.center_line, self, self.position.Vz)

if __name__ == '__main__':
    from parapy.gui import display
    obj = Cabin(length=10., diameter_fuselage=3., n_circles=10)
    display(obj)
