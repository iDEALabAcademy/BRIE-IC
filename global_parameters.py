from Config import Config
global_parameters = {'battery': 0.01}
max_battery = 0.5 * Config.capacitor_size * (Config.capacitor_voltage * Config.capacitor_voltage)
# battery= 0.025
computing_index = [0,0,0,0]  #L, K, H, W
time_speed = 1e+8

vt_sensing = Config.vt_sensing
vt_computation = Config.vt_computation
vt_backup = Config.vt_backup
vt_transmitting = Config.vt_transmitting
vt_start = Config.vt_start
safe_area = Config.safe_area
energy_offset = vt_start + vt_backup + safe_area


charge_value = 0
charge_plot = []
vt_sensing_plot = []
vt_computation_plot = []
vt_backup_plot = []
vt_transmitting_plot = []
vt_start_plot = [] #less than this threshold everything is down
vt_safe_area_plot = []
system_status_plot = []
battery_values = []
global_charge_index = 0

