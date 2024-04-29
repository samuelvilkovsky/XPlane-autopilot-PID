import sys
import xpc as xpc
from datetime import datetime, timedelta
import PID as PID

# set update interval so loop runs at 10Hz
update_interval = 0.100 # seconds

# start is set when the script is executed
start = datetime.now()
last_update = start

# define initial PID values
P = 0.1 # initial proportional gain - 0.2
I = P/10 # initial integral gain - 0.0
D = 0 # initial derivative gain - 0.0

roll_pid = PID.PID(P, I, D)
pitch_pid = PID.PID(P, I, D)
heading_pid = PID.PID(P, I, D)

# set desired values
# roll = 0 means wings level
# pitch = 2 means slightly nose up. which is required for level flight

desired_roll = 0
desired_pitch = 2
desired_heading = 100

# setpoint is the desired value
roll_pid.SetPoint = desired_roll
pitch_pid.SetPoint = desired_pitch

def monitor():
    global last_update
    with xpc.XPlaneConnect() as client:
        while True:
            if (datetime.now() > last_update + timedelta(milliseconds=update_interval * 1000)):
                print("Updating -- curent time: %s" % datetime.now())
                last_update = datetime.now()
                posi = client.getPOSI();
                ctrl = client.getCTRL();

                current_roll = posi[4]
                current_pitch = posi[3]

                roll_pid.update(current_roll)
                pitch_pid.update(current_pitch)

                new_aileron_control = roll_pid.output
                new_elevator_control = pitch_pid.output

                # set the new control values
                ctrl = [new_elevator_control, new_aileron_control, 0.0, -998] # ele, ail, rud, thr, -998 means no change
                client.sendCTRL(ctrl)

                output = f"current values --    roll: {current_roll: 0.3f},  pitch: {current_pitch: 0.3f}"
                output = output + "\n" + f"PID outputs    --    roll: {roll_pid.output: 0.3f},  pitch: {pitch_pid.output: 0.3f}"
                output = output + "\n"
                print(output)


if __name__ == "__main__":
    monitor()