import socket
from datetime import date
from os import path

# Change to true if you work with saved requests or test without request
work_offline =  True

today_offline = date(year=2022, month=12, day=18)
today_offline_string = str(today_offline)

# Frequency of updating in seconds
conection_frequency = 4

# Proxy server varibles
proxy_ip = '127.0.0.1'
proxy_port = 64000

# Django server variables
django_ip = '192.168.112.145' if socket.gethostname() == 'D-M006' else '192.168.0.105'
django_port = 8000


file_number = 0

# Machine names for offline testing
machine_xml_names = {
    '202':'202-VF2SS',
    '203':'203-VF2SS',
    '204':'204-VF2SS',
    '205':'205-VF2SS',
    '206':'206-UMC500',
    '301':'301-ST20Y',
    }

# Get the absolute path of the script file
script_directory = path.dirname(path.abspath(__file__))

# Traverse up the directory hierarchy to the desired parent directory
#parent_directory = path.dirname(path.dirname(path.dirname(path.dirname(script_directory))))
#parent_directory = path.join('D:\\')
parent_directory = path.join('E:\\')

# Variables to save rough XML response
path_to_save = path.join(parent_directory, 'mtconnect rough data')

# Variable to get the next offline XML file in response to machine MTConnect request
offline_path_device = path.join(parent_directory, 'mtconnect rough data')

# Variable to save state_changes_csv file
path_to_save_csv = path.join(parent_directory, 'states changes csv data')
