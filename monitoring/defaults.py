
from datetime import datetime, timedelta, date
import pytz

# datetime defaults
stockholm = pytz.timezone('Europe/Stockholm')
midnight_january_first = datetime(2022,1,1,7,00,00, tzinfo=stockholm)
duration_zero = timedelta(0)
duration_one_minute = timedelta(minutes=1)
duration_one_hour = timedelta(hours=1)
january_the_first = date(2022,1,1)

# active program default
nc_program_default = 'default.NC'

# state default
state_default = {
        'status': 'STOPPED',
        'remain_time': timedelta(0),
        'last_cycle': timedelta(0),
        'this_cycle': timedelta(0),
        'current_machine_time': january_the_first,
        'm30_counter2': 0,
        'm30_counter1': 0,
        'active_nc_program': nc_program_default,
        'mode': 'AUTOMATIC',
        'current_tool': '0'}


# Machine default
default_IP = "0.0.0.0"

# Machine Unnonwn
machine_uknown = "Unknown"
machine_network_name_unknown = "Unknown network name"

# JOB
# Default job project
job_project_default = 'Unknown poject'
job_nc_program_defautl = 'T.nc'

# CYCLE
# Default cycle time
warm_up_cycle_duration = timedelta(minutes=16)