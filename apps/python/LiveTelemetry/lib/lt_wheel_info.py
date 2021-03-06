#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one wheel infos from car and draw on screen.
"""
import copy
import sys

import ac

from lib.lt_colors import Colors
from lib.lt_config import Config
from lib.lt_components import BoxComponent, Camber, Dirt, Height, Pressure, Temps, Suspension, Tyre, Wear
from sim_info.sim_info import info
from lib.lt_util import WheelPos


class Data(object):

    def __init__(self):
        self.camber = 0.0
        self.height = 0.0
        self.susp_m_t = 1.0
        self.susp_t = 0.0
        self.timestamp = 0
        self.tyre_d = 0.0
        self.tyre_p = 0.0
        self.tyre_t_c = 0.0
        self.tyre_t_i = 0.0
        self.tyre_t_m = 0.0
        self.tyre_t_o = 0.0
        self.tyre_w = 0.0

    def update(self, wheel, info):
        index = wheel.index()
        self.camber = info.physics.camberRAD[index]

        # If there's no max travel, keep it 50%.
        self.susp_t = info.physics.suspensionTravel[index]
        max_travel = info.static.suspensionMaxTravel[index]
        self.susp_m_t = max_travel if max_travel > 0.0 else (self.susp_t * 2.0)
        
        # um to mm
        self.height = info.physics.rideHeight[int(index / 2)] * 1000.0
        
        # Get susp diff
        susp_diff = self.susp_t - info.physics.suspensionTravel[index + (1 if wheel.is_left() else -1)]
        self.height -= ((susp_diff / 2.0) * 1000.0)
        
        self.timestamp = info.graphics.iCurrentTime
        self.tyre_d = info.physics.tyreDirtyLevel[index] * 4.0

        # N to (5*kgf)
        # self.tyre_l = info.physics.wheelLoad[index] / (5.0 * 9.80665)
        self.tyre_p = info.physics.wheelsPressure[index]
        self.tyre_t_c = info.physics.tyreCoreTemperature[index]
        self.tyre_t_i = info.physics.tyreTempI[index]
        self.tyre_t_m = info.physics.tyreTempM[index]
        self.tyre_t_o = info.physics.tyreTempO[index]

        # Normal to percent
        self.tyre_w = info.physics.tyreWear[index] / 100.0


class WheelInfo(object):
    """ Wheel info to draw and update each wheel. """

    def __init__(self, wheel_index):
        """ Default constructor receive the index of the wheel it will draw info. """
        configs = Config()

        self.__wheel = WheelPos(wheel_index)
        self.__active = False
        self.__data = Data()
        self.__data_log = []
        self.__info = info
        self.__window_id = ac.newApp("Live Telemetry {}".format(self.__wheel.name()))
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        pos_x = configs.get_x(self.__wheel.name())
        pos_y = configs.get_y(self.__wheel.name())
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setSize(self.__bt_resolution, 50, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

        self.__components = []
        self.__components.append(Temps(resolution, self.__wheel))
        self.__components.append(Dirt(resolution))
        self.__components.append(Tyre(resolution, self.__wheel))

        # self.__components.append(Brake(resolution, self.__wheel, self.__window_id))
        self.__components.append(Camber(resolution))
        self.__components.append(Suspension(resolution, self.__wheel))
        self.__components.append(Height(resolution, self.__wheel, self.__window_id))
        self.__components.append(Pressure(resolution, self.__wheel, self.__window_id))
        self.__components.append(Wear(resolution, self.__wheel))
        # self.__components.append(Load(resolution))

        self.set_active(configs.is_active(self.__wheel.name()))
    
    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self.__data_log

    def get_id(self):
        """ Returns the wheel id. """
        return self.__wheel.name()

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_button_id(self):
        """ Returns the resolution button id. """
        return self.__bt_resolution

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self):
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.draw(self.__data)
        ac.glColor4f(*Colors.white)

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)
        ac.setText(self.__bt_resolution, resolution)
        for component in self.__components:
            component.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def update(self):
        """ Updates the wheel information. """
        self.__data.update(self.__wheel, self.__info)
        self.__data_log.append(copy.copy(self.__data))
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.update(self.__data)
