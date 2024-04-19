import jsbsim
import time

aircraft = 'F16'
init_script = 'model/reset_base.xml'

fdm = jsbsim.FGFDMExec("/Users/samuelvilkovsky/Library/Python/3.9/lib/python/site-packages/jsbSim")
fdm.load_model(aircraft)
fdm.load_ic(init_script, False)
fdm.run_ic()

target_altitude = 10000

for _ in range (3600):
    altitude = fdm['position/h-sl-ft']

    error = target_altitude - altitude
    pitch_command = 0.05 * error
    fdm['fcs/pitch-cmd-norm'] = pitch_command

    fdm.run()
    time.sleep( 1 / 60 )

    print(f'altitude: {altitude: .2f} ft')

fdm.reset_to_initial_conditions(1)