from math import sqrt, pi, radians

import matplotlib.pyplot as plt
import numpy as np
from parapy.core import *


# Typical cg range 25 to 35 percent of mac


class ScissorPlot(Base):
    """ This class calculates the scissor plot from the various inputs from
    the other classes. The purpose of this class is to size the tail for
    a certain c.g. range and a position of the tail and the main wing.
    """

    # Airfoil Specifics
    CL_0 = Input(validator=val.is_number)  # lift at zero angle of attack.
    Cm_0 = Input(validator=val.is_number)  # zero pitching moment

    # Wing Specifics
    # span of the wing.
    span = Input(validator=val.is_positive)
    # The aspect ratio of th wing.
    aspect_ratio = Input(validator=val.is_positive)
    # Wing area
    wing_area = Input(validator=val.is_positive)
    # Wing area- the area within the fuselage
    net_wing_area = Input(validator=val.is_positive)

    # horizontal distance between te tail and the c.g.
    l_h = Input(validator=val.is_number)
    # Vertical distance between c.g. and the tail
    z_h = Input(validator=val.is_number)
    # mac position wing & fus combination in main wing mac.
    x_ac = Input(validator=val.is_number)
    # CL alpha of the wing fus combination.
    CL_alpha_a_h = Input(validator=val.is_positive)
    # sweep angle at quarter chord
    sweep_angle_025c = Input(validator=val.is_number)
    # Lift curve coefficient.
    CL_alpha_wing = Input(validator=val.is_positive)
    # Lift curve of the tail
    CL_alpha_horizontal = Input(validator=val.is_positive)
    # Mean aerodynamic chord
    mac = Input(validator=val.is_positive)
    stability_margin = Input(validator=val.is_number)

    # Other Inputs
    # Length of the fuselage needed for stabiliser
    fuselage_length = Input(validator=val.is_positive)
    fuselage_diameter = Input(validator=val.is_positive)

    # Input depending of what tail configuration is used.
    tail_type = Input(validator=val.is_string)
    # Forward position of the c.g. as fraction of mac.
    forward_cg = Input()  # validator=val.Between(0, 1))
    # Aft position of the c.g. as fraction of mac.
    aft_cg = Input()  # validator=val.Between(0, 1))

    @Attribute
    def vh_v_ratio(self):
        """ Calculates the ratio between the velocities of the main wing and
        the horizontal tailplane. The choice is between Conventional,
        Mid and T Tail configuration

                :rtype: float
        """
        if self.tail_type == 't-tail':
            return sqrt(1)
        elif self.tail_type == 'mid-tail':
            return sqrt(0.95)
        elif self.tail_type == 'conventional':
            return sqrt(0.85)

    @Attribute
    def downwash_gradient(self):
        """ Calculates the downwash gradient using a semi-emperical method.

                :rtype: float
        """

        r = self.l_h / (self.span / 2.)
        m_tv = self.z_h / (self.span / 2.)

        k_e_lambda = (0.1124 + 0.1265 *
                      radians(self.sweep_angle_025c) +
                      0.1766 * (radians(self.sweep_angle_025c)) ** 2) / \
            r ** 2 + 0.1024 / r + 2

        k_e_0 = 0.1124 / r ** 2 + 0.1024 / r + 2

        first = (r / (r ** 2 + m_tv ** 2)) * 0.4876 / (
            sqrt(r ** 2 + 0.6319 + m_tv ** 2))

        second = (1 +
                  (r ** 2 / (r ** 2 + 0.7915 + 5.0734 * m_tv ** 2)) **
                  0.3113) \
            * (1 - sqrt(m_tv ** 2 / (1 + m_tv ** 2)))

        return k_e_lambda / k_e_0 * (first + second) * self.CL_alpha_wing / \
            (pi * self.aspect_ratio)

    @Attribute
    def cm_ac(self):
        """ The moment coefficient around the aerodynamic centre is
        calculated. This is used for the controllability curve of the aircraft.

        :rtype: float
        """
        cm_ac_engines = -0.05

        cm_ac_fuselage = -1.8 * (1 - 2.5 * self.fuselage_diameter
                                 / self.fuselage_length) \
            * pi * self.fuselage_diameter \
            * self.fuselage_diameter * self.fuselage_length \
            / (4 * self.wing_area * self.mac) \
            * self.CL_0 / self.CL_alpha_a_h

        return cm_ac_engines + self.Cm_0 + cm_ac_fuselage

    @Attribute
    def cg_range(self):
        """ The c.g. range that is used for the scissor plot. It is between
        0 and 1. This means that is a fraction of the mac.

        :rtype: numpy.ndarray
        """
        return np.linspace(0, 1, 100)

    @Attribute
    def c_l_h(self):
        """ Value dependent on the type of tail. Since a conventional
        aircraft is assumed it is set to -0.8

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
        list1 = []
        for i in self.cg_range:
            first = i / \
                    (self.c_l_h / self.CL_alpha_a_h
                     * self.l_h / self.mac * self.vh_v_ratio ** 2)

            second = (self.cm_ac / self.CL_alpha_a_h - self.x_ac) \
                / (self.c_l_h / self.CL_alpha_a_h
                    * self.l_h / self.mac * self.vh_v_ratio ** 2)

            list1.append(first + second)
        return list1

    @Attribute
    def stability_values(self):
        """ This attribute goes through the c.g. range and calculates the
        corresponding Stability limits. This is later used for the
        scissor plot.

        :rtype: list
        """
        list1 = []
        for j in self.cg_range:
            first = j / (self.CL_alpha_horizontal / self.CL_alpha_a_h *
                         (1 - self.downwash_gradient) * self.l_h /
                         self.mac * self.vh_v_ratio ** 2)
            second = (self.x_ac - self.stability_margin) / \
                     (self.CL_alpha_horizontal / self.CL_alpha_a_h *
                      (1 - self.downwash_gradient) * self.l_h /
                      self.mac * self.vh_v_ratio ** 2)
            list1.append(first - second)
        return list1

    @Attribute
    def tail_area(self):
        """ Calculates the tail area based on the stability and
        controllability constraint. It checks if it satisfies the constraints
        exactly which one is sizing.

        :rtype: float
        """
        stability_forward_cg = self.forward_cg / \
            (self.CL_alpha_horizontal / self.CL_alpha_a_h
                * (1 - self.downwash_gradient) * self.l_h
                / self.mac * self.vh_v_ratio ** 2) \
            - (self.x_ac - self.stability_margin) \
            / (self.CL_alpha_horizontal / self.CL_alpha_a_h
                * (1 - self.downwash_gradient)
                * self.l_h / self.mac * self.vh_v_ratio ** 2)

        stability_aft_cg = self.aft_cg / \
            (self.CL_alpha_horizontal / self.CL_alpha_a_h
                * (1 - self.downwash_gradient) * self.l_h
                / self.mac * self.vh_v_ratio ** 2) \
            - (self.x_ac - self.stability_margin) \
            / (self.CL_alpha_horizontal / self.CL_alpha_a_h
                * (1 - self.downwash_gradient)
                * self.l_h / self.mac * self.vh_v_ratio ** 2)

        controllability_forward_cg = self.forward_cg \
            / (self.c_l_h / self.CL_alpha_a_h
                * self.l_h / self.mac
                * self.vh_v_ratio ** 2) \
            + (self.cm_ac / self.CL_alpha_a_h -
                self.x_ac) \
            / (self.c_l_h / self.CL_alpha_a_h
                * self.l_h / self.mac
                * self.vh_v_ratio ** 2)

        controllability_aft_cg = self.aft_cg \
            / (self.c_l_h / self.CL_alpha_a_h
                * self.l_h / self.mac
                * self.vh_v_ratio ** 2) \
            + (self.cm_ac / self.CL_alpha_a_h -
                self.x_ac) \
            / (self.c_l_h / self.CL_alpha_a_h
                * self.l_h / self.mac
                * self.vh_v_ratio ** 2)

        if controllability_forward_cg > stability_forward_cg or \
                stability_aft_cg > controllability_forward_cg:

            control_diff = controllability_forward_cg - stability_forward_cg

            stability_diff = stability_aft_cg - controllability_aft_cg

            if control_diff > stability_diff:
                return controllability_forward_cg * self.wing_area

            elif stability_diff > control_diff:
                return stability_aft_cg * self.wing_area

    @Attribute(in_tree=False)
    def scissor_curve(self):
        """ Plots the scissor plot to get a visual idea about the
        controllability and stability constraints.

        :rtype: matplotlib.pyplot.plot
        """
        plt.plot(self.cg_range, self.stability_values, label='Stability')
        plt.plot(self.cg_range, self.controllability_values,
                 label='Controllability')
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        # plt.xlabel(r'\frac{x_{cg}}{mac}$')
        # plt.ylabel(r'$\frac{S_{h}}{S}$')
        plt.xlabel('x_cg/mac')
        plt.ylabel('S_h/S')
        plt.legend(loc='upper left')
        a = plt.show()
        return a


if __name__ == '__main__':
    from parapy.gui import display

    obj = ScissorPlot()
    display(obj)
