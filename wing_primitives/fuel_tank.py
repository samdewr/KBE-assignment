from parapy.core import *
from parapy.geom import *

from wing_primitives.fuel import Fuel


class FuelTank(SewnShell):
    """ This class represents a fuel tank within a wing.
    """
    wing = Input()

    starting_rib_index = Input(validator=lambda x: isinstance(x, int))
    ending_rib_index = Input(validator=lambda x: isinstance(x, int))

    color = Input('green')
    transparency = Input(0.6)
    tolerance = Input(1e-3)

    __initargs__ = ['wing', 'starting_rib_index', 'ending_rib_index']

    # Input to the SewnShell Class
    @Attribute
    def built_from(self):
        return [self.starting_rib, self.front_tank_spar, self.upper_surface,
                self.lower_surface, self.ending_rib, self.rear_tank_spar]

    @Attribute
    def orientation(self):
        """ Overwrites the default orientation, such that the fuel tank
        orientation is changed, whenever the wing cant angle is changed.

        :rtype: parapy.geom.generic.positioning.Orientation
        """
        return self.wing.orientation

    @Attribute
    def starting_rib(self):
        """ Returns the first rib that makes up one of the faces of this
        fuel tank. The first rib is the most inboard rib.

        :rtype: wing_primitives.structural_elements.rib.WingBoxRib
        """
        return self.wing.wing_box_ribs[self.starting_rib_index]

    @Attribute
    def ending_rib(self):
        """ Returns the second rib that makes up one of the faces of this
        fuel tank. The second rib is the most outboard rib.

        :rtype: wing_primitives.structural_elements.rib.WingBoxRib
        """
        return self.wing.wing_box_ribs[self.ending_rib_index]

    @Attribute
    def mid_rib_pos(self):
        """ Returns a point lying in between the two centres of gravity of
        the starting and ending ribs.

        :rtype: parapy.geom.generic.positioning.Point
        """
        return self.ending_rib.cog.midpoint(self.starting_rib.cog)

    @Attribute
    def front_spar(self):
        """ Returns the entire (full length over the entire wing) front spar
        that is used to make one of the faces of this fuel tank.

        :rtype: wing_primitives.structural_elements.spar.FusedSpar
        """
        return min(self.wing.spars, key=lambda s: s.position.x)

    @Attribute
    def front_spar_segments(self):
        """ Returns the segments (components) of the front spar that
        are in contact with the starting and ending ribs of the fuel tank.
        These segments are effectively the components that are used to make
        the front spar face of the fuel tank.

        :rtype: list[wing_primitives.structural_elements.spar.SparSegment]
        """
        return [spar_segment for spar_segment in self.front_spar.segments
                if IntersectedShapes(self.starting_rib.rib_plane,
                                     spar_segment).edges or
                IntersectedShapes(self.ending_rib.rib_plane,
                                  spar_segment).edges]

    @Attribute
    def rear_spar(self):
        """ Returns the entire (full length over the entire wing) rear spar
        that is used to make one of the faces of this fuel tank.

        :rtype: wing_primitives.structural_elements.spar.FusedSpar
        """
        return max(self.wing.spars, key=lambda s: s.position.x)

    @Attribute
    def rear_spar_segments(self):
        """ Returns the segments (components) of the rear spar that
        are in contact with the starting and ending ribs of the fuel tank.
        These segments are effectively the components that are used to make
        the rear spar face of the fuel tank.

        :rtype: list[wing_primitives.structural_elements.spar.SparSegment]
        """
        return [spar_segment for spar_segment in self.rear_spar.segments
                if IntersectedShapes(self.starting_rib.rib_plane,
                                     spar_segment).edges or
                IntersectedShapes(self.ending_rib.rib_plane,
                                  spar_segment).edges]

    @Attribute
    def spar_half_space_solids(self):
        """ Creates the HalfSpaceSolids that are run through the front and
        rear spar segments and have their matter on the side of the fuel
        tank centre of mass (defined by :any:`mid_rib_pos`).

        :rtype: list[parapy.geom.occ.halfspace.HalfSpaceSolid]
        """
        return [HalfSpaceSolid(segment.web_plane, self.mid_rib_pos)
                for segment in self.front_spar_segments] + \
               [HalfSpaceSolid(segment.web_plane, self.mid_rib_pos)
                for segment in self.rear_spar_segments]

    @Attribute
    def rib_half_space_solids(self):
        """ Creates the HalfSpaceSolids that are run through the starting and
        ending ribs and have their matter on the side of the fuel
        tank centre of mass (defined by :any:`mid_rib_pos`).

        :rtype: list[parapy.geom.occ.halfspace.HalfSpaceSolid]
        """
        return [HalfSpaceSolid(self.starting_rib.rib_plane, self.mid_rib_pos),
                HalfSpaceSolid(self.ending_rib.rib_plane, self.mid_rib_pos)]

    @Attribute
    def front_tank_spar(self):
        """ Creates the face that makes for the front spar tank face. This
        face is obtained by splitting the :any:`front_spar_segments` with
        the starting and ending rib planes. Because the spar segments are
        individual segments, several split shells are obtained upon this
        splitting operation. From the split segments, the faces of which
        the centres of gravity lie within both the
        :any:`rib_half_space_solids` are selected.

        :rtype:  parapy.geom.occ.sewing.SewnShell
        """
        split_spar_faces = [fce for spar in self.front_spar_segments for fce in
                            SplitSurface(spar.web,
                                         [self.starting_rib.rib_plane,
                                          self.ending_rib.rib_plane]).faces]
        return SewnShell(
            [fce for fce in split_spar_faces if
             all(half_space_solid.is_point_inside(fce.cog)
                 for half_space_solid in self.rib_half_space_solids)]
        )

    @Attribute
    def rear_tank_spar(self):
        """ Creates the face that makes for the rear spar tank face. This
        face is obtained by splitting the :any:`rear_spar_segments` with
        the starting and ending rib planes. Because the spar segments are
        individual segments, several split shells are obtained upon this
        splitting operation. From the split segments, the faces of which
        the centres of gravity lie within both the
        :any:`rib_half_space_solids` are selected.

        :rtype:  parapy.geom.occ.sewing.SewnShell
        """
        split_spar_faces = [fce for spar in self.rear_spar_segments for fce in
                            SplitSurface(spar.web,
                                         [self.starting_rib.rib_plane,
                                          self.ending_rib.rib_plane]).faces]
        return SewnShell(
            [fce for fce in split_spar_faces if
             all(half_space_solid.is_point_inside(fce.cog)
                 for half_space_solid in self.rib_half_space_solids)]
        )

    @Attribute
    def upper_surface(self):
        """ Returns the upper surface of the fuel tank by cutting the upper
        wing surface with:
            - the front tank spar, extended in positive and negative 'z'
              direction, to ensure a proper intersection
              (:any:`extended_front_tank_spar`).
            - the rear tank spar, extended in positive and negative 'z'
              direction, to ensure a proper intersection
              (:any:`extended_rear_tank_spar`).
            - the rib plane of the starting rib
            - the rib plane of the ending rib
        Because the wing is a multi-segment (Sewn) surface,
        this splitting results in multiple wing segments which should be joined
        together to retrieve the proper upper tank surface. This is done by
        looping over the attained split segments, and selecting all elements
        of which the centres of gravity lie within the rib as well as the spar
        halfspace solids. These segments are then sewn back together in the
        end.

        :rtype: parapy.geom.occ.sewing.SewnShell
        """
        cutting_srf = self.extended_front_tank_spar + \
            self.extended_rear_tank_spar + \
            [self.starting_rib.rib_plane, self.ending_rib.rib_plane]

        split_wing_faces = [fce for srf in self.wing.upper_surface.faces
                            for fce in SplitSurface(srf, cutting_srf).faces]
        return SewnShell(
            [fce for fce in split_wing_faces if
             all(half_space_solid.is_point_inside(fce.cog)
                 for half_space_solid in
                 self.spar_half_space_solids + self.rib_half_space_solids)]
        )

    @Attribute
    def lower_surface(self):
        """ Returns the lower surface of the fuel tank by cutting the lower
        wing surface with:
            - the front tank spar, extended in positive and negative 'z'
              direction, to ensure a proper intersection
              (:any:`extended_front_tank_spar`).
            - the rear tank spar, extended in positive and negative 'z'
              direction, to ensure a proper intersection
              (:any:`extended_rear_tank_spar`).
            - the rib plane of the starting rib.
            - the rib plane of the ending rib.
        Because the wing is a multi-segment (Sewn) surface,
        this splitting results in multiple wing segments which should be joined
        together to retrieve the proper upper tank surface. This is done by
        looping over the attained split segments, and selecting all elements
        of which the centres of gravity lie within the rib as well as spar
        halfspace solids. These segments are then sewn back together in the
        end.

        :rtype: parapy.geom.occ.sewing.SewnShell
        """
        cutting_srf = self.extended_front_tank_spar + \
            self.extended_rear_tank_spar + \
            [self.starting_rib.rib_plane, self.ending_rib.rib_plane]

        split_wing_faces = [fce for srf in self.wing.lower_surface.faces
                            for fce in SplitSurface(srf, cutting_srf).faces]
        return SewnShell(
            [fce for fce in split_wing_faces if
             all(half_space_solid.is_point_inside(fce.cog)
                 for half_space_solid in
                 self.spar_half_space_solids + self.rib_half_space_solids)]
        )

    @Attribute
    def extended_front_tank_spar(self):
        """ Extends the front tank spar in the direction normal to the
        flight and spanwise directions. This is useful when used as a tool
        for intersecting shapes (see :any:`upper_surface` and
        :any:`lower_surface`).

        :rtype: list[parapy.geom.occ.surface.ExtendedSurface]
        """
        no_spar_fces = len(self.front_tank_spar.faces)
        if no_spar_fces == 1:
            return [self.front_spar_segments[0].web_plane]
        elif no_spar_fces == 2:
            sides = [['u-', 'v'], ['u+', 'v']]
        else:
            sides = [['u-', 'v']] + (no_spar_fces - 2) * ['v'] + [['u+', 'v']]
        return [ExtendedSurface(fce, distance=10.0, side=sides[idx])
                for idx, fce in enumerate(self.front_tank_spar.faces)]

    @Attribute
    def extended_rear_tank_spar(self):
        """ Extends the rear tank spar in the direction normal to the
        flight and spanwise directions. This is useful when used as a tool
        for intersecting shapes (see :any:`upper_surface` and
        :any:`lower_surface`).

        :rtype: list[parapy.geom.occ.surface.ExtendedSurface]
        """
        no_spar_fces = len(self.rear_tank_spar.faces)
        if no_spar_fces == 1:
            return [self.rear_spar_segments[0].web_plane]
        elif no_spar_fces == 2:
            sides = [['u-', 'v'], ['u+', 'v']]
        else:
            sides = [['u-', 'v']] + (no_spar_fces - 2) * ['v'] + [['u+', 'v']]
        return [ExtendedSurface(fce, distance=10.0, side=sides[idx])
                for idx, fce in enumerate(self.rear_tank_spar.faces)]

    @Attribute
    def solid(self):
        """ Returns a solid of the fuel tank by cutting the wing solid with
        the boundary elements of the fuel tank (rib planes and front and
        rear tank spars). The splitting is done in two phases, because
        ParaPy cannot handle tools intersecting within the wing solid.

        :rtype: parapy.geom.occ.solid.Solid_
        """
        tools1 = [self.starting_rib.rib_plane, self.ending_rib.rib_plane]
        tools2 = self.extended_front_tank_spar + self.extended_rear_tank_spar

        split_wing1 = SplitSolid(self.wing.closed_solid, tools1)
        solid = min(split_wing1.solids,
                    key=lambda s: s.cog.distance(self.mid_rib_pos))
        split_wing2 = SplitSolid(solid, tools2)

        return min(split_wing2.solids,
                   key=lambda s: s.cog.distance(self.mid_rib_pos))

    @Attribute
    def volume(self):
        return self.solid.volume

    @Attribute
    def is_empty(self):
        return self.fuel.volume <= 0.

    @Attribute
    def is_full(self):
        return self.fuel.volume >= self.volume

    @Part
    def fuel(self):
        return Fuel(self.solid)


if __name__ == '__main__':
    from parapy.gui import display
    obj = ()
    display(obj)
