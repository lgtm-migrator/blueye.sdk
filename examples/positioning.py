import threading
import serial
import time

from blueye.sdk import Pioneer


class PioneerPosition(threading.Thread):
    """A serial interface to the sonardyne positioning beacon on the Pioneer at BTS 2019

    self.northing: the current relative northing in meters, of the Pioneer to the middle of the pool
    self.easting: the current relative easting in meters, of the Pioneer to the middle of the pool
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.northing = 0
        self.easting = 0
        self.ser = serial.Serial("/dev/ttyUSB3", 9600, timeout=1)
        print("Serial connected")

    def run(self):
        while True:
            msg = self.ser.readline().decode("utf-8").split(",")
            if len(msg) > 5:
                self.northing = msg[4]
                self.easting = msg[5]


# below are some example functions. They are not well tested, but can serve as a place to start from
# for experimenting with acoustic positioning of the Pioneer
def print_pos_forever():
    while True:
        print(f"Pioneer Northing: {p_pos.northing},  Easting: {p_pos.easting}")
        time.sleep(1)


# limit the Pioneers thruster input to <-0.5, 0.5>, half of the full range
def limit_force(force, max_force=0.5):
    if abs(force) > max_force:
        force_sign = force / abs(force)
        force = 0.5 * force_sign
    return force


# P regulator that controls the surge axis of the Pioneer
def positioning(wanted_pos, current_pos, pioneer):
    delta = wanted_pos - current_pos
    force = delta * 0.01
    limited_force = limit_force(force)
    print(f"Surge force: {limited_force}")
    pioneer.motion.surge = limited_force


pioneer_pos = PioneerPosition()
# start a thread that reads the position of the Pioneer over serial at 1Hz
pioneer_pos.start()
p = Pioneer()

# a starting point for a positioning loop for northing positioning
while True:
    wanted_northing_pos = 5
    positioning(wanted_northing_pos, pioneer_pos.northing, p)
    time.sleep(1)
