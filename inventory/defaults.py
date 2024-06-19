from .utils import reverse_dict
from . import choices

class DefaultProduct:
    CODE = '0000'
    EAN = '0000000000000'
    BARCODE = '0000000000000'
    MANUFACTURER = choices.Strings.UNKNOWN
    DESCRIPTION = choices.Strings.UNKNOWN
    LINK = choices.Strings.UNKNOWN
    PICTURE = choices.Strings.UNKNOWN
    LOCATION = choices.Strings.UNKNOWN
    QUANTITY = choices.Strings.ZERO_INT
    CATALOG_PRICE = choices.Strings.ZERO_FLOAT
    TOOL_TYPE = choices.Strings.UNKNOWN

class DefaultOrder:
    QUANTITY = choices.Strings.ONE_INT
    STATUS = choices.OrderStatus.PENDING

# thisn is the barcode for the custom order product
# all custom orders will have this PostMachine product
default_custom_order_barcode = '2023122711263'

class DefaultMaterialToBeMachined:
    NAME = choices.Strings.UNDEFINED
    COLOUR = choices.Strings.BLACK
    GROUP = choices.Strings.LETTER_U


class DefaultTool:
    MATERIAL = choices.ToolMaterial.UNDEFINED
    COATING = choices.ToolCoating.UNDEFINED
    MTBM = DefaultMaterialToBeMachined()

class DefaultMillingTool:
    DIAMETER = choices.Strings.ZERO_FLOAT
    OVERALL_LENGTH = choices.Strings.ZERO_FLOAT
    NECK_DIAMETER = choices.Strings.ZERO_FLOAT
    SHANK_DIAMETER = choices.Strings.ZERO_FLOAT
    FLUTE_LENGTH = choices.Strings.ZERO_FLOAT
    USABLE_LENGTH = choices.Strings.ZERO_FLOAT
    CORNER_RADIUS = choices.Strings.ZERO_FLOAT
    CORNER_CHAMFER = choices.Strings.ZERO_FLOAT
    NUMBER_OF_FLUTES = choices.Strings.ONE_INT

class DefaultEndMill:
    LENGTH_CATEGORY = choices.MillLengthCategory.UNKNOWN

class DefaultFaceMill:
    FACE_ANGLE = choices.Strings.NINETY_FLOAT

class DefaultChamferMill:
    CHAMFER_ANGLE = choices.Strings.ZERO_FLOAT
    POINT_DIAMETER = choices.Strings.ZERO_FLOAT
    MAX_CHAMFER_WIDTH = choices.Strings.ZERO_FLOAT
    IS_REAR_SIDE_CUTTING = False

class DefaultBallMill:
    RADIUS = choices.Strings.ZERO_FLOAT

class DefaultThreadMill:
    THREAD = choices.Strings.UNKNOWN 
    THREAD_SERIES = choices.Strings.UNKNOWN
    THREAD_PITCH = choices.Strings.UNKNOWN

class DefaultRadiusMill:
    RADIUS = choices.Strings.ZERO_FLOAT

class DefaultLollipopMill:
    NECK_DIAMETER = choices.Strings.ZERO_FLOAT

class DefaultTSlotMill:
    MANUFACTURER = choices.Strings.UNKNOWN
    THICKNESS = choices.Strings.ZERO_FLOAT
    CUTTING_DEPTH_MAX  = choices.Strings.ZERO_FLOAT

class DefaultCircularSaw:
    THICKNESS = choices.Strings.ZERO_FLOAT
    CUTTING_DEPTH_MAX  = choices.Strings.ZERO_FLOAT
    INNER_DIAMETER = choices.Strings.ZERO_FLOAT

class DefaultDrillingTool:
    DIAMETER = choices.Strings.ZERO_FLOAT
    OVERALL_LENGTH = choices.Strings.ZERO_FLOAT
    POINT_ANGLE = choices.Strings.ZERO_FLOAT
    NUMBER_OF_FLUTES = choices.Strings.ONE_INT
    FLUTE_LENGTH = choices.Strings.ZERO_FLOAT
    SHANK_DIAMETER = choices.Strings.ZERO_FLOAT
    USABLE_LENGTH = choices.Strings.ZERO_FLOAT

class DefaultDrillTool:
    DIAMETER = choices.Strings.ZERO_FLOAT
    OVERALL_LENGTH = choices.Strings.ZERO_FLOAT
    POINT_ANGLE = choices.Strings.ZERO_FLOAT
    NUMBER_OF_FLUTES = choices.Strings.ONE_INT
    FLUTE_LENGTH = choices.Strings.ZERO_FLOAT
    SHANK_DIAMETER = choices.Strings.ZERO_FLOAT
    USABLE_LENGTH = choices.Strings.ZERO_FLOAT

class DefaultDrill:
    LENGTH_CATEGORY = choices.Strings.UNKNOWN

class DefaultReamer:
    TOLERANCE = choices.Strings.UNKNOWN
    UPPER_TOLERANCE = choices.Strings.ZERO_FLOAT
    LOWER_TOLERANCE = choices.Strings.ZERO_FLOAT
    PILOT_DIAMETER = choices.Strings.ZERO_FLOAT

class DefaultTap:
    DIAMETER = choices.Strings.ZERO_FLOAT
    SHANK_DIAMETER = choices.Strings.ZERO_FLOAT
    PITCH = choices.Strings.ZERO_FLOAT
    THREAD = choices.Strings.UNKNOWN # M5, G1/8, UNC 4-40
    THREAD_SERIES = choices.Strings.UNKNOWN # M, MF, G, UNC, UNF
    THREAD_CLASS = choices.Strings.UNKNOWN # 6H, 6G, 6HX, 6GX
    TAP_TYPE = choices.Strings.UNKNOWN
    TAP_HOLE_DIAMETER = choices.Strings.ZERO_FLOAT
    TAP_THREAD_LENGTH = choices.Strings.ZERO_FLOAT

class DefaultCenterDrill:
    STEP_ANGLE = choices.Strings.ZERO_FLOAT
    POINT_ANGLE = choices.Strings.ZERO_FLOAT
    POINT_ANGLE_NON_ZERO = 118.0

class DefaultU_Drill:
    DIAMETER = choices.Strings.ZERO_FLOAT
    MAX_DIAMETER = choices.Strings.ZERO_FLOAT
    MIN_DIAMETER = choices.Strings.ZERO_FLOAT

class DefaultInsert:
    CHIP_BREAKER = choices.Strings.UNKNOWN

class DefaultInsertTurning: 
    ISOCODE = 'AAAA 000000'
    CHIP_BREAKER = choices.Strings.UNKNOWN
    SHAPE = 80
    RELIEF_ANGLE = choices.Strings.ZERO_INT
    TOLERANCE = 'C'
    CROSS_SECTION = 'Type T'
    CROSS_SECTION_ABR = 'T'
    INSERT_SIZE = 9.67
    THICKNESS = 3.97
    CORNER_RADIUS = 0.8
    CORNER_RADIUS_ABR = '08'

class DefaultInsertGrooving:
    WIDTH = choices.Strings.ZERO_FLOAT
    MAX_CUT_DEPTH_GR = choices.Strings.ZERO_FLOAT
    MIN_CUT_DIAMETER = choices.Strings.ZERO_FLOAT

class DefaultInsertThreading:
    THREAD_TYPE = choices.Strings.UNKNOWN # Internal, External
    THREAD_PROFILE = choices.Strings.UNKNOWN # ISO, UN, Whitworth, Trapezoidal, Acme, Stub Acme, Buttress, R
    THREAD_PITCH = choices.Strings.ZERO_FLOAT
    THREAD_PITCH_SECOND = choices.Strings.ZERO_FLOAT # second value for partial profile
    THREAD_TPI = choices.Strings.ZERO_INT
    THREAD_TPI_SECOND = choices.Strings.ZERO_INT # second value for partial profile
    THREAD_PROFILE_TYPE = choices.Strings.UNKNOWN # Full profile, Partial profile
    THREAD_WIDTH = choices.Strings.ZERO_FLOAT # For trapecial thread

class DefaultCollet:
    DIAMETER = choices.Strings.ZERO_FLOAT
    TYPE = choices.Strings.UNKNOWN # ER, OZ,  
    IS_SEALED = False

# Turning
class DefaultExternalCutter:
    MASTER_INSERT_ISO_CODE = choices.Strings.INSERT_BLANK
    CUTTER_ISO_CODE = choices.Strings.CUTTER_BLANK

class DefaultInternalCutter:
    MASTER_INSERT_ISO_CODE = choices.Strings.INSERT_BLANK
    CUTTER_ISO_CODE = choices.Strings.CUTTER_BLANK
    MIN_BORE_DIAMETER = choices.Strings.ZERO_FLOAT
    OVERALL_LENGTH = choices.Strings.ZERO_FLOAT
    FUNCTIONAL_LENGTH = choices.Strings.ZERO_FLOAT

class DefaultBoringCutter:
    ANGLE = choices.Strings.ZERO_FLOAT
    CUTTER_ISO_CODE = choices.Strings.BORING_CUTTER_BLANK

    @property
    def iso_code_values(self):
        values = {
            'angle' : {
                'F': 90,
                'J': 142,
                'K': 75,
                'L': 95,
                'P': 117.5,
                'Q': 122.5,
                'S': 45,
                'U': 93,
                'W': 60,
                'X': 113,
                'Y': 85
            }
        }
        return values

class DefaultSolidBoringCutter:
    ANGLE = choices.Strings.ZERO_FLOAT
    MATERIAL = choices.ToolMaterial.CARBIDE

class DefaultThreadCutter:
    IS_METRIC = True
    IS_INCH = False

class DefaultSolidThreadCutter:
    MATERIAL = choices.ToolMaterial.CARBIDE

class DefaultGroovingExternalCutter:
    CUTTING_WIDTH = choices.Strings.ZERO_FLOAT
    MAX_CUTTING_DEPTH = choices.Strings.ZERO_FLOAT    

class DefaultGroovingInternalCutter:
    CUTTING_WIDTH = choices.Strings.ZERO_FLOAT
    MAX_CUTTING_DEPTH = choices.Strings.ZERO_FLOAT        

class DefaultSolidGroovingCutter:
    CUTTING_WIDTH = choices.Strings.ZERO_FLOAT
    MAX_CUTTING_DEPTH = choices.Strings.ZERO_FLOAT
    MATERIAL = choices.ToolMaterial.CARBIDE
    FUNCTIONAL_LENGTH = choices.Strings.ZERO_FLOAT

class InsertAbreviations:
    values = {
            'shape': {
                'A' : [85, 'Parallelogram'],
                'B' : [82, 'Parallelogram'],
                'C' : [80, 'Diamond'],
                'D' : [55, 'Diamond'],
                'E' : [75, 'Diamond'],
                'K' : [55, 'Parallelogram'],
                'M' : [90, 'Diamond'], # 86
                'R' : [0, 'Round'],
                'S' : [0, 'Square'],
                'T' : [0, 'Triangle'],
                'V' : [35, 'Diamond'],
                'W' : [0, 'Trigon'],
                'Y' : [25, 'Diamond'],
            },
            'relief_angle': {
                'N' : 0,
                'A' : 3,
                'B' : 5,
                'C' : 7,
                'P' : 11,
                'D' : 15,
                'E' : 20,
                'F' : 25,
                'G' : 30,
                'W' : 35, # check this
            },
            'tolerance' : {
                'C': 'C',
                'H': 'H',
                'E': 'E',
                'G': 'G',
                'M': 'M',
                'U': 'U',
                },
            'cross_section' : {
                'A' : 'Type A',
                'B' : 'Type B',
                'C' : 'Type C',
                'F' : 'Type F',
                'G' : 'Type G',
                'H' : 'Type H',
                'J' : 'Type J',
                'M' : 'Type M',
                'N' : 'Type N',
                'P' : 'Type P', # check this on ceratizit
                'Q' : 'Type Q',
                'R' : 'Type R',
                'T' : 'Type T',
                'U' : 'Type U',
                'W' : 'Type W',
                'X' : 'Type X',
            },
            'insert_size' : {
                'S4': 4.03,
                '04': 4.84,
                '05': 5.64,
                '06': 6.45,
                '07': 6.35, # check this on tungaloy
                '08': 8.06,
                '09': 9.67,
                '11': 11.28,
                '12': 12.9,
                '14': 14.51,
                '15': 15.5, # check this on ceratizit
                '16': 16.12,
                '17': 17.73,
                '19': 19.34,
                '22': 22.57,
                '25': 25.79,
                '32': 32.24,
            },
            'thickness' : {
                'T0': 1.02,
                '01': 1.59,
                'T1': 1.98,
                '02': 2.38,
                'T2': 2.78,
                '03': 3.18,
                'T3': 3.97,
                '04': 4.76,
                '05': 5.56,
                '06': 6.35,
                '07': 7.94,
                '09': 9.52,
                '11': 11.11,
                '12': 12.7,
            },
            'corner_radius' : {
                'X0': 0.04,
                '00': 0.05,
                '01': 0.1,
                '02': 0.2,
                '04': 0.4,
                '08': 0.8,
                '12': 1.2,
                '16': 1.6,
                '20': 2.0,
                '24': 2.4,
                '32': 3.2,
            },
        }

    @property
    def reversed_values(self):
        reversed_values = {}
        for key in self.values:
            if key == 'shape':
                reversed_values[key] = {
                    '85': 'A',
                    '82': 'B',
                    '80': 'C',
                    '55': 'D',
                    '75': 'E',
                    '55': 'K',
                    '90': 'M', # 86
                    'Round': 'R',
                    'Square': 'S',
                    'Triangle': 'T',
                    '35': 'V',
                    'Trigon': 'W',
                    '25': 'Y'
                }
            elif key == 'tolerance':
                reversed_values[key] = self.values[key]
            else:
                reversed_values[key] = reverse_dict(self.values[key])
        return reversed_values

# Equipment
class DefaultMillingHolder:
    NAME = choices.Strings.MILLING_HOLDER_BLANK
    DIAMETER = choices.Strings.ZERO_FLOAT
    LENGTH = choices.Strings.ZERO_FLOAT
    HOLDER_TYPE = choices.Strings.UNKNOWN

class DefaultMeasurementTool:
    MIN = choices.Strings.ZERO_FLOAT
    MAX = choices.Strings.ZERO_FLOAT
    PRECISION = choices.Strings.ZERO_FLOAT

class DefaultThreadGauge:
    GOUGE_TYPE = choices.Strings.UNKNOWN # GO, NOGO
    THREAD_PROFILE = choices.Strings.UNKNOWN # ISO, UN, Whitworth, Trapezoidal, Acme, Stub Acme, Buttress, R
    THREAD_PITCH = choices.Strings.ZERO_FLOAT
    THREAD_TPI = choices.Strings.ZERO_INT

class DefaultGauge:
    MIN = choices.Strings.ZERO_FLOAT
    MAX = choices.Strings.ZERO_FLOAT

class DefaultMeasuringPin:
    DIAMETER = choices.Strings.ZERO_FLOAT

# Items
class DefaultScrewdriver:
    SCREWDRIVER_SIZE = choices.Strings.ZERO_STRING

class DefaultKey:
    KEY_SIZE = choices.Strings.ZERO_STRING