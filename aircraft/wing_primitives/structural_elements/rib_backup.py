import numpy as np
from parapy.core import *
from parapy.geom import *


class Rib(GeomBase):

    wing = Input()

    rib_spanwise_reference_spar_idx = Input(validator=lambda x:
                                            isinstance(x, int))
    rib_spanwise_position = Input(validator=val.Range(0, 1))
    rib_orientation_reference_spar_idx = Input(validator=lambda x:
                                               isinstance(x, int))
    rib_orientation_angle = Input(
        validator=lambda x: isinstance(x, (int, float)) or
                            (x == 'flight_direction' or x == 'normal')
    )

    __initargs__ = ['wing', 'rib_spanwise_reference_spar_idx',
                    'rib_spanwise_position',
                    'rib_orientation_reference_spar_idx',
                    'rib_orientation_angle', 'island']

    # Tolerance to set the rib positioning properly. If tolerance not set,
    # differences in the order of 1e-16 screw up the 'greater than'-clause.
    tolerance = 1e-07

    # Optional inputs
    color = Input('black')

    @Attribute
    def position(self):
        # Q: With this routine, errors in the order of machine precision
        #  screw up the > clause, for example when assigning a rib at
        #  relative longitudinal position 1. How do I mitigate this?
        plane_spanwise_position = self.spanwise_reference_spar.span * \
                                  self.rib_spanwise_position
        # print plane_spanwise_position
        for spar_i, spar in enumerate(self.spanwise_reference_spar.segments):
            if plane_spanwise_position > spar.span:
                plane_spanwise_position -= spar.span
            else:
                break
            # print plane_spanwise_position
        span_ref_spar_section = self.spanwise_reference_spar.segments[spar_i]
        u_max = self.spanwise_reference_spar.segments[spar_i].web.u_max
        return self.spanwise_reference_spar.segments[spar_i].web.point(
            plane_spanwise_position / span_ref_spar_section.span * u_max, 0.
        )

    @Attribute
    def orientation(self):
        orientation_spar_total_span = sum(
            spar.span for spar in self.orientation_reference_spar.segments
        )

        plane_spanwise_position = self.position.y
        for spar_i, spar in enumerate(self
                                      .orientation_reference_spar.segments):
            if self.position.y > orientation_spar_total_span:
                orientation_ref_spar = self.orientation_reference_spar \
                    .segments[-1]
                break
            elif plane_spanwise_position > spar.span:
                plane_spanwise_position -= spar.span
            else:
                orientation_ref_spar = self.orientation_reference_spar \
                    .segments[spar_i]
                break
        if isinstance(self.rib_orientation_angle, (float, int)):
            rib_orientation = rotate(orientation_ref_spar.orientation,
                                     self.wing.orientation.Vz,
                                     self.rib_orientation_angle, deg=True)
        elif self.rib_orientation_angle.lower() == 'flight_direction':
            rib_orientation = orientation_ref_spar.orientation.align(
                'y', self.wing.position.Vx_
            )
        else:
            rib_orientation = rotate90(orientation_ref_spar.orientation,
                                       self.wing.orientation.Vz)
        return rib_orientation

    @Attribute
    def spanwise_reference_spar(self):
        """ Returns the spar that is used as a reference for the longitudinal
        positioning of the rib.

        :rtype: spar.Spar
        """
        return self.wing.spars[self.rib_spanwise_reference_spar_idx]

    @Attribute
    def orientation_reference_spar(self):
        """ Returns the spar that is used as a reference for the orientation
        of the rib.

        :rtype: spar.Spar
        """
        return self.wing.spars[self.rib_orientation_reference_spar_idx]

    @Attribute
    def rib_plane(self):
        """ Returns the plane, positioned at the required longitudinal
        position with respect to its longitudinal position reference spar,
        and with a rib orientation angle, with respect to the orientation of
        the rib orientation reference spar.

        :rtype: parapy.geom.occ.surface.Plane
        """
        # Q: Check why (u, v) parameter of spar.web runs from 0 to 1 over
        #  the entire length of the uncut spar.
        return Plane(self.position, self.orientation.Vx, self.orientation.Vz)

    @Attribute
    def airfoil_shell(self):
        return CommonShell(self.wing.closed_solid, self.rib_plane)

    @Attribute
    def planes(self):
        sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)

        for spar in sorted_spars[0].segments:
            if IntersectedShapes(spar.web, self.rib_plane).edges:
                front_cutter = spar.web_plane

        for spar in sorted_spars[-1].segments:
            if IntersectedShapes(spar.web, self.rib_plane).edges:
                rear_cutter = spar.web_plane
        return [front_cutter, rear_cutter]

    @Attribute
    def split_rib(self):
        return SplitSurface(self.airfoil_shell, self.planes)


class WingBoxRib(Rib, CommonShell):

    @Attribute
    def ref_point(self):
        rib = max(self.split_rib.faces, key=lambda f: len(f.neighbours))
        return rib.cog

    @Attribute
    def tool(self):
        return [HalfSpaceSolid(pln, self.ref_point) for pln in self.planes]

    @Attribute
    def shape_in(self):
        return self.airfoil_shell

    # Inputs for the RuledSurface class
    # @Attribute
    # def curve1(self):
    #     """ The upper line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_upper_line
    #
    # @Attribute
    # def curve2(self):
    #     """ The lower line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_lower_line
    #
    # @Attribute
    # def rib_upper_line(self):
    #     """ Returns the upper line that defines the WingBoxRib geometry,
    #     found by intersecting the upper wing surface with the planes through
    #     front and rear spars. The required upper line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the most neighbours.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     upper_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.upper_surface).edges
    #     )
    #
    #     sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in sorted_spars[0].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             front_cutter = spar.web_plane
    #
    #     for spar in sorted_spars[-1].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             rear_cutter = spar.web_plane
    #
    #     upper_rib_line = max(SplitCurve(upper_line,
    #                                     [front_cutter, rear_cutter]).edges,
    #                          key=lambda e: len(e.neighbours))
    #     return upper_rib_line
    #
    # @Attribute
    # def rib_lower_line(self):
    #     """ Returns the lower line that defines the WingBoxRib geometry,
    #     found by intersecting the lower wing surface with the planes through
    #     front and rear spars. The required lower line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the most neighbours.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     lower_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.lower_surface).edges
    #     )
    #
    #     sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in sorted_spars[0].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             front_cutter = spar.web_plane
    #
    #     for spar in sorted_spars[-1].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             rear_cutter = spar.web_plane
    #
    #     lower_rib_line = max(SplitCurve(lower_line,
    #                                     [front_cutter, rear_cutter]).edges,
    #                          key=lambda e: len(e.neighbours))
    #     if (np.sign(max(lower_rib_line.direction_vector,
    #                     key=abs)) !=
    #         np.sign(max(self.rib_upper_line.direction_vector,
    #                     key=abs))):
    #         return lower_rib_line.reverse
    #     else:
    #         return lower_rib_line
    #
    # @Attribute
    # def tools(self):
    #     sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in sorted_spars[0].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             front_cutter = spar.web_plane
    #
    #     for spar in sorted_spars[-1].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             rear_cutter = spar.web_plane
    #     return [front_cutter, rear_cutter]
    #
    # @Attribute
    # def split_rib(self):
    #     return SplitSurface(self.airfoil_shell, self.tools)
    #
    # @Attribute
    # def rib_web(self):
    #     """ Returns the web of the rib (currently the same as the rib
    #     itself), as a product of a ruling between the upper and lines of the
    #     rib.
    #
    #     :rtype: parapy.geom.occ.ruling.RuledSurface
    #     """
    #     return RuledSurface(self.rib_upper_line, self.rib_lower_line)


class TrailingEdgeRiblet(Rib, CommonShell):

    @Attribute
    def ref_point(self):
        rib = max(self.split_rib.faces, key=lambda f: f.cog.x)
        return rib.cog

    @Attribute
    def tool(self):
        return HalfSpaceSolid(self.planes[-1], self.ref_point)

    @Attribute
    def shape_in(self):
        return self.airfoil_shell

    # # Inputs for the RuledSurface class
    # @Attribute
    # def curve1(self):
    #     """ The upper line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_upper_line
    #
    # @Attribute
    # def curve2(self):
    #     """ The lower line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_lower_line
    #
    # @Attribute
    # def rib_upper_line(self):
    #     """ Returns the upper line that defines the TrailingEdgeRiblet
    #     geometry, found by intersecting the upper wing surface with the plane
    #     through the rear spar. The required upper line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the rearmost centre of gravity.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     upper_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.upper_surface).edges
    #     )
    #
    #     sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in sorted_spars[-1].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             rear_cutter = spar.web_plane
    #
    #     upper_rib_line = max(SplitCurve(upper_line, rear_cutter).edges,
    #                          key=lambda e: e.cog.x)
    #
    #     return upper_rib_line
    #
    # @Attribute
    # def rib_lower_line(self):
    #     """ Returns the lower line that defines the TrailingEdgeRiblet
    #     geometry, found by intersecting the lower wing surface with the plane
    #     through the rear spar. The required lower line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the rearmost centre of gravity.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     lower_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.lower_surface).edges
    #     )
    #
    #     sorted_spars = sorted(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in sorted_spars[-1].segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             rear_cutter = spar.web_plane
    #
    #     lower_rib_line = max(SplitCurve(lower_line, rear_cutter).edges,
    #                          key=lambda e: e.cog.x)
    #
    #     if (np.sign(max(lower_rib_line.direction_vector,
    #                     key=abs)) !=
    #         np.sign(max(self.rib_upper_line.direction_vector,
    #                     key=abs))):
    #         return lower_rib_line.reverse
    #     else:
    #         return lower_rib_line
    #
    # @Attribute(in_tree=True)
    # def rib_web_test(self):
    #     return CommonShell(self.wing.closed_solid, self.rib_plane)
    #
    # @Attribute
    # def rib_web(self):
    #     """ Returns the web of the rib (currently the same as the rib
    #     itself), as a product of a ruling between the upper and lines of the
    #     rib.
    #
    #     :rtype: parapy.geom.occ.ruling.RuledSurface
    #     """
    #     return RuledSurface(self.rib_upper_line, self.rib_lower_line)


class LeadingEdgeRiblet(Rib, CommonShell):

    @Attribute
    def ref_point(self):
        rib = min(self.split_rib.faces, key=lambda f: f.cog.x)
        return rib.cog

    @Attribute
    def tool(self):
        return HalfSpaceSolid(self.planes[0], self.ref_point)

    @Attribute
    def shape_in(self):
        return self.airfoil_shell

    # # Inputs for the RuledSurface class
    # @Attribute
    # def curve1(self):
    #     """ The upper line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_upper_line
    #
    # @Attribute
    # def curve2(self):
    #     """ The lower line of the wing (segment) surface that defines the
    #     rib geometry. Serves as an input to the RuledSurface class.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     return self.rib_lower_line
    #
    # @Attribute
    # def rib_upper_line(self):
    #     """ Returns the upper line that defines the LeadingEdgeRiblet
    #     geometry, found by intersecting the upper wing surface with the plane
    #     through the front spar. The required upper line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the most forward centre of gravity.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     upper_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.upper_surface).edges
    #     )
    #
    #     front_spar = min(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in front_spar.segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             front_cutter = spar.web_plane
    #
    #     upper_rib_line = min(SplitCurve(upper_line, front_cutter).edges,
    #                          key=lambda e: e.cog.x)
    #
    #     return upper_rib_line
    #
    # @Attribute
    # def rib_lower_line(self):
    #     """ Returns the lower line that defines the LeadingEdgeRiblet
    #     geometry, found by intersecting the lower wing surface with the plane
    #     through the front spar. The required lower line is then
    #     selected from the set of segmented lines by looking for the line
    #     with the most forward centre of gravity.
    #
    #     :rtype: parapy.geom.occ.edge.Edge_
    #     """
    #     lower_line = ComposedCurve(
    #         IntersectedShapes(self.rib_plane, self.wing.lower_surface).edges
    #     )
    #
    #     front_spar = min(self.wing.spars, key=lambda s: s.position.x)
    #
    #     for spar in front_spar.segments:
    #         if IntersectedShapes(spar.web, self.rib_plane).edges:
    #             front_cutter = spar.web_plane
    #
    #     lower_rib_line = min(SplitCurve(lower_line, front_cutter).edges,
    #                          key=lambda e: e.cog.x)
    #
    #     if (np.sign(max(lower_rib_line.direction_vector, key=abs)) !=
    #             np.sign(max(self.rib_upper_line.direction_vector, key=abs))):
    #         return lower_rib_line.reverse
    #     else:
    #         return lower_rib_line
    #
    # @Attribute
    # def rib_web(self):
    #     """ Returns the web of the rib (currently the same as the rib
    #     itself), as a product of a ruling between the upper and lines of the
    #     rib.
    #
    #     :rtype: parapy.geom.occ.ruling.RuledSurface
    #     """
    #     return RuledSurface(self.rib_upper_line, self.rib_lower_line)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Rib()
    display(obj)
