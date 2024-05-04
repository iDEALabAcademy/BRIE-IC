import time
from global_parameters import *
import matplotlib.pyplot as plt
import pandas as pd

def calculate_macs(layer):
    """
    Calculate the number of Multiply-Accumulate Operations for a convolutional layer.
    
    Parameters:
    layer (dict): A dictionary containing layer parameters.
    
    Returns:
    int: The number of MAC operations.
    """
    # Extract layer parameters
    input_height, input_width, input_channels = layer["input_dimensions"]
    filter_height, filter_width = layer["filter_dimensions"]
    num_filters = layer["num_filters"]
    stride = layer["stride"]
    padding = layer["padding"]
    
    # Calculate output dimensions
    out_height = ((input_height - filter_height + 2 * padding) // stride) + 1
    out_width = ((input_width - filter_width + 2 * padding) // stride) + 1
    
    # Calculate MACs
    macs = out_height * out_width * num_filters * filter_height * filter_width * input_channels
    return macs

def calculate_number_of_one_output_macs(layer):
    """
    Calculate the number of Multiply-Accumulate Operations for one output.
    
    Parameters:
    layer (dict): A dictionary containing layer parameters.
    
    Returns:
    int: The number of MAC operations.
    """
    # Extract layer parameters
    input_height, input_width, input_channels = layer["input_dimensions"]
    filter_height, filter_width = layer["filter_dimensions"]

    # Calculate MACs
    macs = filter_height * filter_width * input_channels
    return macs

def calculate_output_size(layer):
    """
    Calculate output_size for a convolutional layer.
    
    Parameters:
    layer (dict): A dictionary containing layer parameters.
    
    Returns:
    int: output size (width, height).
    """
    # Extract layer parameters
    input_height, input_width, input_channels = layer["input_dimensions"]
    filter_height, filter_width = layer["filter_dimensions"]
    num_filters = layer["num_filters"]
    stride = layer["stride"]
    padding = layer["padding"]
    
    # Calculate output dimensions
    out_height = ((input_height - filter_height + 2 * padding) // stride) + 1
    out_width = ((input_width - filter_width + 2 * padding) // stride) + 1
    
    # Calculate MACs
   
    return out_width, out_height


        
def energy_per_mac(voltage, current, mips):

   return (voltage * current)/(mips * 1e6) #energy of one mac operation

def energy_per_bit_tranceiver(voltage, current, data_rate):

   return (voltage * current)/(data_rate) #energy send or receive one bit

def write_energy_per_bit_NVM():
#TODO: check it
   return  Config.write_energy_per_bit  #energy send or receive one bit

def read_energy_per_bit_NVM():
#TODO: check it
   return  Config.read_energy_per_bit  #energy send or receive one bit    


def precise_delay(target_delay):
    start = time.perf_counter()
    while (time.perf_counter() - start) < target_delay:
        pass

def remove_specific_consecutive_duplicates(seq, values_to_remove):
    if not seq:  # Check if the list is empty
        return []
    
    result = [seq[0]]  # Initialize the result list with the first element
    for item in seq[1:]:  # Iterate over the list starting from the second element
        # Check for consecutive duplicates that are in the values_to_remove list
        if item in values_to_remove and item == result[-1]:
            continue  # Skip adding this item to the result
        else:
            result.append(item)  # Add the item to the result
    return result
def energy(voltage, current, time):
    '''
    voltage (V)
    current (A)
    time (s)
    '''
    return voltage * current * time

def print_dictionary_keys_and_values(dictionary):
    result = ""
    for key, value in dictionary.items():
        result += (f"Key: {key}, Value: {value}") + '\n'
    return result

def calculate_percentage_of_all_values(array):
    # Create a dictionary to count occurrences of each value
    value_counts = {}
    for value in array:
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1

    # Total number of elements in the array
    total_elements = len(array)

    # Calculate the percentage for each value and print
    percentages = {}
    for value, count in value_counts.items():
        percentage = (count / total_elements) * 100
        percentages[value] = percentage
        print(f"{percentage:.2f}% of array values are equal to {value}.")

    return percentages


def plot_dict(data, name, custom_labels = None):
    keys = list(data.keys())
    values = list(data.values())
    
    # Calculate the total to find percentages
    total = sum(values)
    percentages = [(v / total) * 100 for v in values]

    # Creating the bar plot
    fig, ax = plt.subplots(figsize=(10, 5))  # Using subplots to get ax for text placement
    bars = ax.bar(keys, values, color='blue')

    # Adding percentage text on top of each bar
    for bar, percentage in zip(bars, percentages):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f'{percentage:.5f}%', va='bottom', ha='center', fontsize=8)

    # Set x-ticks and x-tick labels
    if custom_labels is not None and len(custom_labels) == len(keys):
        ax.set_xticks(range(len(custom_labels)))
        ax.set_xticklabels(custom_labels)
    else:
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels(keys)
    plt.title("State Of the System")    
    # Save the plot to a file with high resolution
    plt.savefig(name , dpi=300)  # Change dpi for higher or lower quality


def plot_energy(data, name, custom_labels=None):
    keys = list(data.keys())
    values = list(data.values())

    # Creating the bar plot
    fig, ax = plt.subplots(figsize=(10, 5))  # Using subplots to get ax for text placement
    bars = ax.bar(keys, values, color='blue')

    # Adding value text on top of each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.5f}', ha='center', va='bottom')
    
    # Set x-ticks and x-tick labels
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(custom_labels if custom_labels else keys, rotation=45, ha='right')
    plt.title("Energy consummption in each state")
    # Save the plot to a file with high resolution
    plt.savefig(name, dpi=300)  # Save the figure with high quality
    
    # plt.show()  # Show the plot

def calculate_percentage_of_all_values(array):
    # Create a dictionary to count occurrences of each value
    value_counts = {}
    for value in array:
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1

    # Total number of elements in the array
    total_elements = len(array)

    # Calculate the percentage for each value and create a dictionary
    percentages = {value: (count / total_elements) * 100 for value, count in value_counts.items()}
    return percentages

def save_data(data, save_path):
    
    # Create a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(save_path, index=False)