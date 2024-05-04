from global_parameters import *
from global_parameters import global_parameters

from utilities import *
import random


class StateMachine:
    def __init__(self):
        self.states = ['start', 'load', 'stop', 'standby', 'sense', 'compute', 'transmit', 'store']

        self.next_state = None
        self._transceiver_status = 'idle' # send and receive
        self.state_log = []
        self.NVM_state = None
        self.stop_counter = 0
        self.stop_interval = 0
        global vt_sensing 
        global vt_computation 
        global vt_backup 
        global vt_transmitting 
        global vt_start 
        global safe_area 
        global energy_offset 
        
        # self.backup_computing_index = 
        self.state_to_number = {
            'off': 0,
            'load': 7,
            'stop': 2,
            'standby': 1,
            'sense': 3,
            'compute': 4,
            'transmit': 5,
            'store': 6
        }
        self.total_energy = {
            'off': 0.0,
            'load': 0.0,
            'stop': 0.0,
            'standby': 0.0,
            'sense': 0.0,
            'compute': 0.0,
            'transmit': 0.0,
            'store': 0.0
        }
        self.number_to_state = {num: state for state, num in self.state_to_number.items()}
        self.current_state = 'off'

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        self._current_state = value
        self.state_log.append(self.convert_state_to_number()) 


            # self.on_change(value)
    # @property
    # def current_state(self):
    #     return self._current_state

    # @_current_state.setter
    # def current_state(self, value):
    #     self._current_state = value
    #     self.state_log.append(self.convert_state_to_number()) 
    #     return value

               
    def get_state_name(self, number):
        return self.number_to_state[number] 
       
    def convert_state_to_number(self):
        return self.state_to_number[self.current_state]

    def transition(self):
        self.static_power()
        if self.current_state == 'off':
            self.off()
        elif self.current_state == 'load':
            self.load()
        elif self.current_state == 'stop':
            self.stop()
        elif self.current_state == 'transmit' :
            self.transmit()
        elif self.current_state == 'compute' :
            self.compute()
        elif self.current_state == 'store':
            self.store()
        elif self.current_state == 'sense':
            self.sense()
        elif self.current_state == 'standby':
            self.standby()
        else:
            print(f'Invalid transition from {self.current_state}')

    def off(self):
        #TODO: add some power for startup
        if global_parameters['battery'] > vt_start:
            self.current_state = 'standby'

    def standby(self):
        #The system should go to the load mode
        # self.current_state = 'standby'
        if  self.current_state != 'standby':
            self.current_state = 'standby'
            precise_delay(Config.delay_wakeup/time_speed) 
            self.transition()
            
        elif global_parameters['battery'] > energy_offset: #we can change it to higher level to do at least one mac or transmit
            self.current_state = 'stop' #in standby the information lost
            if self.NVM_state != None:
                self.next_state = 'load'
            else:
                self.next_state = 'sense'
            precise_delay(Config.delay_wakeup/time_speed) 
            # self.transition()
        

    def stop(self):
        if global_parameters['battery'] < vt_start + vt_backup and self.NVM_state == None:
            self.stop_counter = 0
            self.store()
        if global_parameters['battery'] <  vt_start and self.current_state != 'standby':
            self.stop_counter = 0
            self.standby()    
        else:
            # if self.stop_interval == self.stop_counter: 
            self.stop_counter = 0
            if self.next_state == 'sense':
                self.sense()
            elif self.next_state == 'compute':
                self.compute() 
            elif self.next_state == 'transmit':
                self.transmit()
            elif self.next_state == 'load':
                self.load() 
            # self.stop_counter += 1

    def sense(self):
        # global global_parameters
        if global_parameters['battery'] > vt_sensing + energy_offset and self.current_state == 'stop':
            self.NVM_state = None
            self.current_state = 'sense'
            precise_delay(Config.delay_wakeup/time_speed) 
            self.transition()
        elif global_parameters['battery'] > vt_sensing + energy_offset and self.current_state == 'sense' :
            temp_energy = random.gauss(vt_sensing, vt_sensing*0.1)
            self.total_energy['sense'] += temp_energy
            global_parameters['battery'] -= temp_energy
            precise_delay(Config.delay_sensing/time_speed)
            self.current_state = 'stop'
            self.next_state = 'compute'

            
        return
                   
    def compute(self):
        global computing_index
        # global global_parameters
        mac_energy = energy_per_mac(Config.cpu_voltage_run_flash, Config.cpu_current_run_flash, Config.mips) 
        if global_parameters['battery'] > vt_computation + energy_offset and self.current_state == 'stop':
            self.NVM_state = None
            self.current_state = 'compute'
            precise_delay(Config.delay_wakeup/time_speed) 
            self.transition()
        elif global_parameters['battery'] > vt_computation + energy_offset and self.current_state == 'compute':
            for layer in range (computing_index[0], Config.layer_number ):#layer number
                mac_num = calculate_number_of_one_output_macs(Config.cnn_layers[layer])
                network_parameter = Config.cnn_layers[layer]['num_filters']
                for kernel in range (computing_index[1], Config.cnn_layers[layer]['num_filters'] ):#kernel number
                    for width in range (computing_index[2], Config.cnn_layers[layer]['input_dimensions'][0] ): #input width
                        for height in range (computing_index[3], Config.cnn_layers[layer]['input_dimensions'][1] ):#input height
                            
                            self.total_energy['compute'] += mac_num * mac_energy
                            global_parameters['battery']-= mac_num * mac_energy
                            mac_delay = (float(mac_num)/Config.mips)/time_speed
                            precise_delay(mac_delay)
                            computing_index[3] = height 
                            if global_parameters['battery'] < energy_offset:
                                self.next_state = self.current_state #contuniue in next power up
                                self.current_state = 'stop' 
                                return
                        computing_index[2] = width
                    computing_index[1] = kernel
                computing_index[0] = layer  
              
            #TODO: Check if transmit required
            if random.random() < 0.05: #in 5% we need transmit
                self.next_state = 'transmit' 
                computing_index[0] = computing_index[1] = computing_index[2] = computing_index[3] = 0
            else:
                self.next_state = 'sense'
            self.current_state = 'stop'                    
                            

    def transmit(self):
        #TODO: our architecture only support cnn layers we need to have something for MLP as well
        # global global_parameters

        if global_parameters['battery'] > vt_transmitting + energy_offset and self.current_state == 'stop':
            self.NVM_state = None
            self.current_state = 'transmit'
            precise_delay(Config.delay_wakeup/time_speed) 
            precise_delay(Config.tranceiver_transmit_wakeup_time/time_speed)
            self.transition()
        elif global_parameters['battery'] > vt_transmitting + energy_offset and self.current_state == 'transmit':
            output_width, output_height = calculate_output_size(Config.cnn_layers[Config.layer_number - 1])
            transfer_energy = energy_per_bit_tranceiver(Config.transiver_voltage, Config.tranceiver_transmit_current, Config.tranceiver_data_rate) * Config.support_bit
            
            for kernel in range (computing_index[1], Config.cnn_layers[Config.layer_number - 1]['num_filters'] ):#kernel number
                for width in range (computing_index[2], output_width): #output width
                    for height in range (computing_index[3], output_height):#output height
                        self.total_energy['transmit'] += transfer_energy
                        global_parameters['battery']-= transfer_energy
                        precise_delay((1/Config.tranceiver_data_rate)/time_speed)
                        computing_index[3] = height 
                        if global_parameters['battery'] < energy_offset:
                            self.next_state = self.current_state #contuniue in next power up
                            self.current_state = 'stop' 
                            return
                    computing_index[2] = width
                computing_index[1] = kernel
            #TODO: we can go to recieve mode here to get something from cloud 
            self.next_state = 'sense' 
            computing_index[2] = computing_index[3] = 0        
            self.current_state = 'stop'# 


            
    def store(self):
        #computing_index are use to strat point for recovery 

        if self.next_state == 'sense': # there is nothing to send
            return
        elif self.next_state == 'transmit':
            self.current_state = 'store'
            output_width, output_height = calculate_output_size(Config.cnn_layers[Config.layer_number - 1])
            write_energy = write_energy_per_bit_NVM() * Config.support_bit #assume the bus are same size
            for bit_number in range(0 , Config.support_bit): #most significant bit first
                for kernel in range (computing_index[1], Config.cnn_layers[Config.layer_number - 1]['num_filters'] ):#kernel number
                    for width in range (computing_index[2], output_width): #output width
                        for height in range (computing_index[3], output_height, Config.support_bit):#output height 
                            global_parameters['battery']-= write_energy #storing the last OF in NVM
                            self.total_energy['store'] += write_energy
                            precise_delay(Config.write_delay_per_bit/time_speed)
                            if global_parameters['battery'] < Config.vt_start:
                                self.next_state = 'load' 
                                self.current_state = 'standby' #TODO check with Arman
                                self.NVM_state = 'transmit'
                                return
            self.NVM_state = 'transmit'                
            self.current_state = 'stop'
            self.next_state = 'transmit' # value of computing_index did not change so with next power up the system start transmitting.
            return #TODO: Do we need to know backup is complete or not
        
        elif self.next_state == 'compute':
            self.current_state = 'store'
            write_energy = write_energy_per_bit_NVM() * Config.support_bit #assume the bus are same size
            for bit_number in range(0 , Config.support_bit): #most significant bit first
                for kernel in range (0, computing_index[1]):
                    for width in range (0, computing_index[2]): #input width
                        for height in range (0, computing_index[3], Config.support_bit):#input height
                            global_parameters['battery']-= write_energy #storing the last OF in NVM
                            self.total_energy['store'] += write_energy
                            precise_delay(Config.write_delay_per_bit/time_speed)
                            if global_parameters['battery'] < Config.vt_start:
                                self.next_state = 'load' 
                                self.current_state = 'standby' #TODO check with Arman
                                self.NVM_state = 'compute'
                                return
            self.NVM_state = 'compute'                
            self.current_state = 'stop'
            self.next_state = 'compute' # value of computing_index did not change so with next power up the system start transmitting.
            return #TODO: Do we need to know backup is complete or not
    
    def load(self):
        global global_parameters
        #computing_index are use to strat point for recovery 
        if global_parameters['battery'] > vt_start + vt_backup and self.NVM_state != None:
            self.current_state = 'load'
            if self.NVM_state == 'sense': # there is nothing to send
                self.next_state = self.NVM_state
                self.NVM_state = None 
                self.current_state = 'stop'
                self.transition()
                return
            elif self.NVM_state == 'transmit': #TODO: check if there is enough energy for load and a transmit
                output_width, output_height = calculate_output_size(Config.cnn_layers[Config.layer_number - 1])
                read_energy = read_energy_per_bit_NVM() * Config.support_bit #assume the bus are same size
                for bit_number in range(0 , Config.support_bit): #most significant bit first
                    for kernel in range (computing_index[1], Config.cnn_layers[Config.layer_number - 1]['num_filters'] ):#kernel number
                        for width in range (computing_index[2], output_width): #output width
                            for height in range (computing_index[3], output_height, Config.support_bit):#output height 
                                global_parameters['battery']-= read_energy #storing the last OF in NVM
                                self.total_energy['load'] += read_energy
                                precise_delay(Config.read_delay_per_bit/time_speed)
                                if global_parameters['battery'] < Config.vt_start: #load not completed
                                    self.next_state = 'load' 
                                    self.current_state = 'standby' #TODO check with Arman
                                    return
                self.next_state = self.NVM_state
                self.NVM_state = None                
                self.current_state = 'stop'
                
                self.transition()

                return #TODO: Do we need to know backup is complete or not

            elif self.NVM_state == 'compute':
                read_energy = read_energy_per_bit_NVM() * Config.support_bit #assume the bus are same size
                for bit_number in range(0 , Config.support_bit): #most significant bit first
                    for kernel in range (0, computing_index[1]):
                        for width in range (0, computing_index[2]): #input width
                            for height in range (0, computing_index[3], Config.support_bit):#input height
                                global_parameters['battery']-= read_energy #storing the last OF in NVM
                                self.total_energy['load'] += read_energy
                                precise_delay(Config.read_delay_per_bit/time_speed)
                                if global_parameters['battery'] < Config.vt_start:
                                    self.next_state = 'load' 
                                    self.current_state = 'standby' #TODO check with Arman
                                    return
                self.next_state = self.NVM_state
                self.NVM_state = None                
                self.current_state = 'stop'
                self.transition()
                return #TODO: Do we need to know backup is complete or not

    
    def static_power(self):
        interval = 1.0

        self.state_log.append(self.convert_state_to_number()) 
        global global_parameters
        if global_parameters['battery'] < 0:
            global_parameters['battery'] = 0.0
        elif self.current_state == 'stop':
            global_parameters['battery'] -= energy(Config.cpu_voltage_stop,Config.cpu_current_stop, interval)# TODO: change it using stop and standby power
            self.total_energy['stop'] += energy(Config.cpu_voltage_stop,Config.cpu_current_stop, interval)
        elif self.current_state == 'standby':
            global_parameters['battery'] -= energy(Config.cpu_voltage_standby,Config.cpu_current_standby, interval)
            self.total_energy['standby'] += energy(Config.cpu_voltage_standby,Config.cpu_current_standby, interval)
        # print("charging, battery level is " + str(global_parameters['battery']) + " state= " + self.current_state + "charge value = " + str(charge_value))
        

# Example Usage
# machine = StateMachine()
# machine.start()  # Begin with the start state

# In a real application, events like 'initialize', 'data_ready', etc., would be triggered by external factors
