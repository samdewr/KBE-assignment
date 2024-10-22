import numpy as np
from parapy.core import *
from parapy.geom import *


class Engine(FusedShell):
    """ A simple engine model that can be used to estimate the location of
    the engines' centres of gravity.
    """

    __initargs__ = ['thrust', 'specific_fuel_consumption', 'diameter_inlet',
                    'diameter_outlet', 'diameter_part2', 'length_cone1',
                    'length_cone2']

    diameter_inlet = Input(validator=val.is_positive)
    diameter_outlet = Input(validator=val.is_positive)
    diameter_part2 = Input(validator=val.is_positive)
    length_cone1 = Input(validator=val.is_positive)
    length_cone2 = Input(validator=val.is_positive)
    thrust = Input(validator=val.is_positive)
    specific_fuel_consumption = Input(validator=val.is_positive)

    # Optional arguments
    color = Input('cyan')
    transparency = Input(0.5)

    @Attribute
    def cog(self):
        return translate(self.location,
                         self.parent.parent.position.Vx,
                         0.45 * (self.length_cone2 + self.length_cone1))

    @Attribute
    def first_cone_list(self):
        list1 = np.arange(1.0, 1.2, 0.1)
        list2 = np.arange(list1[-1], 1., -00.1)
        list3 = np.append(list1, list2)
        return list3

    @Attribute
    def spacing_1(self):
        return self.length_cone1 / (len(self.first_cone_list) - 1)

    @Part(in_tree=False)
    def cone_1(self):
        return Circle(
            quantify=len(self.first_cone_list),
            position=rotate90(translate(self.position, 'x',
                                        child.index * self.spacing_1), 'y'),
            radius=self.diameter_inlet / 2. * self.first_cone_list[child.index]
        )

    @Attribute
    def surface_cone_1(self):
        return LoftedSurface(profiles=self.cone_1)

    @Attribute
    def second_cone_list(self):
        list1 = np.arange(1.0, 1.01, 0.02)
        list2 = np.arange(list1[-1], 0.75, -0.1)
        list3 = np.append(list1, list2)
        return list3

    @Attribute
    def spacing_2(self):
        return self.length_cone2 / (len(self.second_cone_list) - 1)

    @Part(in_tree=False)
    def cone_2(self):
        return Circle(quantify=len(self.second_cone_list),
                      position=translate(self.cone_1[-1].position,
                                         'z',
                                         child.index * self.spacing_2),
                      radius=self.diameter_outlet / 2. * self.second_cone_list[
                          child.index])

    @Attribute
    def surface_cone_2(self):
        return LoftedSurface(profiles=self.cone_2)

    @Attribute
    def shape_in(self):
        return self.surface_cone_1

    @Attribute
    def tool(self):
        return [self.surface_cone_2]

    @Attribute
    def length(self):
        return self.length_cone1 + self.length_cone2

    @Attribute
    def mass(self):
        return self.parent.parent.MTOM * 0.097 / 4.


if __name__ == '__main__':
    from parapy.gui import display

    obj = Engine(diameter_inlet=2.0, diameter_outlet=1.0,
                 diameter_part2=0.5, length_cone1=2.0, length_cone2=1.0,
                 thrust=50000., specific_fuel_consumption=1.79e-5)
    display(obj)
