import configparser

class Config():
    __config = configparser.ConfigParser()
    __config.read('config.ini')
    #Hardware Configs
    capacitor_size = float(__config["HardwareConfig"]["capacitor_size"])
    capacitor_voltage = float(__config["HardwareConfig"]["capacitor_voltage"])
    charge_trace = str(__config["HardwareConfig"]["charging_trace"])
    charging_sample_rate = float(__config["HardwareConfig"]["charging_sample_rate"])
    vt_sensing = float(__config["HardwareConfig"]["vt_sensing"])
    vt_computation = float(__config["HardwareConfig"]["vt_computation"])
    vt_backup = float(__config["HardwareConfig"]["vt_backup"])
    vt_transmitting = float(__config["HardwareConfig"]["vt_transmitting"])
    vt_start = float(__config["HardwareConfig"]["vt_start"])
    safe_area = float(__config["HardwareConfig"]["safe_area"])
    delay_sensing = float(__config["HardwareConfig"]["delay_sensing"])
    delay_wakeup = delay_sensing = float(__config["HardwareConfig"]["delay_wakeup"])

    write_energy_per_bit = float(__config["HardwareConfig"]["write_energy_per_bit"])
    read_energy_per_bit = float(__config["HardwareConfig"]["read_energy_per_bit"])

    read_delay_per_bit = float(__config["HardwareConfig"]["read_delay_per_bit"])
    write_delay_per_bit = float(__config["HardwareConfig"]["write_delay_per_bit"])

    #CPU Configs
    mips = float(__config["CpuConfig"]["dmips"]) * float(__config["CpuConfig"]["frequency"]) * 1e-6

    # run-flash,run-ram,stop,standby
    cpu_currents = __config["CpuConfig"]["current_" + str(int(float(__config["CpuConfig"]["frequency"]) * 1e-6))].split(',') 
    cpu_current_run_flash = float(cpu_currents[0])
    cpu_current_run_ram = float(cpu_currents[1])
    cpu_current_stop = float(cpu_currents[2])
    cpu_current_standby = float(cpu_currents[3])


    cpu_voltages = __config["CpuConfig"]["cpu_voltage"].split(',') 
    cpu_voltage_run_flash = float(cpu_voltages[0])
    cpu_voltage_run_ram = float(cpu_voltages[1])
    cpu_voltage_stop = float(cpu_voltages[2])
    cpu_voltage_standby = float(cpu_voltages[3])

    support_bit =  int(__config["CpuConfig"]["support_bit"])



    #tranceiver
    tranceiver_sleep_current =  float(__config["TransceiverConfig"]["sleep_current"])
    tranceiver_receive_current =  float(__config["TransceiverConfig"]["receive_current"])
    tranceiver_transmit_current =  float(__config["TransceiverConfig"]["transmit_current"])
    tranceiver_receive_wakeup_time =  float(__config["TransceiverConfig"]["receive_wakeup_time"])
    tranceiver_transmit_wakeup_time =  float(str(__config["TransceiverConfig"]["transmit_wakeup_time"]).split('+')[0]) + float(str(__config["TransceiverConfig"]["transmit_wakeup_time"]).split('+')[1])
    tranceiver_data_rate =  float(__config["TransceiverConfig"]["data_rate"])
    transiver_voltage =  float(__config["TransceiverConfig"]["transiver_voltage"])
    
    #Network Configs
    cnn_layers = []
    layer_number = int(__config["NetworkConfig"]["layer_number"])
    try:
        for i in range(0, layer_number ):
            temp =  str(__config["NetworkConfig"]["layer"+str(i)]).split(":")

            conv_layer = {
                "input_dimensions": [int(item) for item in temp[0].split(',')],
                "filter_dimensions": [int(item) for item in temp[1].split(',')],
                "num_filters": int(temp[2]),
                "stride": int(temp[3]),
                "padding": int(temp[4])
            }
            cnn_layers.append(conv_layer)

    except :
        pass