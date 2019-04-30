from __future__ import division
from math import radians, tan
from parapy.core import Base, Part, child, Attribute, Input
from kbeutils.avl import (Interface, Case, Configuration, Section, NacaAirfoil,
                          Surface, Spacing, Control, Parameter)

class AVLAnalysis(Base):

    @Part
    def aircraft(self):
        return AircraftConfiguration(root_chord=6.0,
                                     taper_ratio=0.4,
                                     span=42,
                                     sweep_angle=24.0,
                                     name="Example aircraft")

    @Part
    def interface(self):
        return AVLInterface(configuration=self.aircraft,
                            case_settings=[('fixed_aoa', {'alpha': 5}),
                                           ('flap_cl',
                                            {'alpha': Parameter(name='alpha',
                                                                value=1.2,
                                                                constraint='CL'),
                                             'flap': 15})])


class AVLInterface(Interface):

    case_settings = Input()

    # overridden slot from Interface superclass
    @Part
    def cases(self):
        return Case(quantify=len(self.case_settings),
                    name=self.case_settings[child.index][0],
                    settings=self.case_settings[child.index][1])


class AircraftConfiguration(Configuration):

    root_chord = Input()
    taper_ratio = Input()
    span = Input()
    sweep_angle = Input()
    naca_airfoil = Input('2412')

    flap_hinge = Input(0.75)

    @Part
    def airfoil(self):
        return NacaAirfoil(self.naca_airfoil)

    @Part
    def root_section(self):
        return Section(chord=self.root_chord,
                       airfoil=self.airfoil,
                       controls=[self.flap])

    @Part
    def tip_section(self):
        return Section(chord=self.root_chord * self.taper_ratio,
                       airfoil=self.airfoil,
                       position=self.root_section.position.translate(
                           'x', self.span / 2 * tan(radians(self.sweep_angle)),
                           'y', self.span / 2),
                       controls=[self.flap])

    @Part
    def flap(self):
        return Control(name='flap',
                       gain=1,
                       x_hinge=self.flap_hinge,
                       dupplicate_sign=1)

    @Attribute
    def mac(self):
        t = self.taper_ratio
        return (2 / 3) * self.root_chord * (1 + t + t ** 2) / (1 + t)

    @Part
    def wing_surface(self):
        return Surface(name="Wing",
                       n_chordwise=8,
                       chord_spacing=Spacing.cosine,
                       n_spanwise=20,
                       span_spacing=Spacing.cosine,
                       y_duplicate=0.0,
                       sections=[self.root_section, self.tip_section])


    # overridden slots from Configuration superclass
    @Attribute
    def reference_point(self):
        return self.root_section.position.translate('x', self.root_chord / 4)

    @Attribute
    def reference_chord(self):
        return self.mac

    @Attribute
    def reference_span(self):
        return self.span

    @Attribute
    def reference_area(self):
        return self.wing_surface.area * 2

    @Attribute
    def surfaces(self):
        return [self.wing_surface]


if __name__ == '__main__':
    from parapy.gui import display

    analysis = AVLAnalysis()
    display(analysis)
