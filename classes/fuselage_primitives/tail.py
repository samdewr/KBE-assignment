import numpy as np
from parapy.core import *
from parapy.geom import *


class TailCone(LoftedSurface):

    # Inputs for the Tail
    height_ratio = Input()
    length = Input(validator=val.is_positive)
    fuselage_diameter = Input(validator=val.is_positive)

    @Attribute
    def tail_scaling_list(self):
        """ Generates a list of scaling factors that decreases step by step
        this is later used for the generation of the circles that form the
        tail.
        :rtype: float
        """
        return np.arange(1., 0.05, -0.05)

    @Attribute
    # The distance between each circle is predefined by this attribute.
    def section_length(self):
        """ Defines the length between each circle. This will also be used
        later for the generation of the circles.

        :rtype: float
        """
        return self.length / (len(self.tail_scaling_list) - 1)

    @Part(in_tree=False)
    def tail_circles(self):
        """ Builds a continuous number of circles. These circles become
        smaller and smaller by each circle with the help of the scaling
        list. Furthermore, The position is affected by height ratio

        :rtype: parapy.geom.occ.curve.Circle
        """
        return Circle(
            quantify=len(self.tail_scaling_list),
            position=rotate90(
                translate(self.position,
                          'x', child.index * self.section_length,
                          'y', self.fuselage_diameter * self.height_ratio *
                          (self.tail_scaling_list[0] -
                           self.tail_scaling_list[child.index])), 'y'),
            radius=self.tail_scaling_list[child.index]
            * self.fuselage_diameter / 2.)

    @Attribute
    def profiles(self):
        """ This is the input for the LoftedSurface that generates the shell
        for the total tail.

        :rtype: parapy.geom.occ.lofting.LoftedSurface
        """
        return self.tail_circles

    @Attribute
    def center_line(self):
        """ Return the line that is the center of the tail.

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
    obj = TailCone(height_ratio=0.5, length=3., fuselage_diameter=3.)
    display(obj)
    __initargs__ = ['n_wing_segments', 'airfoil_names', 'chords', 'twists',
                    'sweeps_le', 'dihedral_angles', 'spanwise_positions',
                    'semi_span', 'wing_cant', 'n_spars',
                    'spar_chordwise_positions', 'spar_aspect_ratios',
                    'spar_profiles', 'spar_spanwise_positions_end',
                    'n_ribs_wb', 'ribs_wb_spanwise_reference_spars_idx',
                    'ribs_wb_spanwise_positions',
                    'ribs_wb_orientation_reference_spars',
                    'ribs_wb_orientation_angles',
                    'n_ribs_te', 'ribs_te_spanwise_reference_spars_idx',
                    'ribs_te_spanwise_positions',
                    'ribs_te_orientation_reference_spars',
                    'ribs_te_orientation_angles',
                    'n_ribs_le', 'ribs_le_spanwise_reference_spars_idx',
                    'ribs_le_spanwise_positions',
                    'ribs_le_orientation_reference_spars',
                    'ribs_le_orientation_angles', 'fuel_tank_boundaries',
                    'n_movables',
                    'movable_spanwise_starts', 'movable_spanwise_ends',
                    'movable_hingeline_starts', 'movable_deflections',
                    'n_engines',
                    'engine_spanwise_positions', 'engine_overhangs']
