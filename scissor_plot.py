from parapy.core import *
from parapy.geom import *

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, tan, radians, pi, cos, radians
# Typical cg range 25 to 35 percent of MAC


class ScissorPlot(Base):
    # Inputs for stability only
    # Wing geometry or specifics
    cm0_airfoil = Input(0.)  # zero pitching moment coefficient of the airfoil.
    span = Input(20.)  # span of the wing.
    aspect_ratio = Input(8.)  # The aspect ratio of th wing.
    wing_area = Input(30.)  # Wing area
    wing_area_net = Input(38.)  # Wing area- the area within the fuselage
    l_h = Input(5.)  # horizontal distance between te tail and the c.g.
    z_h = Input(1.0)  # Vertical distance between c.g. and the tail
    sweep_angle = Input(20.)  # sweep angle
    cl_alpha_wing = Input(2 * pi)  # Lift curve coefficient.
<<<<<<< HEAD
    cl_alpha_horizontal = Input(2 * pi - 2.0)  # Lift curve of the tail
=======
    cl_alhpa_horizontal = Input(2 * pi - 2.0)  # Lift curve of the tail
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
    MAC = Input(3.)  # Mean aerodynamic chord
    taper_ratio = Input(0.5)  # Taper ratio of the main wing.
    cl_0 = Input(.5)  # lift at zero angle of attack.
    # engine inputs
<<<<<<< HEAD
    width_nacelle = Input(1.2)  # Width of the nacelle
=======
    width_nacelle = Input(1.2)  # Widt of the nacelle
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
    distance_nacel_mac = Input(2.2)  # Distance of the nacelle infront of the
    # main wing.
    # Other Inputs
    length_fuselage = Input(20.)  # Length of the fuselage
    diameter_fuselage = Input(5.)  # needed for stabiliser
    Vh_V_ratio = Input(sqrt(0.85))  # Statistics
    l_nose_LE = Input(8.)

    # Stability part of the scissor plot
    @Attribute
    def cl_alpha_a_h(self):
        """ Calculates the Lift curve coefficient of the fuselage wing body.

                        :rtype: float
                        """
        value = self.cl_alpha_wing * (
<<<<<<< HEAD
                1 + 2.15 * self.diameter_fuselage / self.span) \
                 * self.wing_area_net / self.wing_area + pi / 2. * \
                self.diameter_fuselage ** 2 \
=======
                    1 + 2.15 * self.diameter_fuselage / self.span) \
                * self.wing_area_net / self.wing_area + pi / 2. * self.diameter_fuselage ** 2 \
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
                / self.wing_area
        return value

    @Attribute
    def downwash_gradient(self):
        # THis attribute calculates the downwash gradient of the wing. This
        # is necessary in order to calculate the stability.

        r = self.l_h / (self.span / 2.)
        m_tv = self.z_h / (self.span / 2.)
<<<<<<< HEAD
        k_e_lambda = (0.1124 + 0.1265 * radians(
            self.sweep_angle) + 0.1766 * (radians(
            self.sweep_angle)) ** 2) / r ** 2 + 0.1024 / r + 2
        k_e_0 = 0.1124 / r ** 2 + 0.1024 / r + 2
        first = (r / (r ** 2 + m_tv ** 2)) * 0.4876 / (
            sqrt(r ** 2 + 0.6319 + m_tv ** 2))
        second = (1 + (
                r ** 2 / (r ** 2 + 0.7915 + 5.0734 * m_tv ** 2)) ** 0.3113) \
                 * (1 - sqrt(m_tv ** 2 / (1 + m_tv ** 2)))
        return k_e_lambda / k_e_0 * (first + second) * self.cl_alpha_wing / \
               (pi * self.aspect_ratio)
=======
        K_e_lambda = (0.1124 + 0.1265 * radians(
            self.sweep_angle) + 0.1766 * radians(
            self.sweep_angle) ** 2) / r ** 2 + 0.1024 / r + 2
        K_e_0 = 0.1124 / r ** 2 + 0.1024 / r + 2
        first = (r / (r ** 2 + m_tv ** 2)) * 0.4876 / (
            sqrt(r ** 2 + 0.6319 + m_tv ** 2))
        second = (1 + (
                    r ** 2 / (r ** 2 + 0.7915 + 5.0734 * m_tv ** 2)) ** 0.3113) \
                 * (1 - sqrt(m_tv ** 2 / (1 + m_tv)))
        return K_e_lambda / K_e_0 * (first + second) * self.cl_alpha_wing / (
                pi * self.aspect_ratio)
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e

    @Attribute
    def x_ac(self):
        # This attributes calculates the position of the aerodynamic centre
        # of the aircraft. For stability and controllability this position
        # is an important factor.
<<<<<<< HEAD
        x_ac_engines = 2 * -4.0 * self.width_nacelle ** 2 * \
                       self.distance_nacel_mac / \
                       (self.wing_area * self.MAC * self.cl_alpha_a_h)
        x_ac_wing = 0.25
        x_ac_rest_1 = -1.8 / self.cl_alpha_a_h * self.diameter_fuselage ** 2\
                      * self.l_nose_LE / (self.wing_area * self.MAC)
        x_ac_rest_2 = 0.273 / (1 + self.taper_ratio) * (
                self.wing_area / self.span) * self.diameter_fuselage * (
                              self.span - self.diameter_fuselage) / \
                            (self.MAC ** 2 *
                            (self.span + 2.15 * self.diameter_fuselage)) \
=======
        x_ac_engines = 2 * -2.5 * self.width_nacelle ** 2 * self.distance_nacel_mac / (
                self.wing_area * self.MAC * self.cl_alpha_A_H)
        x_ac_wing = 0.25
        x_ac_rest_1 = -1.8 / self.cl_alpha_wing * self.diameter_fuselage ** 2 \
                      * self.l_nose_LE / (self.wing_area * self.MAC)
        x_ac_rest_2 = 0.273 / (1 + self.taper_ratio) * (
                self.wing_area / self.span) * self.diameter_fuselage * (
                              self.span - self.diameter_fuselage) / (
                                  self.MAC ** 2 *
                                  (self.span + 2.15 * self.diameter_fuselage)) \
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
                      * tan(radians(self.sweep_angle))
        return x_ac_wing + x_ac_rest_1 + x_ac_rest_2 + x_ac_engines

    # @Attribute
    # def x_cg(self):
    #     return self.cl_alpha_wing/self.cl_alpha_a_h\
    #            *(1-self.downwash_gradient)*self.Vh_V_ratio ** 2 + self.x_ac

    # Stability part of the aircraft.
    @Attribute
    def cm_ac(self):
        # This calculates the moment coefficient around the aerodynamic centre.
        cm_ac_w = self.cm0_airfoil * (self.aspect_ratio * (cos(radians(
<<<<<<< HEAD
            self.sweep_angle))) ** 2 / (self.aspect_ratio + 2 *
            cos(radians(self.sweep_angle))))
        cm_ac_engines = -0.05
        cm_ac_fuselage = -1.8 * (1 - 2.5 * self.diameter_fuselage /
                         self.length_fuselage) * pi * self.diameter_fuselage \
                         * self.diameter_fuselage * self.length_fuselage / \
                         (4 * self.wing_area * self.MAC) * self.cl_0 / \
                         self.cl_alpha_a_h
=======
            self.sweep_angle))) ** 2 /
                                      (self.aspect_ratio + 2 * cos(radians(
                                          self.sweep_angle))))
        cm_ac_engines = +0.2
        cm_ac_fuselage = -1.8 * (
                    1 - 2.5 * self.diameter_fuselage / self.length_fuselage) \
                         * pi * self.diameter_fuselage * self.diameter_fuselage \
                         * self.length_fuselage / (
                                     4 * self.wing_area * self.MAC) \
                         * self.cl_0 / self.cl_alpha_A_H
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
        return cm_ac_engines + cm_ac_w + cm_ac_fuselage

    @Attribute
    def hoi(self):
        return self.cm0_airfoil * (self.aspect_ratio * (cos(radians(
            self.sweep_angle))) ** 2 /
                                   (self.aspect_ratio + 2 * cos(radians(
                                       self.sweep_angle))))

    @Attribute
    def cg_range(self):
        # The range of c.g.'s that is being used for computation of the
        # stabiilty and the controllability curve.
        return np.linspace(0, 1, 100)

    @Attribute
    def type_tail(self):
        # Value dependent on the type of tail. Right now set to fixed tail.
        return -0.8

    @Attribute
    def controllability_values(self):
        list = []
        for i in self.cg_range:
<<<<<<< HEAD
            first = i / (self.type_tail / self.cl_alpha_a_h
                         * self.l_h / self.MAC * self.Vh_V_ratio ** 2)
            second = (self.cm_ac / self.cl_alpha_a_h - self.x_ac) \
                     / (self.type_tail / self.cl_alpha_a_h
=======
            first = i / (self.type_tail / self.cl_alpha_A_H
                         * self.l_h / self.MAC * self.Vh_V_ratio ** 2)
            second = (self.cm_ac / self.cl_alpha_A_H - self.x_ac) \
                     / (self.type_tail / self.cl_alpha_A_H
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
                        * self.l_h / self.MAC * self.Vh_V_ratio ** 2)
            list.append(first + second)
        return list

    @Attribute
    def stability_values(self):
        list = []
        for j in self.cg_range:
<<<<<<< HEAD
            first = j / (self.cl_alpha_horizontal / self.cl_alpha_a_h *
                         (1 - self.downwash_gradient) * self.l_h /
                         self.MAC * self.Vh_V_ratio ** 2)
            second = self.x_ac / (
                    self.cl_alpha_horizontal / self.cl_alpha_a_h *
                    (1 - self.downwash_gradient) * self.l_h /
                    self.MAC * self.Vh_V_ratio ** 2)
=======
            first = j / (self.cl_alhpa_horizontal / self.cl_alpha_A_H *
                         (1 - self.downwash_gradient) * self.l_h / self
                         .MAC * self.Vh_V_ratio ** 2)
            second = (self.x_ac) / (
                    self.cl_alhpa_horizontal / self.cl_alpha_A_H *
                    (1 - self.downwash_gradient) * self.l_h / self
                    .MAC * self.Vh_V_ratio ** 2)
>>>>>>> cf22d987211f7394514057aefe9525b88f87552e
            list.append(first - second)
        return list

    @Attribute
    def scissor_curve(self):
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
