import re
import os
import math
from .logging_config import logger


def reverse_dict(dict):
    return {str(v): k for k, v in dict.items()}

# function to get the last capitalized letters of a string
def get_acronym(s):
    # delete +/- value for ceratizit inserts
    # find "+" and delete everything after it
    if '+' in s:
        s = s[:s.find('+')]
    # if last character is a ')', remove it
    no_brackets = s.replace(')', '').replace('(', ' ')
    s = no_brackets.strip()
    # if last characters "m7", "h6" remove them
    if s[-2:] in ['m7', 'h6', 'h8', 'h7', 'h9', 'h5', 'f8', 'e8', 'H6']:
        s = s[:-2]
    elif s[-3:] in ['js8', 'h10']:
        s = s[:-3]
    elif s[-4:] in ['js15']:
        s = s[:-4]
    elif s[-5:] in ['-0,01', '±0,01', '±0,02', '±0,03', '±0,04', '±0,05']:
        s = s[:-5]
    elif s[-6:] in ['-0,004', '-0,012', '±0,005']:
        s = s[:-6]
    result = re.findall(r'[A-Z0-9]+\s*$', s)
    return result[0].strip() if result else s

def find_number(s: str) -> str:
    # Update the regular expression to capture both integers and floating-point numbers
    pattern = re.compile(r'\b\d+(\,\d+)?')
    match = pattern.search(s)
    return match.group().replace(',', '.') if match else None

# function to drop 'mm' and replace ',' with '.'
def get_float(s: str) -> float:
    if s == 0:
        return float(0)
    try:
        res = s.replace('Threads', '') # remove Threads
        res = res.replace(' 1/"','') # remove 1/" for ceratizit imperial threads
        res = res.replace('mm', '').replace(',', '.') # remove mm and replace , with .
        res = res.replace(' °', '') # remove °
        res = res.replace('grad', '') # remove grad
        res = res.replace('Degrees', '') # remove Degrees
        return float(res)
    except:
        logger.info(f'Error: {s} not parsable to float')
        return float(0)
    
# function to get int from float  
def get_int(s: str) -> int:
    res = None
    if isinstance (s, int):
        return s
    try:
        res = int(get_float(s))
    except:
        res = 0
        logger.info(f'Error: {s} not parsable to int')
    return res
    
# function get a range of floats
# used for partial profile thread inserts
def get_float_range(s: str) -> tuple:
    if s == 0:
        return (float(0), float(0))
    try:
        res = s.replace('Threads', '') # remove Threads
        res = res.replace(' 1/"','') # remove 1/" for ceratizit imperial threads
        res = res.replace('mm', '').replace(',', '.') # remove mm and replace , with .
        return tuple(map(float, res.split('-')))
    except:
        logger.info(f'Error: {s} not parsable to float')
        return (float(0), float(0))

# function to get drill lengh_category (3xD, 5xD, 8xD, 12xD, 20xD) from description
def get_drill_length_category(s: str) -> str:
    pattern = re.compile(r'\b\d+xD\b')
    match = pattern.search(s)
    return match.group() if match else None

# function to get reamer tolerances from description
def get_reamer_tolerances(s):
    # Updated pattern to match tolerances with both commas and periods as decimal separators
    pattern = r'\+\s*([\d,]+(?:\.\d+)?)\s*/\s*([+-]?\d+,\d+|[+-]?\d+\.\d+?)'
    matches = re.findall(pattern, s)
    results = []
    for match in matches:
        upper_tolerance = float(match[0].replace(',', '.'))
        lower_tolerance = float(match[1].replace(',', '.'))
        
        # Ensuring the larger number is first
        if upper_tolerance < lower_tolerance:
            upper_tolerance, lower_tolerance = lower_tolerance, upper_tolerance
        
        results.append(upper_tolerance)
        results.append(lower_tolerance)
        
    return results


# TAP SPECIFIC FUNCTIONS
# fuction to get type of the tap
# works for ceratizit inside scraper
def get_tap_type(s: list) -> str:
    l = list(map(lambda x: x.upper(), s))
    tap_types = {
        'form': ['DSL', 'FORMING', 'FORM', 'FORMERS', 'FORMER'],
        'cut': ['DL', 'CUTTING', 'CUT'],
        'spiral': ['SL', 'SPIRAL']
    }
    for k, v in tap_types.items():
        for i in v:
            if i in l:
                return k
    return None

# fuction to get diameter of the tap from thread type (M4 -> 4, MF14 -> 14)
def get_tap_diameter(s: str, series: str = None) -> float:
    s = s.replace(',', '.') # replace , with .
    # Function to convert fractions to decimal
    def fraction_to_decimal(frac_str: str) -> float:
        numerator, denominator = map(int, frac_str.split('/'))
        return numerator / denominator

    # American thread sizes mapping (in inches)
    american_thread_sizes = {
        0: 0.06,
        1: 0.073,
        2: 0.086,
        3: 0.099,
        4: 0.112,
        5: 0.125,
        6: 0.138,
        7: 0.151,
        8: 0.164,
        9: 0.177,
        10: 0.190,
        11: 0.203,
        12: 0.216
    }

    # Check if it is a metric thread
    if '/' in s or series in ['G', 'BSP']:  # is imperial
        # Regular expression to match a fraction
        match = re.search(r'(\d+/\d+)', s)
        if match:
            # Convert fraction to inches and then to millimeters
            inches = fraction_to_decimal(match.group(1))
            mm = round(inches * 25.4, 3)  # Convert inches to millimeters and round to 3 decimal places
            return mm
    
    # Check if it is an American thread
    if "Nr." in s or series in ['UNC', 'UNF']:
        # Adjusted regular expression pattern
        match = re.search(r'(Nr. )?(\d+)( -)?', s)
        if match:
            thread_number = int(match.group(2))
            if thread_number in american_thread_sizes:
                inches = american_thread_sizes[thread_number]
                mm = round(inches * 25.4, 3)
                return mm
            else:
                raise ValueError(f"American thread number {thread_number} not found in chart")
        
    # Regular expression to match a number (integer or floating point)
    match = re.search(r'(\d+(\.\d+)?)', s)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"No number found in string: {s}")

def tpi_to_pitch(tpi: int) -> float:
    if  not int(tpi):
        return tpi
    try:
        return round(25.4 / tpi, 3)
    except Exception as e:
        logger.error(f'Error: {e}')
        return 0

# CUTTER SPECIFIC FUNCTIONS
# function to get ISO code from description
# SDJCL 2525M 11 -> SDJCL
def get_cutter_iso_code(s: str) -> str:
    pattern = re.compile(r'\b[A-Z]+\d*\b')
    match = pattern.search(s)
    res = match.group() if match else None
    return res

def normalize_boring_iso_code(s: str) -> str:
    # Standart ISO format for borign bars is A16R SCLCR 09"
    # Step 1: Replace "R/L" with "R"
    s = s.replace("R/L", "R")

    # Step 2: Use regex to find letters, digits, and spaces
    letters = ''.join(re.findall(r'[A-Za-z]', s))
    digits = ''.join(re.findall(r'\d+', s))

    # Step 3: Arrange them to get the normalized string
    # Adding spaces explicitly to maintain the pattern "LDDLSLLLLLSDD"
    normalized = f"{letters[:1]}{digits[:2]}{letters[1:2]} {letters[2:7]} {digits[2:4]}"
    
    return normalized

# COLLET SPECIFIC FUNCTIONS
# function to get collet type from description
def get_collet_type(s: str) -> str:
    collete_types = ['ER25', 'ER32', 'ER16', 'ER11', 'ER40', 'ER20', 'ER8']
    for i in collete_types:
        if i in s.replace(' ', ''):
            return i
    return None

# function to data from ceratizit specification
def get_from_ceratizit_specification(s: str) -> str:
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_tur_abstechen_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_spanmittel_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_tur_schnitt-010_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_cbmd-m1_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_coatn-ctp1340_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_hm_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_op-tur-part-off_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_op-tur-groove-external_all_pim
    # https://cdn.plansee-group.com/is/image/planseemedia/sym_hin_all_gx_all_pim
    u = s[64:]
    s = u[:u.find('_')]
    return s

def get_file_path(filename):
    # Get the directory where the calling script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define relative path to the data files
    relative_path = ''  # Adjust this as needed

    # Construct the full path
    file_path = os.path.join(script_dir, relative_path, filename)
    
    return file_path

# function to find inch value in string
def find_inch(s: str) -> str:
    pattern = re.compile(r'\b\d+/\d+')
    match = pattern.search(s)
    return match.group() if match else None

# fuction to find mm value in string
# ER-spännhylsa för gängtappar 3,5 mm -> 3.5
def find_mm(s: str) -> float:
    pattern = r'(\d+(\.\d*)?) mm'
    match = re.search(pattern, s.replace(',', '.'))
    if match:
        value = match.group(1)
        try:
            return float(value)
        except:
            logger.info(f'Error: {match.group()} not parsable to float')
            return None
    else:
        return None

# function to convert inch to mm
def inch_to_mm(inch: str, digit=2) -> float:
    inch_nominal_list = [
        '1/16',
        '5/64',
        '3/32',
        '7/64',
        '1/8',
        '5/32',
        '3/16',
        '7/32',
        '1/4',
        '9/32',
        '5/16',
        '11/32',
        '3/8',
        '13/32',
        '7/16',
        '15/32',
        '1/2',
        '17/32',
        '9/16',
        '19/32',
        '5/8',
        '21/32',
    ]
    if inch in inch_nominal_list:
        inch_float = float(inch.split('/')[0]) / float(inch.split('/')[1])
        return  round(inch_float * 25.4, digit)
    else:
        try:
            inch_float = float(inch.split('/')[0]) / float(inch.split('/')[1])
            return round(inch_float * 25.4, digit)
        except:
            logger.info(f'Error: {inch} not parsable to float')
            return None
        
# round float to 0.5
def round_to_half(number) -> float:
    """Rounds a number based on custom rules.
    
    - Rounds down to the nearest whole number if the fractional part is less than 0.4.
    - Rounds to *.5 if the fractional part is between 0.4 and 0.6 (inclusive).
    - Rounds up to the nearest whole number if the fractional part is greater than 0.6.
    
    Parameters:
    - number (float): The number to round.
    
    Returns:
    - float: The rounded number.
    """
    int_part, frac_part = divmod(number, 1)
    
    if frac_part < 0.4:
        return math.floor(number)
    elif 0.4 <= frac_part <= 0.6:
        return int_part + 0.5
    else:
        return math.ceil(number)