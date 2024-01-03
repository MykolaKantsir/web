import re
import os
import math
from inventory.choices import OrderStatus, orderStatusChangingOrder
from inventory.choices import Manufacturer
from .logging_config import logger


# Class to identify manufacturer from barcodes
class ManufacturerIdentifier:
    """
    A class to identify manufacturer from barcodes using various methods.
    It tries methods in the following order:
    1. Prefix matching
    2. Heuristic-based identification
    3. Machine learning model prediction
    """

    def __init__(self):
        # Load resources
        self.unique_prefixes = {
            'hoffmann' : {
                'characters' : 6,
                'prefixes' : [
                    '404519',
                    '406240',
                    '203054',
                    '496066',
                    '205000',
                    '404636',
                    '402077',
                    '401328',
                    '403061',
                    '401613',
                    '403772',
                    '403074',
                    '401920',
                    '426071',
                    '494636',
                    '403145',
                    '763004',
                    '404612',
                    '692390',
                    '405919',
                    '137150',
                    '425026',
                    '404732',
                    '739139',
                    '500882',
                    '400300',
                    '425036',
                    '405427',
                    '541131',
                    '500511',
                    '731255',
                    '404671',
                    '101114',
                    '729000',
                    '400921',
                    '613548',
                    '313437',
                    '400189',
                    '048011',
                    '426049',
                    '403707',
                    '900317',
                    '500480',
                    '401012',
                    '761073',
                    '726680',
                    '425015',
                    '501259',
                    '541238',
                    '402493',
                    '497536',
                    '732254',
                    '100764',
                    '324542',
                    '076490',
                    '400819',
                    '401620',
                    '426002',
                    '805552',
                    '405798',
                    '450798',
                    '033552',
                    '403110',
                    '571520',
                    '731061',
                    '401875',
                    '406726',
                    ],
                },
            'guehring' : {
                'characters' : 6,
                'prefixes' : [
                    '404984',
                    '403109',
                    ],
                },
            'ceratizit' : {
                'characters' : 5,
                'prefixes' : [
                    '54611',
                    '10113',
                    '70779',
                    '53554',
                    '53562',
                    '70258',
                    '10200',
                    '50991',
                    '23120',
                    '23240',
                    '10522',
                    '54059',
                    '53520',
                    '53519',
                    '54006',
                    '50615',
                    '52211',
                    '53518',
                    '52806',
                    '50609',
                    '52345',
                    '54072',
                    '50975',
                    '54610',
                    '53615',
                    '54590',
                    '52802',
                    '53616',
                    '52942',
                    '50958',
                    '53643',
                    '52786',
                    '52784',
                    '52932',
                    '52349',
                    '52230',
                    '53613',
                    '52228',
                    '53569',
                    '53611',
                    '53639',
                    '50944',
                    '52158',
                    '52159',
                    '50990',
                    '52050',
                    '52804',
                    '53052',
                    '50803',
                    '53053',
                    '53012',
                    '53050',
                    '53003',
                    '54700',
                    '11705',
                    '11715',
                    '11603',
                    '10110',
                    '10107',
                    '10235',
                    '10130',
                    '10171',
                    '10700',
                    '11702',
                    '11704',
                    '11629',
                    '10772',
                    '10788',
                    '10270',
                    '10710',
                    '10781',
                    '11620',
                    '11623',
                    '11700',
                    '11770',
                    '11706',
                    '10225',
                    '10161',
                    '10103',
                    '10703',
                    '10532',
                    '40140',
                    '23114',
                    '23124',
                    '23814',
                    '23162',
                    '23160',
                    '23026',
                    '23810',
                    '23122',
                    '22163',
                    '23112',
                    '23410',
                    '23372',
                    '22107',
                    '10913',
                    '10912',
                    '10880',
                    '70688',
                    '70773',
                    '70780',
                    '70663',
                    '70845',
                    '70844',
                    '71280',
                    '70716',
                    '70892',
                    '71282',
                    '73104',
                    '51016',
                    '73322',
                    '51113',
                    '51055',
                    '53008',
                    '53007',
                    '51051',
                    '50876',
                    '50477',
                    '93090',
                    '10923',
                    '10830',
                    '10822',
                    '76250',
                    '70248',
                    '75210',
                    '76252',
                    '76135',
                    '76132',
                    '75011',
                    '76256',
                    '70263',
                    '71163',
                    '75213',
                    '75304',
                    '76258',
                    '75305',
                    '76246',
                    '76136',
                    '76263',
                    '76134',
                    '75014',
                    '70270',
                    '76146',
                    '76138',
                    '75006',
                    '76255',
                    '76277',
                    '71330',
                    '71189',
                    '71331',
                    '70282',
                    '70277',
                    '70280',
                    '76288',
                    '70167',
                    '76131',
                    '71228',
                    '71264',
                    '71220',
                    '71272',
                    '71224',
                    '71222',
                    '70351',
                    '70363',
                    '70349',
                    '70342',
                    '70346',
                    '70350',
                    '80950',
                    '83535',
                    '82483',
                    '83271',
                    '83272',
                    '83453',
                    '83950',
                    '85299',
                    '82415',
                    '82310',
                    '82315',
                    '84578',
                    '84596',
                    '82684',
                    '84580',
                    '82685',
                    '84581',
                    '82686',
                    '70950',
                    '71950',
                    '10950',
                    '73082',
                    '80393',
                    '83357',
                    '10773',
                    '70748',
                    '73004',
                    '73012',
                    '73004',
                    '76276',
                    '50477',
                    '75022',
                    '75310',
                    '75023',
                    '70193',
                    '70260',
                    '84950',
                    '70263',
                    '75305',
                    '76251',
                    '70343',
                    '73314',
                    '73520',
                    '53015',
                    '50234',
                    '50886',
                    '50451',
                    '53001',
                    '54063',
                    '50955',
                    '53612',
                    '50965',
                    '53524',
                    '40150',
                    '23010',
                    '22501',
                    '50965',
                    '50591',
                    '10718',
                    '23144',
                    '10523',
                    '52291',
                    '50900',
                    '11021',
                    '53587',
                    '50901',
                    '10170',
                    '10791',
                    '11786',
                    '50815',
                    '52346',
                    ],
                },
            'sandvik' : {
                'characters' : 5,
                'prefixes' : [
                        '73232',
                        '10378',
                        '26537',
                        '12090',
                        '12384',
                        '26138',
                        '12160',
                        '10529',
                        '25961',
                        '12055',
                        '26770',
                        '10001',
                        '12460',
                        '12373',
                        '10503',
                        '12442',
                        '25857',
                        '12374',
                        '12324',
                        '11588',
                        '11170',
                        '12375',
                        '12358',
                        '12379',
                        '12356',
                        '12360',
                        '12313',
                        '11093',
                        '12290',
                        '26532',
                        '26426',
                        '25966',
                        '10069',
                        '12277',
                        '12449',
                        '12286',
                        '10979',
                        '10335',
                        '10284',
                        '10197',
                        '10164',
                        '11256',
                        '11947',
                        '11778',
                        '11367',
                        '26539',
                        '26433',
                        '26427',
                        '12177',
                        '12179',
                        '12237',
                        '12343',
                        '12368',
                        '12357',
                        '11313',
                        '11192',
                        '11370',
                        '11094',
                        '12445',
                        '12443',
                        '12357',
                        '12301',
                        '10896',
                        '12205',
                        '26261',
                        '25847',
                        '26350',
                        '12237',
                        '25860',
                        '12441',
                        '12342',
                ],
                },
            'phorn' : {
                'characters' : 4,
                'prefixes' : [
                    'LA10',
                    'S223',
                    'RS11',
                    '3110',
                    'SH11',
                    'SB10',
                    'B105',
                    'R105',
                    'R111',
                    'L105',
                    'N105',
                    ],
                },    
            'tungaloy' : {
                'characters' : 3,
                'prefixes' : [
                    '056',
                    '068',
                    '069',
                    '033',
                    '067',
                    '074',
                    '043',
                    '070',
                    ],
                },
        }

    def find_manufacturer(self, barcode):
        """
        Tries to identify the manufacturer based on known prefixes.
        """
        prefix_lengths = [6, 5, 4, 3]  # Adjust based on actual lengths in your data
        for manufacturer, details in self.unique_prefixes.items():
            char_length = details['characters']
            if char_length in prefix_lengths:
                for prefix in details['prefixes']:
                    if barcode.startswith(prefix):
                        return manufacturer, "prefix"
        return None, None

    def identify_manufacturer(self, barcode):
        """
        Tries to identify the manufacturer based on heuristic rules.
        """
        manufacturer = None
        # Example heuristic rules, replace with actual logic
        if barcode.startswith("0"):
            manufacturer = 'tungaloy'
        if re.match(r"^\d{6}\s", barcode):
            manufacturer = 'hoffmann'
        if re.match(r"^[RLN]\d", barcode):
            manufacturer = 'phorn'
        # ... Add other heuristics as necessary
            
        if manufacturer:
            return manufacturer, "heuristic"
        return None, None


    def identify(self, barcode):
        """
        Identifies the manufacturer by sequentially trying all methods.
        """
        order_of_methods = [
            self.find_manufacturer,
            self.identify_manufacturer,
            ]
        for method in order_of_methods:
            manufacturer, method_used = method(barcode)
            if manufacturer:
                return manufacturer, method_used
            
        # If all methods fail, return a message indicating such
        return None, "unknown"

# Class to get manufacturer's search page and xpath for the search field
class ManufacturerSearchPage:
    MANUFACTURER_INFO = {
        Manufacturer.HOFFMANN.value : {
            'homepage': 'https://www.hoffmann-group.com/SE/sv/ravema/', 
            'search_bar_xpath': '//*[@id="search"]',
            'search_button_xpath': '',
            'first_search_result_xpath': '//*[@id="autosuggest-products"]/ul/li[1]',
            'cookie_button_xpath': '//*[@id="privacy-cat-modal"]/div/div/div[3]/div[1]/div/button[1]',
            'barcode_xpath': '//*[@id="technicalData"]/table[2]/tbody/tr[2]/td[3]/input',
            'code_xpath': '//*[@id="technicalData"]/table[2]/tbody/tr[1]/td[3]/input',
            'picture_xpath': '//*[@id="productImagesSlider"]/div/figure[1]/a/div/img',
            'description_xpath': '/html/body/div[1]/main/section[2]/div[1]/div/div/div/div[1]/div[2]/h1',
            },
        Manufacturer.GUEHRING.value : {
            'homepage': 'https://webshop.guehring.se/',
            'search_bar_xpath': '//*[@id="proLineSearchQuery"]',
            'search_button_xpath': '',
            'first_search_result_xpath': '//*[@id="proline-autocomplete-store-search"]/div[2]/div[2]/div/div[1]',
            'first_search_result_xpath': '//*[@id="proline-autocomplete-store-search"]/div[2]/div[2]/div/div[1]',
            'cookie_button_xpath': '//*[@id="uc-center-container"]/div[2]/div/div[1]/div/button[4]',
            'barcode_xpath': '//*[@id="maincontent"]/div[3]/div/div[3]/div[1]/div[2]/div',
            'code_xpath': '//*[@id="maincontent"]/div[3]/div/div[3]/div[1]/div[1]/div',
            'picture_xpath': '//*[@id="maincontent"]/div[3]/div/div[5]/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/img',
            'description_xpath': '//*[@id="maincontent"]/div[1]/h1/span',
            },
        Manufacturer.CERATIZIT.value : {
            'homepage': 'https://cuttingtools.ceratizit.com/se/en.html',
            'search_button_xpath': '/html/body/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/button',
            'search_bar_xpath': '/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div/div/input',
            'first_search_result_xpath': '/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div/div/div/div/div/ul/li[1]/div[1]/div[1]/div',
            'cookie_button_xpath': '//*[@id="truste-consent-button"]',
            'barcode_xpath': '/html/body/div[3]/div[6]/div/div[1]/div[2]/span',
            'code_xpath': '/html/body/div[3]/div[6]/div/div[1]/div[2]/span',
            'picture_xpath': '//*[@id="expandedImg"]',
            'description_xpath': '/html/body/div[3]/div[6]/div/div[2]/div[1]/div[2]/div[1]',
            },
        Manufacturer.SANDVIK.value : {
            'homepage': 'https://www.sandvik.coromant.com/sv-se',
            'search_bar_xpath': '//div[contains(@class, "coromant-main-search")]//input[contains(@class, "main-search-box") and @type="text"]',
            'search_button_xpath': '',
            'first_search_result_xpath': '',
            'cookie_button_xpath': '//*[@id="onetrust-accept-btn-handler"]',
            'barcode_xpath': '//*[@id="searchcontent"]/div[1]/div/div[3]/product-price-information-add-to-cart-v5/div/div[1]/product-details-codes-v5/div[4]',
            'code_xpath': '//*[@id="searchcontent"]/div[1]/div/div[1]/product-header-v5/div/div[1]/h1',
            'picture_xpath': '//*[@id="searchcontent"]/div[1]/div/div[2]/div/product-details-image-gallery-v5/div/div[1]/div/img',
            'description_xpath': '//*[@id="searchcontent"]/div[1]/div/div[1]/product-header-v5/div/div[1]/div/h5',
            },
        Manufacturer.PHORN.value : {
            'homepage': 'https://www.phorn.de/en/',
            'search_bar_xpath': '//*[@id="main-search-input"]',
            'search_button_xpath': '',
            'first_search_result_xpath': '',
            'cookie_button_xpath': '',
            'barcode_xpath': '',
            'code_xpath': '',
            'picture_xpath': '',
            'description_xpath': '',
            },
        Manufacturer.TUNGALOY.value : {
            'homepage': 'https://www.tungaloy.com/se/',
            'search_bar_xpath': '//*[@id="content_txttungaSearchValue"]',
            'search_button_xpath': '',
            'first_search_result_xpath': '',
            'cookie_button_xpath': '',
            'barcode_xpath': '',
            'code_xpath': '',
            'picture_xpath': '',
            },
        }

    def get_info(self, manufacturer: str, info_type: str) -> str:
        return self.MANUFACTURER_INFO.get(manufacturer, {}).get(info_type)

    def get_all_links(self) -> dict:
        return {manufacturer: info['homepage'] for manufacturer, info in self.MANUFACTURER_INFO.items()}

# Function to get the next order status
def get_next_order_status(current_order_status):
    try:
        # Find the index of the current status in the changing order list
        current_index = orderStatusChangingOrder.index(current_order_status)

        # Get the next status if the current status is not the last; otherwise, return the same status
        if current_index < len(orderStatusChangingOrder) - 1:
            return orderStatusChangingOrder[current_index + 1]
        else:
            # If current status is the last in the sequence or not in the sequence, return current status
            return current_order_status
    except ValueError:
        # Current order status not in the changing order list, return as 'UNKNOWN' or current status
        return OrderStatus.UNKNOWN

# function to reverse a dict
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

def get_tap_thread_series(s: str) -> str:
    # For M threads return 'M'
    if s.startswith('M') and not s.startswith('MF'):
        return 'M'
    if s.startswith('MF'):
        return 'MF'

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