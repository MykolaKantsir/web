import dateutil.parser
import pytz
from datetime import date as this_date
from datetime import datetime, timedelta, date
from django.utils.timezone import make_aware, is_aware
from pytz import timezone
from os import path, mkdir, listdir
from re import match
from ..testing_variables_defaut import path_to_save, offline_path_device

# Additional functions

# function which retunt datetime after timedelta
# counts only WORKING TIME
def when_work_will_end(time_from : datetime, after : timedelta) -> datetime:
    if after == timedelta(hours=0, minutes=0, seconds=0):
        return time_from
    one_shift = timedelta(hours=8)
    # initial values have to be set in UTC timezone
    start_time = 6 # hours 7 AM in Stockholm
    end_time = 15 # hours 4 PM in Stockholm
    breakfast = 9 # hours 10 AM in Stockholm
    break_breakfast = 30 # duration of breakfast in minutes
    lunch = 13 # hours 2 PM in Stockholm
    break_lunch = 30 # duration of lunch in minutes
    isCheckedForBreaks = False # variable for runnig checking only once, changes to 'True' on first run

    # function to return begining of shift
    def get_start(this_date: datetime) -> datetime:
        res = datetime(this_date.year, this_date.month, this_date.day, start_time, 0, 0)
        return res

    # function to return end of shift
    def get_end(this_date : datetime) -> datetime:
        res = datetime(this_date.year, this_date.month, this_date.day, end_time, 0, 0)
        return res
    
    # fuction remove timezones, miliseconds and microseconds
    def remove_timezones(this_date : datetime) -> datetime:
        res = datetime(this_date.year, this_date.month, this_date.day, this_date.hour, this_date.minute, this_date.second)
        return res

    # fuction return start of the closest shift
    def to_closest_shift(this_date : datetime) -> datetime:
        # is between 00:00 and 07:00 start of shift
        if this_date.time().hour < start_time:
            # move to start of shift
            return get_start(this_date)
        # if between end of shift 16:00 and 23:59
        if this_date.time().hour >= end_time:
            # move to start of shift next day
            return get_start(this_date) + timedelta(days=1)
        # if recieved time is in working hours
        if this_date.time().hour >= start_time and this_date.hour < end_time:
            return this_date

    # fuction return start of the closest workday
    def to_closest_workday(this_date : datetime) -> datetime:
        #print(f'end day is {this_date.strftime("%A")}')
        monday = 7 - this_date.weekday()
        # if monday is None:
        #     print(f'monday is none weekday {this_date.weekday()}')
        over_shift = get_over_time(this_date)
        this_date = to_closest_shift(this_date)
        this_date += timedelta(days=monday)
        this_date += over_shift  
        #print(f'moved to {this_date.strftime("%A")}')
        #print(f'start day is {this_date} : {this_date.strftime("%A")}')
        return this_date

    # function to return time passed after end of shift
    def get_over_time(this_date : datetime) -> timedelta:
        if this_date.time().hour >= end_time:
            result = remove_timezones(this_date) - get_end(this_date)
            return result
        if this_date.time().hour < start_time:
            result = remove_timezones(this_date) - get_end(this_date-timedelta(days=1))
            return result
        else:
            #print(f'get_over_time {this_date} returned 0')
            return timedelta(0)

    # adds 30 minutes if after breakfast or after lunch
    def check_breaks(this_date : datetime) -> datetime:
        nonlocal isCheckedForBreaks
        # run only once
        if not isCheckedForBreaks:
            # check if the end working hour is during breakfast    
            if this_date.hour >= breakfast:
                this_date += timedelta(minutes=break_breakfast)
                #print(f'Work ends during breakfast, moved to {this_date}')
            if this_date.hour >= lunch:
                this_date += timedelta(minutes=break_lunch)
                #print(f'Work ends during lunch, moved to {this_date}')
            isCheckedForBreaks = True
        return this_date

    # function to check if the time and day is valid
    def is_valid(this_date : datetime) -> bool:
        result = True
        if this_date.time().hour < start_time: 
            #print(f'Too early {this_date.time()}')
            result = False
        if this_date.time().hour >= end_time:  
            #print(f'Too late {this_date.time()}')
            result = False
        if this_date.weekday() > 5:  
            #print(f'Weekend {this_date.weekday()} : {this_date.strftime("%A")}')
            result = False
        # if result:
        #     print('Valid date')
        return result

    # recursive function to correct time and day
    def check_and_correct(this_date : datetime) -> datetime:
        #print(f'Checking {this_date} : {this_date.strftime("%A")}')
        # check if the end working hour is not after shift ends
        if this_date.time().hour >= end_time:
            over_shift = get_over_time(this_date)
            this_date = to_closest_shift(this_date)
            this_date += over_shift  
            #print(f'Work ends after shift, moved to {this_date}')
        # check if the end working hour is not before shift starts
        if this_date.time().hour < start_time:
            over_shift = get_over_time(this_date)
            this_date = get_start(this_date)
            this_date += over_shift             
            #print(f'Work ends before shift, moved to {this_date}')
        this_date = check_breaks(this_date)
        # check if end day is not Saturday or Sunday
        if this_date.weekday() >= 5:
            this_date = to_closest_workday(this_date)
        if not is_valid(this_date):
            this_date = check_and_correct(this_date)
        #print(f'Checked {this_date} : {this_date.strftime("%A")}')
        return this_date
    
    #################################################################
    # THIS BLOCK CAN SHIFT STARTING HOUR TO CLOSEST WORKING SHIFT
    #################################################################
    # # check if starting day is not Saturday or Sunday
    # if time_from.weekday() >= 5:
    #     #print(f'start day is {time_from.strftime("%A")}')
    #     monday = 7 - time_from.weekday()
    #     time_from = datetime(time_from.year, time_from.month, time_from.day, start_time, 00, 00)
    #     time_from += timedelta(days=monday)
    #     #print(f'moved to {time_from.strftime("%A")}')
    #     #print(f'start day is {time_from} : {time_from.strftime("%A")}')

    # # check if the starting working hour is not before shift starts
    # if time_from.time().hour < start_time:
    #     time_from = datetime(time_from.year, time_from.month, time_from.day, start_time, 00, 00)
    #     time_from += timedelta(hours=(start_time-time_from.time().hour))
    #     #print(f'Work starts before shift moved to {time_from}')
        
    # # check if the starting working hour is not after shift ends
    # if time_from.time().hour > end_time:
    #     time_from = datetime(time_from.year, time_from.month, time_from.day, start_time, 00, 00)
    #     time_from += timedelta(days=1)
    #     #print(f'Work starts after shift, moved to {time_from}')
    
    # calculated delta
    working_days_to_add = after.total_seconds()//one_shift.total_seconds()
    if after.total_seconds()%one_shift.total_seconds() == 0:
        working_days_to_add -=1
    after -= one_shift*working_days_to_add
    
    # counts full shifts
    current_date = time_from
    while working_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        working_days_to_add -= 1
    current_date += after
    
    # hours adding
    current_date = check_and_correct(current_date)
    current_date = convert_to_local_time(current_date)
    return current_date

# round timedelta to seconds
def round_to_seconds(this_timedelta: timedelta) -> timedelta:
    # Retrieve total seconds, round it to the nearest whole number, and create a new timedelta
    total_seconds = this_timedelta.total_seconds()
    rounded_seconds = round(total_seconds)
    res = timedelta(seconds=rounded_seconds)
    return res

# returns the text of the offline xml file
def get_offline_file(machine : str, file_number : int, date : str) -> str:
    subfolder = str(file_number//500*500) + '-' + str(500*(file_number//500+1)-1)
    today = date
    file_name = f'{str(file_number)}_{machine}.xml'
    document_path = path.join(offline_path_device, today, machine, subfolder, file_name)
    # check if offline file exists
    if not path.exists(document_path):
        result = ""
    else:
        with open (document_path, 'r') as xml_file:
            result = xml_file.read()         
    return result

# function to save rough xml response
def save_rough_response(xml_text : str, machine, last_file_number=None) -> None:
    date = this_date.today()
    # checks if today's path exist, creates if not
    def check_and_create(target_path: path):
        if not path.exists(target_path):
            mkdir(target_path)
    # checks todays date
    check_and_create(path.join(path_to_save, str(date)))
    # checks machine name folder
    machine_foder = machine.get_todays_rough_data_folder()
    check_and_create(machine_foder)
    # function to create subfolders (0-499)
    def create_sub(num):
        subfolder = str(num//500*500) + '-' + str(500*(num//500+1)-1)
        subfolder_full_path = path.join(machine_foder, subfolder)
        check_and_create(subfolder_full_path)
        return subfolder_full_path
    
    def get_last_file_number(this_machine_folder):
        
        if len(listdir(this_machine_folder)) == 0:
            return 0

        # function to get latest directoty in machine directory
        def get_last_folder(this_folder : str) -> str:
            dirs = []
            for d in listdir(this_folder):
                if path.isdir(path.join(this_folder, d)) or path.isfile(path.join(this_folder, d)):
                    dirs.append(path.join(this_folder, d))
            dirs.sort(key=lambda x: path.getatime(x), reverse=True)
            if len(dirs) > 0:
                return dirs[0]
            else: return this_folder
        create_sub(last_file_number)
        last_folder = get_last_folder(this_machine_folder)
        last_file = get_last_folder(last_folder).split('\\')[-1]
        print(last_file)
        try:
            number = int(match(r'\b\d+', last_file).group(0))
        except: number = 0
        return number
    
    last_offline_file = last_file_number if last_file_number != None else get_last_file_number(machine_foder) 
    final_folder = create_sub(last_offline_file)


    file_name = path.join(final_folder, f'{str(last_offline_file)}_{machine.name}.xml')
    last_offline_file += 1
    with open (file_name, 'w') as file:
        file.write(xml_text)
    return last_offline_file

# function to save list as text
def list_to_text(this_list : list) -> str:
    return ','.join(this_list)

# function to get list from text
def text_to_list(this_text : str) -> list:
    return this_text.split(',')

# function to serialize timedelta
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (timedelta)):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

# funcion to check if request is sent from ajax
def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'

# function to clean the nc program name
def clean_nc_program_name(name: str) -> str:
    """Removes specified symbols only from the beginning 
    and the end of the nc program name, while ignoring the '.NC' extension."""
    # Symbols to remove
    symbols_to_remove = '*-'
    extention = '.NC'
    name_capital = name.upper()
    
    # Check if '.nc' is present at the end
    is_nc_present = name_capital.endswith(extention)
    
    # If '.nc' is present, remove it before cleaning
    if is_nc_present:
        name = name_capital[:-3]  # Remove the last 3 characters, which are '.nc'
    
    # Strip symbols from both ends
    new_name = name.strip(symbols_to_remove)
    
    # Add '.nc' back if it was originally there
    if is_nc_present:
        new_name += extention
    
    return new_name

# function to get machine state from database
# machine - Machine object, not specified because of circular import
def machine_current_database_state(machine) -> dict:
    status = machine.status
    current_machine_time = machine.current_machine_time
    remain_time = machine.remain_time
    last_cycle_duration = machine.last_cycle_duration
    this_cycle_duration = machine.this_cycle_duration
    m30_counter2 = machine.m30_counter2
    m30_counter1 = machine.m30_counter1
    active_nc_program = machine.active_nc_program
    current_tool = machine.current_tool
    mode = machine.mode
    last_start = machine.last_start
    inactive_time = machine.inactive_time
    cur_state = {
        'status': status,
        'remain_time': remain_time,
        'last_cycle_duration': last_cycle_duration,
        'this_cycle_duration': this_cycle_duration,
        'current_machine_time': current_machine_time,
        'm30_counter2': m30_counter2,
        'm30_counter1': m30_counter1,
        'active_nc_program': active_nc_program,
        'current_tool': current_tool,
        'mode': mode,
        'last_start': last_start,
        'inactive_time': inactive_time,
    }
    return cur_state

# function to format time from ISO 8601 (P0DT00H00M00.000S) to hh:mm:ss.sss
def convert_time_django_javascript(state : dict) -> dict:
    for key in state:
        if isinstance(state[key], timedelta):
            state[key] = str(state[key])
        if isinstance(state[key], datetime):
            state[key] = convert_to_local_time(state[key]).strftime("%H:%M:%S")
    return state

def convert_to_local_time(utc_dt):    
    # Stockholm timezone
    local_tz = pytz.timezone('Europe/Stockholm')

    # Check if utc_dt is already aware and in UTC
    if utc_dt and not is_aware(utc_dt):
        # make the datetime object aware in UTC if it's not already
        aware_utc_dt = make_aware(utc_dt, pytz.utc)
    else:
        aware_utc_dt = utc_dt  # already aware or None

    # Convert to local timezone (Stockholm in this case)
    if aware_utc_dt:
        local_dt = aware_utc_dt.astimezone(local_tz)
        return local_dt
    else:
        return utc_dt

# function to convert time recieved in machine response format to (MM:SS)
def convert_time(time: str) -> str:
    # convert time and remove timezone
    #result_time = dateutil.parser.isoparse(time).replace(tzinfo=pytz)
    result_time = dateutil.parser.isoparse(time).astimezone(timezone('Europe/Stockholm'))
    return result_time

# function to convert time (HH:MM:SS) to timedelta
def timedelta_from_string(string_duration : str) -> timedelta:

    # Parse the string and convert it to a datetime object
    parsed_time = datetime.strptime(string_duration, '%H:%M:%S')

    # Extract the hours, minutes, and seconds from the datetime object
    hours = parsed_time.hour
    minutes = parsed_time.minute
    seconds = parsed_time.second

    # Create a timedelta object using the extracted values
    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    return duration

# function to normalize tool sequence
def normalize_tool_sequence(sequence_str, double_tool=False):
    if sequence_str == '':
        return ''
    # Split the string into individual tools and remove leading zeros
    tools = sequence_str.split(',')
    if double_tool:
        # Assuming double_tool means each tool is represented by a four-digit code
        normalized_tools = [tool.zfill(4) for tool in tools]
    else:
        # Each tool is a regular one or two-digit code, remove leading zeros
        normalized_tools = [str(int(tool)) for tool in tools]
    return ','.join(normalized_tools)

# functon to present timedelta in HH:MM:SS format
def timedelta_to_HHMMSS(timedelta: timedelta) -> str:
    # Extract the hours, minutes, and seconds from the timedelta object
    hours = timedelta.seconds // 3600
    minutes = (timedelta.seconds % 3600) // 60
    seconds = timedelta.seconds % 60
    # Format the time as a string in HH:MM:SS format
    formatted_time = f'{hours:02}:{minutes:02}:{seconds:02}'
    return formatted_time

# function to convert isotime to datetime
def parse_isoformat(date_string):
    """Parse ISO format date string to datetime object."""
    return datetime.fromisoformat(date_string)


# function to update one machine
# machine - Machine object, not specified because of circular import
def update_machine() -> None:
    pass

# function to update machine state
# state - Machine_state object, not specified because of circular import
def update_machine_state() -> None:
    pass