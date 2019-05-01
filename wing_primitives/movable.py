from parapy.core import *
from parapy.geom import *

import math


class Movable(RotatedShape, SewnShell):
    # Q: How do I model the movable without a gap showing up upon rotation
    #  of the movable.
    # Q: Is the modelling of the movable explicitly even necessary or does
    #  the AVL module not need such an input.
    wing = Input()

    spanwise_start = Input(validator=val.Between(0, 1))
    spanwise_end = Input(validator=val.Between(0, 1))
    hingeline_start = Input(validator=val.Between(0, 1))
    deflection = Input(validator=val.is_number)

    __initargs__ = ['wing', 'spanwise_start', 'spanwise_end',
                    'hingeline_start', 'deflection']

    # Optional inputs
    color = Input('orange')
    transparency = Input(0.5)
    symmetric = Input(True, validator=lambda x: isinstance(x, bool))
    name = Input('movable')

    @Input
    def label(self):
        return self.name

    @Attribute
    def orientation(self):
        return rotate(self.wing.orientation, self.wing.orientation.Vy,
                      self.angle, deg=True)

    @Attribute
    def built_from(self):
        return SewnShell([self.upper_surface, self.lower_surface])

    @Attribute
    def shape_in(self):
        return self.built_from

    @Attribute
    def rotation_point(self):
        return self.chordwise_plane.position

    @Attribute
    def vector(self):
        vector = self.chordwise_plane.binormal
        return vector if self.wing.is_starboard and self.symmetric else -vector

    @Attribute
    def angle(self):
        return math.radians(self.deflection)

    @Attribute
    def upper_surface(self):
        upper_split_surface = SplitSurface(self.wing_segment.upper_surface,
                                           self.spanwise_planes +
                                           [self.chordwise_plane])

        upper_movable_surface = max(upper_split_surface.faces,
                                    key=lambda m: (len(m.neighbours), m.cog.x))
        return upper_movable_surface

    @Attribute
    def lower_surface(self):
        lower_split_surface = SplitSurface(self.wing_segment.lower_surface,
                                           self.spanwise_planes +
                                           [self.chordwise_plane])

        lower_movable_surface = max(lower_split_surface.faces,
                                    key=lambda m: (len(m.neighbours), m.cog.x))
        return lower_movable_surface

    @Attribute
    def bisectors(self):

        upper_line_root = min(self.upper_surface.edges, key=lambda e: e.cog.y)
        lower_line_root = min(self.lower_surface.edges, key=lambda e: e.cog.y)
        upper_line_tip = max(self.upper_surface.edges, key=lambda e: e.cog.y)
        lower_line_tip = max(self.lower_surface.edges, key=lambda e: e.cog.y)

        angle_root = upper_line_root.direction_vector.angle(
            lower_line_root.direction_vector)
        angle_tip = upper_line_tip.direction_vector.angle(
            lower_line_tip.direction_vector)

        bisector_root = Line(upper_line_root.start, rotate(
            lower_line_root.direction_vector, self.chordwise_plane.binormal,
            angle_root / 2.))
        bisector_tip = Line(upper_line_tip.start, rotate(
            lower_line_tip.direction_vector, self.chordwise_plane.binormal,
            angle_tip / 2.))

        return [bisector_root, bisector_tip]

    # @Attribute(in_tree=True)
    # def nose(self):
    #     upper_edge = min(self.upper_surface.edges, key=lambda e: e.cog.x)
    #     lower_edge = min(self.lower_surface.edges, key=lambda e: e.cog.x)
    #
    #     upper_line_root = min(self.upper_surface.edges, key=lambda e: e.cog.y)
    #     lower_line_root = min(self.lower_surface.edges, key=lambda e: e.cog.y)
    #     upper_line_tip = max(self.upper_surface.edges, key=lambda e: e.cog.y)
    #     lower_line_tip = max(self.lower_surface.edges, key=lambda e: e.cog.y)
    #
    #     upper_start = min([upper_edge.start, upper_edge.end],
    #                       key=lambda p: p.y)
    #     upper_end = max([upper_edge.start, upper_edge.end], key=lambda p: p.y)
    #     lower_start = min([lower_edge.start, lower_edge.end],
    #                       key=lambda p: p.y)
    #     lower_end = max([lower_edge.start, lower_edge.end], key=lambda p: p.y)
    #
    #     delta = -1e-3
    #
    #     midpnt1 = upper_start.midpoint(lower_start)
    #     print upper_line_root.direction_vector.dot(Arc3P(
    #             upper_start, midpnt1, lower_start).tangent1)
    #     while not upper_line_root.direction_vector.is_parallel(Arc3P(
    #             upper_start, midpnt1, lower_start).tangent1, tol=1e-4):
    #         midpnt1 = translate(midpnt1, self.bisectors[0].direction, delta)
    #         print '------------------------'
    #         print midpnt1
    #         print upper_line_root.direction_vector.angle(
    #             Arc3P(midpnt1, upper_start, lower_start).tangent1
    #         )
    #
    #     midpnt2 = upper_end.midpoint(lower_end)
    #
    #     while not upper_line_tip.direction_vector.is_parallel(Arc3P(
    #             upper_end, midpnt2, lower_end).tangent1, tol=1e-4):
    #         midpnt2 = translate(midpnt2, self.bisectors[1].direction, delta)
    #
    #     arc1 = Arc3P(upper_start, midpnt1, lower_start)
    #     arc2 = Arc3P(upper_end, midpnt2, lower_end)
    #     return RuledSurface(arc1, arc2)

    @Attribute
    def wing_segment(self):
        spanwise_stations = [0] + self.wing.spanwise_positions + [1]
        start_segment = [lower <= self.spanwise_start < upper for
                         lower, upper in zip(spanwise_stations[:-1],
                                             spanwise_stations[1:])
                         ].index(True)
        end_segment = [lower <= self.spanwise_end < upper for
                       lower, upper in zip(spanwise_stations[:-1],
                                           spanwise_stations[1:])
                       ].index(True)
        if start_segment != end_segment:
            msg = 'The start and end segments of {} are not in the same ' \
                  'wing segments.'.format(self)
            raise Exception(msg)
        else:
            return self.wing.segments[start_segment]

    @Attribute
    def spanwise_planes(self):
        return [Plane(translate(self.wing.position, self.wing.orientation.Vy,
                                self.wing.semi_span * self.spanwise_start),
                      self.wing.orientation.Vy, self.wing.orientation.Vx),
                Plane(translate(self.wing.position, self.wing.orientation.Vy,
                                self.wing.semi_span * self.spanwise_end),
                      self.wing.orientation.Vy, self.wing.orientation.Vx)]

    @Attribute
    def chordwise_plane(self):

        root_airfoil = self.wing_segment.root_airfoil
        tip_airfoil = self.wing_segment.tip_airfoil
        u_root_max = root_airfoil.chord_line.u_max
        u_tip_max = tip_airfoil.chord_line.u_max

        pt_root = root_airfoil.chord_line.point(self.hingeline_start *
                                                u_root_max)
        pt_tip = tip_airfoil.chord_line.point(self.hingeline_start * u_tip_max)

        binormal = pt_tip - pt_root
        normal = binormal.cross(self.wing.orientation.Vz)
        return Plane(pt_root, normal, binormal)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Movable()
    display(obj)
