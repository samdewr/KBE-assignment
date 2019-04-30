from parapy.core import *
from parapy.geom import *

import matplotlib.pyplot as plt

import numpy as np
from math import sqrt, tan, radians, pi, cos, radians


# Typical cg range 25 to 35 percent of MAC


class ScissorPlot(Base):
    """ This class calculates the scissor plot from the various inputs from
    the other classes. The purpose of this class is to size the tail from
    the a certain c.g. range and a position from the tail and the main wing.
    From that area other aspects can be calculated.
    """

    # Airfoil Specifics

    cl_0 = Input(.5)  # lift at zero angle of attack.
    cm0_airfoil = Input(0.)  # zero pitching moment

    # Wing Specifics

    span = Input(20., validator=val.is_positive)  # span of the wing.
    aspect_ratio = Input(8.)  # The aspect ratio of th wing.
    wing_area = Input(30.)  # Wing area
    wing_area_net = Input(38.)  # Wing area- the area within the fuselage

    l_h = Input(5.)  # horizontal distance between te tail and the c.g.
    z_h = Input(1.0)  # Vertical distance between c.g. and the tail
    sweep_angle_025c = Input(20.)  # sweep angle at quarter chord
    cl_alpha_wing = Input(2 * pi)  # Lift curve coefficient.
    cl_alpha_horizontal = Input(2 * pi)  # Lift curve of the tail
    MAC = Input(3.)  # Mean aerodynamic chord
    taper_ratio = Input(0.5)  # Taper ratio of the main wing.

    # engine inputs

    width_nacelle = Input(1.2)  # Width of the nacelle
    distance_nacelle_mac = Input(2.2)  # Distance of the nacelle in front of
    # the main wing.

    # Other Inputs

    length_fuselage = Input(20.)  # Length of the fuselage
    diameter_fuselage = Input(5.)  # needed for stabiliser

    l_nose_LE = Input(8.)  # Distance between nose and the leading edge of the
    # wing
    tail_type = Input('T-Tail', validator=val.is_string)  # Input depending
    # of what tail configuration is used.

    forward_cg = Input(validator=val.is_between(0, 1))  # Forward position of
    # the c.g. as fraction of mac.
    aft_cg = Input(validator=val.is_between(0, 1))  # Aft position of the c.g.

    # as fraction of mac.

    # Stability part of the scissor plot

    @Attribute
    def Vh_V_ratio(self):
        """ Calculates the ratio between the velocities of the main wing and
        the horizontal tailplane. The choice is between Conventional,
        Mid and T Tail configuration

                :rtype: float
        """
        if self.tail_type == 'T-Tail':
            return sqrt(1)
        elif self.tail_type == 'Mid-Tail':
            return sqrt(0.95)
        elif self.tail_type == 'Conventional-Tail':
            return sqrt(0.85)

    @Attribute
    def cl_alpha_a_h(self):
        """ Calculates the Lift curve coefficient of the fuselage wing body.
        This is the aircraft with fuselage and wing without horizontal
        tailplane.
                        :rtype: float
                        """
        value = self.cl_alpha_wing * (
                1 + 2.15 * self.diameter_fuselage / self.span) \
                * self.wing_area_net / self.wing_area + pi / 2. * \
                self.diameter_fuselage ** 2 \
                / self.wing_area
        return value

    @Attribute
    def downwash_gradient(self):
        """ Calculates the downwash gradient using a semi-emperical method.

                :rtype: float
        """

        r = self.l_h / (self.span / 2.)
        m_tv = self.z_h / (self.span / 2.)
        k_e_lambda = (0.1124 + 0.1265 * radians(
            self.sweep_angle_025c) + 0.1766 * (radians(
            self.sweep_angle_025c)) ** 2) / r ** 2 + 0.1024 / r + 2
        k_e_0 = 0.1124 / r ** 2 + 0.1024 / r + 2
        first = (r / (r ** 2 + m_tv ** 2)) * 0.4876 / (
            sqrt(r ** 2 + 0.6319 + m_tv ** 2))
        second = (1 + (
                r ** 2 / (r ** 2 + 0.7915 + 5.0734 * m_tv ** 2)) ** 0.3113) \
                 * (1 - sqrt(m_tv ** 2 / (1 + m_tv ** 2)))
        return k_e_lambda / k_e_0 * (first + second) * self.cl_alpha_wing / \
               (pi * self.aspect_ratio)

    @Attribute
    def x_ac(self):
        """ Calculates the position of the aerodynamic centre with respect
        to the position of the MAC. The contributions are the engines,
        the wing and the fuselage.

                :rtype: float
                """
        x_ac_engines = 2 * -4.0 * self.width_nacelle ** 2 * \
                       self.distance_nacelle_mac / \
                       (self.wing_area * self.MAC * self.cl_alpha_a_h)
        x_ac_wing = 0.25
        x_ac_rest_1 = -1.8 / self.cl_alpha_a_h * self.diameter_fuselage ** 2 \
                      * self.l_nose_LE / (self.wing_area * self.MAC)
        x_ac_rest_2 = 0.273 / (1 + self.taper_ratio) * (
                self.wing_area / self.span) * self.diameter_fuselage * (
                              self.span - self.diameter_fuselage) / \
                      (self.MAC ** 2 *
                       (self.span + 2.15 * self.diameter_fuselage)) \
                      * tan(radians(self.sweep_angle_025c))
        return x_ac_wing + x_ac_rest_1 + x_ac_rest_2 + x_ac_engines

    @Attribute
    def cm_ac(self):
        """ The moment coefficient around the aerodynamic centre is
        calculated. This is used for the controllability curve of the aircraft.
                :rtype: float
                """
        cm_ac_w = self.cm0_airfoil * (self.aspect_ratio * (cos(radians(
            self.sweep_angle_025c))) ** 2 / (self.aspect_ratio + 2 *
                                             cos(radians(
                                                 self.sweep_angle_025c))))
        cm_ac_engines = -0.05
        cm_ac_fuselage = -1.8 * (1 - 2.5 * self.diameter_fuselage /
                                 self.length_fuselage) * pi * \
                         self.diameter_fuselage * self.diameter_fuselage \
                         * self.length_fuselage / (4 * self.wing_area
                                                   * self.MAC) * self.cl_0 / self.cl_alpha_a_h
        return cm_ac_engines + cm_ac_w + cm_ac_fuselage

    @Attribute
    def cg_range(self):
        """ The c.g. range that is used for the scissor plot. It is between
        0 and 1. This means that is a fraction of the MAC.
                :rtype: numpy.ndarray
                """
        return np.linspace(0, 1, 100)

    @Attribute
    def c_l_h(self):
        """ Value dependent on the type of tail. Since a conventional
        aircraft is assumed it isset

                :rtype: float
                """
        return -0.8

    @Attribute
    def controllability_values(self):
        """ This attribute goes through the c.g. range and calculates the
        corresponding controllability limits. This is later used for the
        scissor plot.

                        :rtype: list
        """
        list = []
        for i in self.cg_range:
            first = i / (self.c_l_h / self.cl_alpha_a_h
                         * self.l_h / self.MAC * self.Vh_V_ratio ** 2)
            second = (self.cm_ac / self.cl_alpha_a_h - self.x_ac) \
                     / (self.c_l_h / self.cl_alpha_a_h
                        * self.l_h / self.MAC * self.Vh_V_ratio ** 2)
            list.append(first + second)
        return list

    @Attribute
    def stability_values(self):
        """ This attribute goes through the c.g. range and calculates the
                corresponding Stability limits. This is later used for the
                scissor plot.

                                :rtype: list
                """
        list = []
        for j in self.cg_range:
            first = j / (self.cl_alpha_horizontal / self.cl_alpha_a_h *
                         (1 - self.downwash_gradient) * self.l_h /
                         self.MAC * self.Vh_V_ratio ** 2)
            second = self.x_ac / (
                    self.cl_alpha_horizontal / self.cl_alpha_a_h *
                    (1 - self.downwash_gradient) * self.l_h /
                    self.MAC * self.Vh_V_ratio ** 2)
            list.append(first - second)
        return list

    @Attribute
    def tail_area(self):
        """ Calculates the tail area based on the stability and
        controllability contraint. It checks if it satisfies the constraints
        exactly which one is sizing.

                                :rtype: float
                """
        stability_forward_cg = self.forward_cg / (self.cl_alpha_horizontal /
                                 self.cl_alpha_a_h *
                                (1 - self.downwash_gradient) * self.l_h /
                                 self.MAC * self.Vh_V_ratio ** 2) \
                               - self.x_ac / (self.cl_alpha_horizontal /
                                 self.cl_alpha_a_h *
                                              (1 - self.downwash_gradient)
                                * self.l_h /self.MAC * self.Vh_V_ratio ** 2)

        stability_aft_cg =  self.aft_cg / (self.cl_alpha_horizontal /
                                 self.cl_alpha_a_h *
                                (1 - self.downwash_gradient) * self.l_h /
                                 self.MAC * self.Vh_V_ratio ** 2) \
                               - self.x_ac / (self.cl_alpha_horizontal /
                                 self.cl_alpha_a_h *
                                              (1 - self.downwash_gradient)
                                * self.l_h /self.MAC * self.Vh_V_ratio ** 2)

        controllability_forward_cg = self.forward_cg / \
                                     (self.c_l_h / self.cl_alpha_a_h
                                      * self.l_h / self.MAC
                                      * self.Vh_V_ratio ** 2) +\
                                     (self.cm_ac / self.cl_alpha_a_h -
                                      self.x_ac) \
                                     / (self.c_l_h /
                                        self.cl_alpha_a_h * self.l_h / self.MAC
                                        * self.Vh_V_ratio ** 2)

        controllability_aft_cg = self.aft_cg / \
                                     (self.c_l_h / self.cl_alpha_a_h
                                      * self.l_h / self.MAC
                                      * self.Vh_V_ratio ** 2) +\
                                     (self.cm_ac / self.cl_alpha_a_h -
                                      self.x_ac) \
                                     / (self.c_l_h /
                                        self.cl_alpha_a_h * self.l_h / self.MAC
                                        * self.Vh_V_ratio ** 2)

        if controllability_forward_cg > stability_forward_cg or \
                stability_aft_cg > controllability_forward_cg:

            control_diff = controllability_forward_cg - stability_forward_cg
            stability_diff = stability_aft_cg - controllability_aft_cg
            if control_diff > stability_diff:
                return controllability_forward_cg
            elif stability_diff> control_diff:
                return stability_aft_cg


    @Attribute(in_tree=False)
    def scissor_curve(self):
        """ Plots the scissor plot to get a visual idea about the
        controllability and stability constraints.

                                :rtype: matplotlip.pyplot.plot
                """
        plt.plot(self.cg_range, self.stability_values, label='Stability')
        plt.plot(self.cg_range, self.controllability_values,
                 label='Controllability')
        plt.xlabel('X_cg/MAC')
        plt.ylabel('S_h/S')
        plt.legend(loc='upper left')
        a = plt.show()
        return a


if __name__ == '__main__':
    from parapy.gui import display

    obj = ScissorPlot()
    display(obj)
