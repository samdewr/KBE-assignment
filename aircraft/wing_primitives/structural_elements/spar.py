import numpy as np
from parapy.core import *
from parapy.geom import *


class SparSegment(FusedShell):

    # Required inputs
    wing_segment = Input()
    chordwise_pos_root = Input(validator=val.Between(0, 1))
    chordwise_pos_tip = Input(validator=val.Between(0, 1))
    profile = Input(validator=val.OneOf(['C', 'C_', 'I']))
    aspect_ratio = Input(validator=val.is_positive)

    # Optional inputs
    spanwise_pos_end = Input(1, validator=val.Range(0, 1, incl_min=False))
    # Q: Why do I need to manually assign the position of the spar and of
    #  its flanges? If I do not pass the position=... argument for the Spar
    #  part in LiftingSurface, and if I don't do so for the web and flanges
    #  either, its position is set at 0, 0, 0.
    position = Input()

    __initargs__ = ['wing_segment', 'chordwise_pos_root',
                    'chordwise_pos_tip', 'profile', 'aspect_ratio',
                    'position']

    # Optional inputs
    color = Input('cyan')

    @Attribute
    def orientation(self):
        return Orientation(x=-self.web.plane_normal,
                           z=self.wing_segment.position.Vz)

    # Required inputs for the FusedShell class.
    @Attribute
    def shape_in(self):
        return self.web

    # Required input for the Compound class.
    @Attribute
    def tool(self):
        return self.flanges

    # Spar specific attributes.
    @Attribute
    def spar_line(self):
        """ Draw the line along which the spar for this segment will be placed.

        :rtype: parapy.geom.occ.curve.LineSegment
        """
        # Q: Why do I need to use a dimensionalised U-parameter for
        #  crv.point_at_parameter/crv.point instead of a non-dimensional
        #  normalised fraction?
        root_chord = self.wing_segment.root_airfoil.chord_line
        tip_chord = self.wing_segment.tip_airfoil.chord_line
        return LineSegment(root_chord.point(self.chordwise_pos_root *
                                            root_chord.length),
                           tip_chord.point(self.chordwise_pos_tip *
                                           tip_chord.length))

    @Attribute
    def projected_spar_lines(self):
        """ Projects the 'spar_line' onto the upper and lower surface of the
        wing segment. If the orientations of the projected lines are not in
        the same direction, one of the lines is reversed.

        :rtype: list[parapy.geom.occ.wire.Wire]
        """
        upper_crv = ProjectedCurve(self.spar_line,
                                   self.wing_segment.upper_surface,
                                   self.wing_segment.position.Vz)
        lower_crv = ProjectedCurve(self.spar_line,
                                   self.wing_segment.lower_surface,
                                   self.wing_segment.position.Vz_)

        if (np.sign(max(upper_crv.direction_vector,
                        key=abs)) !=
            np.sign(max(lower_crv.direction_vector,
                        key=abs))):
            return [upper_crv.reversed, lower_crv]
        else:
            return [upper_crv, lower_crv]

    @Attribute
    def full_length_web(self):
        return RuledSurface(*self.projected_spar_lines,
                            position=self.position)

    @Attribute
    def cutting_plane(self):
        return Plane(translate(self.position,
                               'y',
                               self.wing_segment.segment_span *
                               self.spanwise_pos_end),
                     self.wing_segment.position.Vy,
                     self.wing_segment.position.Vx)

    @Attribute
    def web(self):
        """ Make the web of the spar beam by ruling a surface between the
        two 'projected_spar_lines'. Afterwards, the web is cut off at the
        spanwise fraction 'spanwise_pos_end', to accommodate spars not
        running through the full length of the wing segment. Then the cut
        off surface at the tip of the wing segment is discarded based on its
        cog position lying most outboard.

        :rtype:
            parapy.geom.occ.ruling.RuledSurface | parapy.geom.occ.face.Face_
        """
        if self.spanwise_pos_end < 1:
            return min(
                SplitSurface(self.full_length_web, self.cutting_plane).faces,
                key=lambda f:
                    f.cog.distance(self.wing_segment.root_airfoil.position))
        else:
            return self.full_length_web

    @Attribute
    def offsets_root(self):
        """ Calculate the offset of the spar's flanges at the root, based on
        the supplied aspect ratio of the spar and its input profile.

        :rtype: list[float]
        """
        root_web_edge = min(
            self.full_length_web.edges,
            key=lambda e: e.cog.distance(self.wing_segment.root_airfoil.cog)
        )

        if self.profile == 'C':
            offsets = [self.aspect_ratio * root_web_edge.length, 0]
        elif self.profile == 'C_':
            offsets = [-self.aspect_ratio * root_web_edge.length, 0]
        else:  # if self.profile == 'I':
            offsets = [0.5 * self.aspect_ratio * root_web_edge.length,
                       -0.5 * self.aspect_ratio * root_web_edge.length]
        return offsets

    @Attribute
    def offsets_tip(self):
        """ Calculate the offset of the spar's flanges at the tip, based on
        the supplied aspect ratio of the spar and its input profile.

        :rtype: list[float]
        """
        tip_web_edge = min(
            self.full_length_web.edges,
            key=lambda e: e.cog.distance(self.wing_segment.tip_airfoil.cog)
        )

        if self.profile == 'C':
            offsets = [self.aspect_ratio * tip_web_edge.length,
                       0]
        elif self.profile == 'C_':
            offsets = [-self.aspect_ratio * tip_web_edge.length,
                       0]
        else:  # if self.profile == 'I':
            offsets = [0.5 * self.aspect_ratio * tip_web_edge.length,
                       -0.5 * self.aspect_ratio * tip_web_edge.length]
        return offsets

    @Attribute
    def web_offset_planes_root(self):
        """ Make the planes that, when intersected with the root airfoil,
        define the boundary points of the flanges at the root.

        :rtype: list[parapy.geom.occ.offset.OffsetPlane]
        """
        return [OffsetPlane(Plane(self.position, self.web.plane_normal,
                                  self.orientation.y),
                            offset if self.wing_segment.parent.is_starboard
                            else -offset)
                for offset in self.offsets_root]

    @Attribute
    def web_offset_planes_tip(self):
        """ Make the planes that, when intersected with the tip airfoil,
        define the boundary points of the flanges at the tip.

        :rtype: list[parapy.geom.occ.offset.OffsetPlane]
        """
        return [OffsetPlane(Plane(self.position, self.web.plane_normal,
                                  self.orientation.y),
                            offset if self.wing_segment.parent.is_starboard
                            else -offset)
                for offset in self.offsets_tip]

    @Attribute
    def flange_points_root(self):
        """ The points (on the root airfoil) that define the boundaries of the
        upper AND lower flange at the root airfoil.

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        points = []
        airfoil = self.wing_segment.root_airfoil
        for srf in self.web_offset_planes_root:
            intersections = airfoil.surface_intersections(srf)
            points += [intersection['point'] for intersection in intersections]
        return points

    @Attribute
    def flange_points_tip(self):
        """ The points (on the tip airfoil) that define the boundaries of the
        upper AND lower flange at the tip airfoil.

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        points = []
        airfoil = self.wing_segment.tip_airfoil
        for srf in self.web_offset_planes_tip:
            intersections = airfoil.surface_intersections(srf)
            points += [intersection['point'] for intersection in intersections]
        return points

    @Attribute
    def forward_flange_points(self):
        """ The points (on the airfoil upper AND lower surfaces) that define
        the boundaries of the upper AND lower flange at the root AND tip
        airfoils that lie most forward (upstream).

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        all_flange_points = self.flange_points_root + self.flange_points_tip
        tip_lower_half = self.wing_segment.tip_airfoil.lower_half
        root_lower_half = self.wing_segment.root_airfoil.lower_half
        tip_upper_half = self.wing_segment.tip_airfoil.upper_half
        root_upper_half = self.wing_segment.root_airfoil.upper_half

        tip_lower_points = min([point for point in all_flange_points if
                                tip_lower_half.is_point_inside(point)],
                               key=lambda pnt:
                               tip_lower_half.start.distance(pnt))

        tip_upper_points = min([point for point in all_flange_points if
                                tip_upper_half.is_point_inside(point)],
                               key=lambda pnt:
                               tip_upper_half.start.distance(pnt))

        root_lower_points = min([point for point in all_flange_points if
                                 root_lower_half.is_point_inside(point)],
                                key=lambda pnt:
                                root_lower_half.start.distance(pnt))

        root_upper_points = min([point for point in all_flange_points if
                                 root_upper_half.is_point_inside(point)],
                                key=lambda pnt:
                                root_upper_half.start.distance(pnt))

        return [tip_lower_points, tip_upper_points,
                root_lower_points, root_upper_points]

    @Attribute
    def rear_flange_points(self):
        """ The points (on the airfoil upper AND lower surfaces) that define
        the boundaries of the upper AND lower flange at the root AND tip
        airfoils that lie most rearward (downstream).

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        all_flange_points = self.flange_points_root + self.flange_points_tip
        tip_lower_half = self.wing_segment.tip_airfoil.lower_half
        root_lower_half = self.wing_segment.root_airfoil.lower_half
        tip_upper_half = self.wing_segment.tip_airfoil.upper_half
        root_upper_half = self.wing_segment.root_airfoil.upper_half

        tip_lower_points = max([point for point in all_flange_points if
                                tip_lower_half.is_point_inside(point)],
                               key=lambda pnt:
                               tip_lower_half.start.distance(pnt))

        tip_upper_points = max([point for point in all_flange_points if
                                tip_upper_half.is_point_inside(point)],
                               key=lambda pnt:
                               tip_upper_half.start.distance(pnt))

        root_lower_points = max([point for point in all_flange_points if
                                 root_lower_half.is_point_inside(point)],
                                key=lambda pnt:
                                root_lower_half.start.distance(pnt))

        root_upper_points = max([point for point in all_flange_points if
                                 root_upper_half.is_point_inside(point)],
                                key=lambda pnt:
                                root_upper_half.start.distance(pnt))

        return [tip_lower_points, tip_upper_points,
                root_lower_points, root_upper_points]

    @Attribute
    def flange_planes(self):
        """ Returns two flange planes, defined by three points out of the
        four respective forward and rearward lying points.

        :return:
        """
        return [Plane3P(*self.forward_flange_points[0:3]),
                Plane3P(*self.rear_flange_points[0:3])]

    @Attribute
    def flanges(self):
        """ Returns a list of (two) flanges of the spar, found as an
        intersectino of the airfoil surfaces, split at the previously
        defined flange planes. The flanges running through the entire span
        of the wing are then cut at  spanwise_pos_end', a spanwise fraction
        of the segment wing span. The most outboard part of this cut surface is
        then discarded based on its cog lying more outboard.

        :rtype: list[parapy.geom.occ.face.Face_]
        """
        airfoil_surfaces = [self.wing_segment.upper_surface,
                            self.wing_segment.lower_surface]
        split_surfaces = [SplitSurface(surf, self.flange_planes)
                          for surf in airfoil_surfaces]
        full_length_flanges = [
            max(split_surf.faces, key=lambda f: len(f.neighbours))
            for split_surf in split_surfaces
        ]
        cutting_plane = Plane(translate(self.position,
                                        'y',
                                        self.wing_segment.segment_span *
                                        self.spanwise_pos_end),
                              self.wing_segment.position.Vy,
                              self.wing_segment.position.Vx)
        return [
            min(SplitSurface(full_length_flange, cutting_plane).faces,
                key=lambda f:
                f.cog.distance(self.wing_segment.root_airfoil.position))
            for full_length_flange in full_length_flanges]

    @Attribute
    def web_plane(self):
        return Plane(self.position, self.web.plane_normal,
                     self.projected_spar_lines[0].direction_vector)

    @Attribute
    def length(self):
        sorted_edges = sorted(
            self.web.edges,
            key=lambda e:
            e.midpoint.distance(self.wing_segment.root_airfoil.position)
        )
        return sorted_edges[1].length

    @Attribute
    def span(self):
        return abs(self.length * np.cos(self.orientation.Vy.angle(
            self.wing_segment.orientation.Vy
        )))


class FusedSpar(FusedShell):

    segments = Input()

    __initargs__ = ["segments"]

    # Optional inputs
    color = Input('cyan')

    @Attribute
    def segments_is_iterable(self):
        msg = "Input {} to 'segments' is not a 'SparSegment' or an iterable " \
              "of SparSegments, as required."
        if hasattr(self.segments, '__iter__'):
            return True
        else:
            assert isinstance(self.segments, SparSegment), \
                   msg.format(self.segments)
            return False

    @Attribute
    def shape_in(self):
        if self.segments_is_iterable:
            return self.segments[0]
        else:
            return self.segments

    @Attribute
    def tool(self):
        if self.segments_is_iterable and len(self.segments) > 1:
            return self.segments[1:]
        else:
            return self.segments

    @Attribute
    def position(self):
        if self.segments_is_iterable:
            return self.segments[0].position
        else:
            return self.segments.position

    @Attribute
    def span(self):
        if self.segments_is_iterable:
            return sum(spar_segment.span for spar_segment in self.segments)
        else:
            return self.segments.span

    @Attribute
    def spar_stations(self):
        if self.segments_is_iterable:
            return [spar_segment.position for spar_segment in self.segments] \
                    + [self.segments[-1].web.point(1., 0.5)]
        else:
            return [self.spar_segment.position,
                    self.spar_segment.web.point(1., 0.5)]

    def point(self, y_over_b_spar):
        # TODO check whether error in this function depends on wrong (u, v)
        #  parameter representation, or inherent function error.

        msg = "The value of parameter 'y_over_b_spar' should range " \
              "between 0 and 1. Value {} is invalid."
        assert 0 <= y_over_b_spar <= 1, msg.format(y_over_b_spar)

        if not self.segments_is_iterable:
            return self.segments.web.point(y_over_b_spar, 0)
        else:
            point_in_section = [
                lower.y <= y_over_b_spar * self.span < upper.y
                for lower, upper in zip(self.spar_stations[:-1],
                                        self.spar_stations[1:])
            ]

            if True in point_in_section:
                segment_idx = point_in_section.index(True)
                point_segment = self.segments[segment_idx]
            else:
                segment_idx = -1
                point_segment = self.segments[segment_idx]

            u_param = (y_over_b_spar * self.span -
                       sum(seg.span for seg in self.segments[:segment_idx]
                           )) / point_segment.span

            return point_segment.web.point(u_param, 0.5)


if __name__ == '__main__':
    from parapy.gui import display
    obj = SparSegment()
    display(obj)
