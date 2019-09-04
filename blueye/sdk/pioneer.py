#!/usr/bin/env python3
import threading
from typing import Iterator, Tuple

from blueye.protocol import TcpClient, UdpClient


class PioneerStateWatcher(threading.Thread):
    """
    Subscribes to UDP messages from the drone and stores the latest data
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.general_state = None
        self.calibration_state = None
        self._udpclient = UdpClient()
        self._exit_flag = threading.Event()
        self.daemon = True

    def run(self):
        while not self._exit_flag.is_set():
            data_packet = self._udpclient.get_data_dict()
            if data_packet["command_type"] == 1:
                self.general_state = data_packet
            elif data_packet["command_type"] == 2:
                self.calibration_state = data_packet

    def stop(self):
        self._exit_flag.set()


class Pioneer:
    def __init__(self, ip="192.168.1.101", tcpPort=2011, autoConnect=True):
        self._ip = ip
        self._tcpclient = TcpClient(
            ip=ip, port=tcpPort, autoConnect=autoConnect)
        self._stateWatcher = PioneerStateWatcher()
        if autoConnect is True:
            self._stateWatcher.start()
            self.thruster_setpoint(0, 0, 0, 0)

    @property
    def lights(self) -> int:
        state = self._stateWatcher.general_state
        return (state["lights_upper"])

    @lights.setter
    def lights(self, brightness: int):
        try:
            self._tcpclient.set_lights(brightness, 0)
        except ValueError as e:
            raise ValueError("Error occured while trying to set lights to: "
                             f"{brightness}") from e

    def thruster_setpoint(self, surge, sway, heave, yaw):
        self._tcpclient.motion_input(surge, sway, heave, yaw, 0, 0)

    @property
    def auto_depth_active(self) -> bool:
        state = self._stateWatcher.general_state
        if(state["control_mode"] is 3 or 9):
            return True
        else:
            return False

    @auto_depth_active.setter
    def auto_depth_active(self, active: bool):
        if active:
            self._tcpclient.auto_depth_on()
        else:
            self._tcpclient.auto_depth_off()

    @property
    def auto_heading_active(self) -> bool:
        state = self._stateWatcher.general_state
        if(state["control_mode"] is 7 or 9):
            return True
        else:
            return False

    @auto_heading_active.setter
    def auto_heading_active(self, active: bool):
        if active:
            self._tcpclient.auto_heading_on()
        else:
            self._tcpclient.auto_heading_off()


if __name__ == "__main__":
    pioneer = Pioneer()
