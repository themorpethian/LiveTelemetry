#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

import ctypes.wintypes
import configparser
import os


class Config(object):
    """ Singleton to handle configuration methods. """

    __configs = configparser.ConfigParser()

    def __init__(self):
        """ Loads or creates the app configuration file. """
        if os.path.isfile("apps/python/LiveTelemetry/cfg.ini"):
            Config.__configs.read("apps/python/LiveTelemetry/cfg.ini")
        else:
            video = configparser.ConfigParser()
            Config.__configs["Windows"] = { "Engine": "False", "FL": "False", "FR": "False", "RL": "False", "RR": "False", "SIZE": "480p"}
            Config.__configs["Positions"] = {}
            
            # Try to use video.ini settings to recalculate window positions.
            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value            
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            
            video.read("{}/Assetto Corsa/cfg/video.ini".format(buf.value));
            h = int(video.get("VIDEO", "HEIGHT"))
            w = int(video.get("VIDEO", "WIDTH"))
            self.set_engine_position((w - 360) / 2, h - 51 - 160)
            self.set_position("FL", 10, 80)
            self.set_position("FR", w - 360 - 10, 80)
            self.set_position("RL", 10, h - 163 - 80)
            self.set_position("RR", w - 360 - 10, h - 163 - 80)

    def get_engine_x(self):
        """ Returns the x position of the engine window. """
        return float(self.get_str("Positions", "Engine_x"))

    def get_engine_y(self):
        """ Returns the y position of the engine window. """
        return float(self.get_str("Positions", "Engine_y"))

    def get_resolution(self):
        """ Returns the windows resolution. """
        return self.get_str("Windows", "SIZE")

    def get_str(self, section, option):
        """ Returns an option. """
        return Config.__configs.get(section, option)

    def get_x(self, wheel_id):
        """ Returns the x position of window. """
        return float(self.get_str("Positions", "{}_x".format(wheel_id)))

    def get_y(self, wheel_id):
        """ Returns the y position of window. """
        return float(self.get_str("Positions", "{}_y".format(wheel_id)))

    def is_active(self, wheel_id):
        """ Returns if window is active. """
        return bool(self.get_str("Windows", wheel_id))
    
    def is_engine_active(self):
        """ Returns if engine window is active. """
        return bool(self.get_str("Windows", "Engine"))

    def save_config(self):
        """ Writes the actual options on the configuration file. """
        cfg_file = open("apps/python/LiveTelemetry/cfg.ini", 'w')
        Config.__configs.write(cfg_file)
        cfg_file.close()

    def set_active(self, wheel_id, active):
        """ Updates if window is active. """
        self.set_str("Windows", wheel_id, str(active))
    
    def set_engine_active(self, active):
        """ Updates if engine window is active. """
        self.set_str("Windows", "Engine", str(active))

    def set_engine_position(self, pos_x, pos_y):
        """ Updates engine window position. """
        self.set_str("Positions", "Engine_x", str(pos_x))
        self.set_str("Positions", "Engine_y", str(pos_y))

    def set_position(self, wheel_id, pos_x, pos_y):
        """ Updates window position. """
        self.set_str("Positions", "{}_x".format(wheel_id), str(pos_x))
        self.set_str("Positions", "{}_y".format(wheel_id), str(pos_y))

    def set_str(self, section, option, value):
        """ Updates an option. """
        Config.__configs.set(section, option, value)
