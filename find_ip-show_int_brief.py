# script to search for the entered ip on the equipment in the output of the "show ip interface brief" command
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException
from tabulate import tabulate
from datetime import datetime
import getpass
from os import path
import re

device_types = {'mikrotik_routeros': '1', 'cisco_ios': '2', 'hp_procurve': '3'}

# Function for connecting to equipment via ssh:
def connection(selected_device, host, username, password):

    device = {
        'device_type': selected_device,
        'host': host,
        'username': username,
        'password': password,
        'port': '22',
        'global_cmd_verify': False,
    }
    try:
        connect_to_device = ConnectHandler(**device)
        return connect_to_device
    except NetMikoTimeoutException: # checking for an incorrectly entered ip
        return 'FalseIP'
    except AuthenticationException: # checking for an incorrectly entered log/pass
        return 'FalseLogPass'


# Function to find and return the type of equipment (key) according to the selected number (value). For example, enter the number 1, which means the value "mikrotik_routeros" will be returned
def search_device_type(selected_device, device_types):
    return list(device_types.keys())[list(device_types.values()).index(selected_device)]

def input_ip():
    return input('Enter the ip to be found: ')

def check_ip(ip):
    return re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)

# Function to search for ip in the output variable (it contains the output of the "show ip interface brief" command):
def find_ip(ip):
    check_ip(ip)
    find_ip = output.find(str(ip)) # If "find" did not find the desired value, then it will return "-1", and if found, it will return some positive number, so I just check for equality with "-1"
    if find_ip != -1:
        return 'IP address found'
    return 'IP address not found'

def file_header():
    writing = open('find_ip.csv', 'a')
    writing.write('Datetime' + ',' + 'desired ip' + ',' + ' is found' + ',' + 'ip device' + ',' + 'equipment type' + '\n')
    writing.close()

def writing_to_file(ip, result_find_ip, selected_device, host):
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    if path.exists('find_ip.csv') is False:
        file_header()
    writing = open('find_ip.csv', 'a')
    writing.write(now + ',' + ip + ',' + result_find_ip + ',' + host + ',' + selected_device + '\n')
    writing.close()


# LOGIC OF THE SCRIPT:

# Displaying the equipment type selection in the form of a table (the data for compiling the table is taken from the device_types dictionary, which is located at the beginning of the code)
print(tabulate(device_types.items(), headers=['Equipment type', 'Choose'], tablefmt="grid"))

selected_device = search_device_type(input('Select a device (enter the value from the second column corresponding to the desired device): '), device_types)

# Connecting to the equipment and executing the "show ip interface brief" command, the output is also written to the output variable:
while True: # the loop is needed to give the opportunity to enter data to connect again when an error occurs
    # Entering data for connecting to equipment:
    host = str(input('ip device: '))
    username = str(input('login: '))
    password = getpass.getpass('password: ')
    if connection(selected_device, host, username, password)=='FalseIP':
        print('Incorrect data entered (equipment ip)')
    elif connection(selected_device, host, username, password)=='FalseLogPass':
        print('Incorrect data entered (login or password)')
    else: 
        output = connection(selected_device, host, username, password).send_command('show ip interface brief')
        print(output)
        break

# Enter and validate the ip to be found in the output of the "show ip interface brief" command (the loop will break if the check_ip() function does not return None:
while True:
    ip = input_ip()
    if check_ip(ip) is None:
        print('Invalid ip entered, please try again.')
    else:
        break

# Search for the entered ip in the output of the "show ip interface brief" command:
result_find_ip = find_ip(ip)
# Display the result:
print(result_find_ip)

writing_to_file(ip, result_find_ip, selected_device, host)