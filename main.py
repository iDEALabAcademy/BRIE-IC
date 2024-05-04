
import random
import numpy as np
from utilities import *
from Config import Config
import matplotlib.pyplot as plt
import threading
from global_parameters import *
from global_parameters import global_parameters
from states import StateMachine
import pandas as pd


import os
from datetime import datetime



with open(Config.charge_trace, 'r') as file:
        data = [float(line.strip()) for line in file.readlines()]



def charge_battery(stop_event):
    # global global_parameters
    global charge_value
    global battery_values
    global global_charge_index
    global data

    while not stop_event.is_set():

        if global_charge_index == len(data):
            global_charge_index = 0
        real_sample = Config.charging_sample_rate * time_speed
        temp_charge = data[global_charge_index] / real_sample
        temp_charge *= 0.7
        for i in range(0, int(real_sample)):
            precise_delay(100.0/time_speed)
            charge_value = temp_charge + random.gauss(temp_charge, temp_charge)
            global_parameters['battery'] += charge_value
            if global_parameters['battery'] > max_battery:
                global_parameters['battery'] = max_battery
        global_charge_index += 1



def log_system():
    #log all the parameters to plot
    global charge_value
    global battery_values
    global vt_sensing_plot
    global vt_computation_plot
    global vt_safe_area_plot
    global vt_backup_plot
    global vt_transmitting_plot
    global charge_plot
    global vt_start_plot
    global system_status_plot
    global machine
    # global global_parameters
    
    battery_values.append(global_parameters['battery'])
    vt_sensing_plot.append(energy_offset + vt_sensing)
    vt_computation_plot.append(energy_offset + vt_computation)
    vt_safe_area_plot.append(energy_offset)
    vt_backup_plot.append(energy_offset - safe_area)
    vt_transmitting_plot.append(energy_offset + vt_transmitting)
    vt_start_plot.append(vt_start)
    charge_plot.append(charge_value)
    # charge_value = 0
    # machine.state_log.append(machine.convert_state_to_number())

    
def system_monitor(stop_event): 
    global global_parameters
    global battery_values
    global machine
    while not stop_event.is_set():

        log_system()
        precise_delay(1.0/time_speed)


def system_plot(name):
    # Generate an array of indices for the x-values
    print(len(battery_values))
    print(len(machine.state_log)) 
    fig, axs = plt.subplots(3) # TODO: add system states to plot
    fig.suptitle('Vertically stacked subplots')
    x = np.arange(len(battery_values))


    
    # Plot the array
    axs[0].plot(x, battery_values, label = "battery")
    axs[0].plot(x, vt_sensing_plot, label = "Sensing")
    axs[0].plot(x, vt_computation_plot, label = "Computation")
    axs[0].plot(x, vt_backup_plot, label = "Backup")
    axs[0].plot(x, vt_transmitting_plot, label = "Transmit")
    axs[0].plot(x, vt_start_plot, label = "Off")
    axs[0].plot(x, vt_safe_area_plot, label = "Safe area")

    
    axs[1].plot(x, charge_plot, label = "charge")

    
    state_names_log = [machine.get_state_name(state_number) for state_number in range(len(machine.state_to_number))]
    indices = list(range(len(machine.state_to_number)))

    # Plotting
    new_states = remove_specific_consecutive_duplicates(machine.state_log,[1,2,3,4,5,6,7,8,9,0])
    # axs[2].plot(new_states, 'o-', label="System Status")  # Using 'o-' to indicate both line and marker

    # # Set the y-ticks to show state names
    # axs[2].set_yticks(indices)
    # axs[2].set_yticklabels(state_names_log)

    # axs[2].plot(new_states, label = "system status")


    
    axs[2].bar(range(len(new_states)), new_states, label="System Status", width = 1)
    axs[2].set_yticks(indices)
    axs[2].set_yticklabels(state_names_log)
    np.savetxt('change_state_log.txt', np.array(new_states), fmt='%d')
    # axs[2].legend(loc='upper right',bbox_to_anchor=(1, 1))

    # Add title and labels
    # axs[0].title("Plot of a 1D Array")
    # axs[0].xlabel("Index")
    # axs[0].ylabel("Value")
    # plt.legend()
    # Display the plot
    # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.savefig(name, dpi=1200)

    data1 = {
    'x': x,
    'battery': battery_values,
    'sensing': vt_sensing_plot,
    'computation': vt_computation_plot,
    'backup': vt_backup_plot,
    'transmit': vt_transmitting_plot,
    'off': vt_start_plot,
    'safe_area': vt_safe_area_plot
    }
    data2 = {
        'x': x,
        'charge': charge_plot
    }
    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_data(data1, f'system_energy_{current_date}.csv')
    save_data(data2, f'battery_{current_date}.csv')
    



def state_machines_transient(stop_event):
    global machine
    while not stop_event.is_set():
        machine.transition()
        precise_delay(1/time_speed)


if __name__ == '__main__':
    machine = StateMachine()
    machine.off()  # Begin with the off state

    
    stop_battery_charging = threading.Event()
    stop_state_machine = threading.Event()
    stop_system_monitor = threading.Event()
    stop_back_up_monitor = threading.Event()
    stop_static_power = threading.Event()
    
    stop_battery_charging.clear()
    stop_state_machine.clear()
    stop_system_monitor.clear()
    stop_back_up_monitor.clear()
    stop_static_power.clear()
    
    system = threading.Thread(target=system_monitor, args=(stop_system_monitor,))
    state_machine = threading.Thread(target=state_machines_transient, args=(stop_state_machine,))
    # static_power_tr = threading.Thread(target=static_power, args=(stop_static_power,))
    
    # battery_charging.start()
    system.start()
    state_machine.start()
    # static_power_tr.start()
    
    for i in range(6):
        battery_charging = threading.Thread(target=charge_battery, args=(stop_battery_charging,))
        stop_battery_charging.clear()
        battery_charging.start()
        time.sleep(20)
        stop_battery_charging.set()
        battery_charging.join()
        # time.sleep(20)
    
    stop_battery_charging.set()
    stop_state_machine.set()
    stop_system_monitor.set()
    stop_back_up_monitor.set()
    stop_static_power.set()
    
    # static_power_tr.join()
    battery_charging.join()
    system.join()
    state_machine.join()

    # Save array to a file using NumPy
    np.savetxt('state_log.txt', np.array(machine.state_log), fmt='%d')
    
    print(global_charge_index)
    print(print_dictionary_keys_and_values(machine.total_energy))

    print(calculate_percentage_of_all_values(machine.state_log))
    
    state_names_log1 = [machine.get_state_name(state_number) for state_number in range(len(machine.state_to_number))]

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    plot_energy(machine.total_energy, f'system_energy_{current_date}.png',)
    plot_dict(calculate_percentage_of_all_values(machine.state_log),f"states_{current_date}.png",state_names_log1)
    system_plot(f"plot_{current_date}.png")