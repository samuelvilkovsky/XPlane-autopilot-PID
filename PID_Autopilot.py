import sys
import os
import xpc
from datetime import datetime, timedelta
import PID
import time
import math, numpy
import redis
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

r = redis.StrictRedis(host='localhost', port=6379, db=0)

setpoints = {
    "desired_roll": 0,
    "desired_pitch": 2,
    "desired_speed": 160,
    "desired_alt": 5000.0,
    "desired_hdg": 140,
    "autopilot_enabled": 0
}

for key in setpoints:
    #   if the key exists in the redis db, use it
    #   otherwise set it
    if r.exists(key):
        setpoints[key] = float(r.get(key))
    else:
        r.set(key, setpoints[key])


update_interval = 0.10 #seconds
update_frequency = 1/update_interval
start = datetime.now()
last_update = start

# defining the initial PID values
P = 0.05
I = 0.01
D = 0
MAX_DEFLECTION_PER_SECOND = 2.0

# initializing PID controllers
roll_PID = PID.PID(P*2, I*2, D)
roll_PID.SetPoint = setpoints["desired_roll"]

pitch_PID = PID.PID(P, I, D)
pitch_PID.SetPoint = setpoints["desired_pitch"]

altitude_PID = PID.PID(P*2, P/2, D)
altitude_PID.SetPoint = setpoints["desired_alt"]

speed_PID = PID.PID(P, I, D)
speed_PID.SetPoint = setpoints["desired_speed"]

heading_error_PID = PID.PID(1,0.05,0.1)
heading_error_PID.SetPoint = 0 # need heading error to be 0


#   initialize graph data structures
x_axis_counters = [] #  0,1,2,3, etc. just basic x-axis values used for plotting
roll_history = []
pitch_history = []
altitude_history = []
roll_setpoint_history = []
pitch_setpoint_history = []
altitude_setpoint_history = []
plot_array_max_length = 100 #   how many data points to hold in our arrays and graph
i = 1

#   defining graph window and parameters
app = pg.mkQApp("python xplane autopilot monitor")

win = pg.GraphicsLayoutWidget(show=True)
win.resize(1000, 600) #     in pixels
win.setWindowTitle('XPlane autopilot system control')

p1 = win.addPlot(title="roll", row=0, col=0)
p2 = win.addPlot(title="pitch", row=1, col=0)
p3 = win.addPlot(title="altitude", row=2, col=0)

# show the y grid lines to make it easier to interpret the graphs
p1.showGrid(y=True)
p2.showGrid(y=True)
p3.showGrid(y=True)

# Define DREFs we want, airspeed, magnetic heading, ground indicator, height
DREFs = ["sim/cockpit2/gauges/indicators/airspeed_kts_pilot",
         "sim/cockpit2/gauges/indicators/heading_electric_deg_mag_pilot",
         "sim/flightmodel/failures/onground_any",
         "sim/flightmodel/misc/h_ind"]

#   Normalizer function
#   this function takes an input and either passes it through or adjust
#   the input to fit within specified max/min values
def normalize(value, min=-1, max=1):
    #   if value = 700, and max = 20, return 20
    #   if value = -200, and min = -20, return -20
    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value

def sleep_until_next_tick(update_frequency):
    #   Calculate the update inteval from the frequency
    update_interval = 1.0 / update_frequency

    #   Get the current time
    current_time = time.time()

    #   Calculate the time remaining until the next tick
    sleep_time = update_interval - (current_time % update_interval)

    #   Sleep for the remaining time
    time.sleep(sleep_time)

#   Function from external source
#   https://rosettacode.org/wiki/Angle_difference_between_two_bearings#Python
def get_angle_difference(b1,b2):
    r = (b2-b1) % 360.0
    #   No need to consider negative case
    if r >= 180.0:
        r -= 360.0
    return r

#   Function from external source
#   https://gist.github.com/jeromer/2005586
def get_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

#   Function from external source
#   https://janakiev.com/blog/gps-points-distance-python/
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

KBJC_lat = 39.9088056
KBJC_lon = -105.1171944

def write_position_to_redis(position):
    #   position is a list of 7 floats
    #   position elements [lat, lon, alt, pitch, roll, yaw, gear_indicator]
    position_elements = ["lat", "lon", "alt", "pitch", "roll", "yaw", "gear_indicator"]
    position_str = ','.join([str(x) for x in position])
    r.set('position', position_str)
    for i in range(len(position_elements)):
        r.set(f"position/{position_elements[i]}", position[i])


def get_setpoints_from_redis():
    setpoints = {
        "desired_roll": 0,
        "desired_pitch": 2,
        "desired_speed": 160,
        "desired_alt": 8000.0,
        "desired_hdg": 140
    }
    for key in setpoints:
        # if the key exists in the redis db, use it
        # otherwise, set it
        if r.exists(key):
            setpoints[key] = float(r.get(key))
        else:
            r.set(key, setpoints[key])
    return setpoints

def get_autopilot_enabled_from_redis():
    if r.exists("autopilot_enabled"):
        return int(r.get("autopilot_enabled").decode('utf-8')) == 1

ele_positions = []
ail_positions = []
thr_positions = []

def update_control_position_history(ctrl):
    ele_positions.append(ctrl[0])
    ail_positions.append(ctrl[1])
    thr_positions.append(ctrl[3])
    # if the list is longer than 20, pop the first element
    if len(ele_positions) > 20:
        ele_positions.pop(0)
        ail_positions.pop(0)
        thr_positions.pop(0)


def monitor():
    with xpc.XPlaneConnect() as client:
        while True:
            loop_start = datetime.now()
            print(f"loop start - {loop_start}")
            posi = client.getPOSI()
            write_position_to_redis(posi)
            ctrl = client.getCTRL()
            bearing_to_kbjc = get_bearing((posi[0], posi[1]), (KBJC_lat, KBJC_lon))
            dist_to_kbjc = haversine((posi[0], posi[1]), (KBJC_lat, KBJC_lon))
            # desired_hdg = 116 #bearing_to_kbjc
            multi_DREFs = client.getDREFs(DREFs)  # speed=0, mag hdg=1, onground=2
            current_roll = posi[4]
            current_pitch = posi[3]
            # current_hdg = posi[5] # this is true, need to use DREF to get mag ''
            current_hdg = multi_DREFs[1][0]
            current_altitude = multi_DREFs[3][0]
            current_asi = multi_DREFs[0][0]
            onground = multi_DREFs[2][0]
            # get the setpoints from redis
            setpoints = get_setpoints_from_redis()
            desired_hdg = setpoints["desired_hdg"]
            desired_alt = setpoints["desired_alt"]
            desired_speed = setpoints["desired_speed"]
            # outer loops first
            altitude_PID.SetPoint = desired_alt
            altitude_PID.update(current_altitude)
            heading_error = get_angle_difference(desired_hdg, current_hdg)
            heading_error_PID.update(heading_error)
            speed_PID.SetPoint = desired_speed

            new_pitch_from_altitude = normalize(altitude_PID.output, -10, 10)
            new_roll_from_heading_error = normalize(heading_error_PID.output, -25, 25)
            # if new_pitch_from_altitude > 15:
            #     new_pitch_from_altitude = 15
            # elif new_pitch_from_altitude < -15:
            #     new_pitch_from_altitude = -15

            pitch_PID.SetPoint = new_pitch_from_altitude
            roll_PID.SetPoint = new_roll_from_heading_error
            roll_PID.update(current_roll)
            speed_PID.update(current_asi)
            pitch_PID.update(current_pitch)
            new_ail_ctrl = normalize(roll_PID.output, min=-1, max=1)
            new_ele_ctrl = normalize(pitch_PID.output, min=-1, max=1)
            new_thr_ctrl = normalize(speed_PID.output, min=0, max=1)
            previous_ail_ctrl = ail_positions[-1] if len(ail_positions) > 0 else 0
            previous_ele_ctrl = ele_positions[-1] if len(ele_positions) > 0 else 0
            previous_thr_ctrl = thr_positions[-1] if len(thr_positions) > 0 else 0

            update_control_position_history((new_ele_ctrl, new_ail_ctrl, 0.0, new_thr_ctrl))
            onground = -1
            if onground == 1:
                print("on ground, not sending controls")
            else:
                if get_autopilot_enabled_from_redis():
                    # ctrl = [new_ele_ctrl_limited, new_ail_ctrl_limited, 0.0, new_thr_ctrl_limited]
                    ctrl = [new_ele_ctrl, new_ail_ctrl, 0.0, new_thr_ctrl]
                    client.sendCTRL(ctrl)
            loop_end = datetime.now()
            loop_duration = loop_end - loop_start
            output = f"current values --    roll: {current_roll: 0.3f},  pitch: {current_pitch: 0.3f},    hdg: {current_hdg:0.3f}, alt: {current_altitude:0.3f}, asi: {current_asi:0.3f}"
            output = output + "\n" + f"hdg error:                 {heading_error: 0.3f}"
            output = output + "\n" + f"new ctrl positions -- ail: {new_ail_ctrl: 0.4f},    ele: {new_ele_ctrl: 0.4f},   thr: {new_thr_ctrl:0.4f}"
            output = output + "\n" + f"PID outputs --   altitude: {altitude_PID.output: 0.4f},  pitch: {pitch_PID.output: 0.4f},   ail: {roll_PID.output: 0.3f},  hdg: {heading_error_PID.output: 0.3f}"
            output = output + "\n" + f"bearing to KBJC: {bearing_to_kbjc:3.1f}, dist: {dist_to_kbjc * 0.000539957:0.2f} NM"
            output = output + "\n" + f"loop duration (ms): {loop_duration.total_seconds() * 1000:0.2f} ms"
            print(output)
            sleep_until_next_tick(update_frequency)
            os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    monitor()