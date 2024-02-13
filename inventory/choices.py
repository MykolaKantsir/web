from django.db import models
from collections import namedtuple
from enum import Enum
from typing import Dict

# Strings used in the project
class Strings():
    NOT_IMPLEMENTED_CONSTRUCTOR = 'Not implemented constructor'
    UNKNOWN = 'Unknown'
    UNDEFINED = 'Undefined'
    ZERO_INT = 0
    ZERO_FLOAT = 0.0
    ZERO_STRING = '0'
    ONE_INT = 1
    ONE_FLOAT = 1.0
    NINETY_FLOAT = 90.0
    
    # Inserts
    INSERT_BLANK = 'AAAA 000000'

    # Cutter
    CUTTER_BLANK = 'AAAAA'
    BORING_CUTTER_BLANK = 'A00A AAAAA00'

    # Milling holder
    MILLING_HOLDER_BLANK = 'AA00-00-000'

    # mtbm
    BLACK = 'black'
    LETTER_U = 'U'

# Choices for order status
class OrderStatus(models.TextChoices):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    ORDERED = 'Ordered'
    UNKNOWN = Strings.UNKNOWN

orderStatusChangingOrder = [OrderStatus.PENDING, OrderStatus.ORDERED, OrderStatus.SHIPPED, OrderStatus.RECEIVED]

# Choices for the mill length category
class MillLengthCategory(models.TextChoices):
    EXTRA_SHORT = 'Extra short'
    SHORT = 'Short'
    MEDIUM = 'Medium'
    MEDIUM_PLUS = 'Medium plus'
    LONG = 'Long'
    EXTRA_LONG = 'Extra long'
    UNKNOWN = Strings.UNKNOWN
    
    @classmethod
    def to_standard(cls, scraped_string):
        # Normalize the string to uppercase for case-insensitive matching
        scraped_string = scraped_string.upper()

        # A custom mapping method to match your enum values
        mapping_dict = {
            cls.EXTRA_SHORT: ['EXTRAKURZ'],
            cls.SHORT: ['KURZ', 'KORT'],
            cls.MEDIUM: ['MITTELLANG', 'LÅNG'],
            cls.MEDIUM_PLUS: ['LANG+'],
            cls.LONG: ['LANG', 'MEDELLÅNG', '3xD'],
            cls.EXTRA_LONG: ['EXTRALANG', '5xD'],
        }
        
        for category, synonyms in mapping_dict.items():
            if scraped_string in [s.upper() for s in synonyms]:
                return category
        return cls.UNKNOWN

class Manufacturer(models.TextChoices):
    UNKNOWN = Strings.UNKNOWN
    CERATIZIT = 'ceratizit'
    GUEHRING = 'guehring'
    HOFFMANN = 'hoffmann'
    TUNGALOY = 'tungaloy'
    SANDVIK = 'sandvik'
    WALTER = 'walter'
    DUEMMEL = 'duemmel'
    PHORN = 'phorn'
    SKENEJARN = 'skene järn'
    PRECISION_DETALJER = 'precision detaljer'

class ToolType(models.TextChoices):
    END_MILL = 'Mill'
    TAP = 'Tap'
    BALL_MILL = 'Ball mill'
    FACE_MILL = 'Face mill'
    THREAD_MILL = 'Thread mill'
    INSERT_TURNING = 'Insert turning'
    DRILL = 'Drill'
    CHAMFER_MILL = 'Chamfer mill'
    COLLET = 'Collet'
    GENERAL_CUTTER = 'General cutter'
    BORING_CUTTER = 'Boring cutter'
    SOLID_BORING_CUTTER = 'Solid boring cutter'
    THREAD_INTERNAL_CUTTER = 'Thread internal cutter'
    SOLID_THREAD_CUTTER = 'Solid thread cutter'
    THREAD_EXTERNAL_CUTTER = 'Thread external cutter'
    GROOVING_INTERNAL_CUTTER = 'Grooving internal cutter'
    SOLID_GROOVING_CUTTER = 'Solid grooving cutter'
    GROOVING_EXTERNAL_CUTTER = 'Grooving external cutter'
    INSERT_THREAD = 'Insert thread'
    INSERT_DRILLING = 'Drill insert'
    SHIM = 'Shim'
    SCREW = 'Screw'
    INSERT_MILLING = 'Insert milling'
    U_DRILL = 'U-Drill'
    KEY = 'Key'
    WRENCH = 'Wrench'
    SCREWDRIVER = 'Screwdriver'
    MILLING_HOLDER = 'Milling holder'
    INSERT_GROOVING = 'Insert cutoff'
    TSLOT_MILL = 'T-Slot mill'
    CIRCULAR_SAW = 'Circular saw'
    EQUIPMENT_TURNING = 'Equipment turning'
    EQUIPMENT_MILLING = 'Equipment milling'
    REAMER = 'Reamer'
    LOLLIPOP_MILL = 'Lollipop mill'
    SPOT_DRILL = 'Spot drill'
    CENTER_DRILL = 'Center drill'
    MILLING_BODY = 'Milling body'
    MEASURING = 'Measuring'
    RADIUS_MILL = 'Radius mill'
    POST_MACHINING = 'Post machining'

class ToolMaterial(models.TextChoices):
    UNDEFINED = 'Undefined'
    CARBIDE = 'Carbide'
    HSS = 'HSS'
    # HC = 'HC'
    # HPC = 'HPC'
    # HSS_CO = 'HSS Co 5'
    # VHM = 'VHM'    
    # HSS_E = 'HSS-E'
    # SOLID_CARBIDE = 'SOLID CARBIDE'
    # SOLID_HÅRDMETALL = 'Solid hårdmetall'

    def to_json(self):
        return {"name": self.name, "value": self.value}


# Normalize the tool material string to the ToolMaterial
def normalize_tool_material(material: str) -> str:
    """Normalize the tool material string to the ToolMaterial choice"""
    CARBIDE_VARIANTS = ['Carbide', 'CARBIDE', 'HC', 'HPC', 'VHM', 'SOLID CARBIDE', 'SOLID', 'Solid hårdmetall']
    HSS_VARIANTS = ['HSS', 'HSS Co 5', 'HSCO', 'HSSE', 'HSS-E', 'HSS E', 'HSS-PM', 'HSSE-PM', 'HSS-E-PM', 'HSS E PM']

    if material in CARBIDE_VARIANTS:
        return ToolMaterial.CARBIDE
    elif material in HSS_VARIANTS:
        return ToolMaterial.HSS
    else:
        return None
        #return ToolMaterial.UNDEFINED

class ToolCoating(models.TextChoices):
    UNDEFINED = 'Undefined'
    BLANK = 'blank'
    AH3225 = 'AH3225'
    AH6225 = 'AH6225'
    AH6235 = 'AH6235'
    AH725 = 'AH725'
    APX72S = 'APX72S'
    ALCRN = 'AlCrN'
    ALTIN = 'AlTiN'
    ALTIX = 'AlTiX'
    BK7710 = 'BK7710'
    BX310 = 'BX310'
    CARBO = 'Carbo'
    CCN20 = 'CCN20'
    CCN1525 = 'CCN1525'
    CCN2520 = 'CCN2520'
    CCN7525 = 'CCN7525'
    CT_P25 = 'CT-P25'
    CTBH20C = 'CTBH20C'
    CTC2135 = 'CTC2135'
    CTCM120 = 'CTCM120'
    CTCM130 = 'CTCM130'
    CTCM235 = 'CTCM235'
    CTCM245 = 'CTCM245'
    CTCP125_P = 'CTCP125-P'
    CTCP135_P = 'CTCP135-P'
    CTDCD10 = 'CTDCD10'
    CTDPD20 = 'CTDPD20'
    CTDPS30 = 'CTDPS30'
    CTEP110 = 'CTEP110'
    CTP1340 = 'CTP1340'
    CTP2120 = 'CTP2120'
    CTPM125 = 'CTPM125'
    CTPM240 = 'CTPM240'
    CTPP345 = 'CTPP345'
    CTPP430 = 'CTPP430'
    CTPX710 = 'CTPX710'
    CTPX715 = 'CTPX715'
    CU7010 = 'CU7010'
    CVD_TICN_PLUS_AL2O3_PLUS_TIN = 'CVD TiCN+Al2O3+TiN'
    CVD_TICRN_PLUS_AL2O3_PLUS_TIN = 'CVD TiCrN+Al2O3+TiN'
    CVD_TICN_TIN = 'CVD TiCN+TiN'
    CWK20 = 'CWK20'
    CWN1525 = 'CWN1525'
    CWX500 = 'CWX500'
    DLC = 'DLC'
    DPA72S = 'DPA72S'
    DPB72S = 'DPB72S'
    DPX14S = 'DPX14S'
    DPX22S = 'DPX22S'
    DPX72S = 'DPX72S'
    DPX74S = 'DPX74S'
    DX110 = 'DX110'
    F__NIT = 'F.-nit'
    FIRE = 'FIRE'
    GT9530 = 'GT9530'
    H210T = 'H210T'
    H216T = 'H216T'
    HB7010 = 'HB7010'
    HB7020 = 'HB7020'
    HB7125_1 = 'HB7125-1'
    HB7310 = 'HB7310'
    HB7510 = 'HB7510'
    HB7520 = 'HB7520'
    HBX130 = 'HBX130'
    HCR = 'HCr'
    HU7305_1 = 'HU7305-1'
    HU7310 = 'HU7310'
    HU7315_1 = 'HU7315-1'
    HU7810 = 'HU7810'
    KS05F = 'KS05F'
    KS15F = 'KS15F'
    KW10 = 'KW10'
    PKD = 'PKD'
    PVD_ALCRN = 'PVD AlCrN'
    PVD_ALTICRN = 'PVD AlTiCrN'
    PVD_ALTIN = 'PVD AlTiN'
    PVD_TIALN = 'PVD TiAlN'
    PVD_TIALN_PLUS_TIALN = 'PVD TiAlN+TiAlN'
    PVD_TIALN_PLUS_TIN = 'PVD TiAlN+TiN'
    PVD_TIN = 'PVD TiN'
    PERROX = 'Perrox'
    RAPTOR = 'Raptor'
    SH725 = 'SH725'
    SH730 = 'SH730'
    SIGNUM = 'Signum'
    SIRIUS = 'Sirius'
    T6130 = 'T6130'
    T6215 = 'T6215'
    T9215 = 'T9215'
    T9225 = 'T9225'
    T9235 = 'T9235'
    TH10 = 'TH10'
    TI1000 = 'Ti1000'
    TI1500 = 'Ti1500'
    TI2000 = 'Ti2000'
    TI500 = 'Ti500'
    TI600 = 'Ti600'
    TI750 = 'Ti750'
    TIALN = 'TiAlN'
    TIALN_NANOA = 'TiAlN-nanoA'
    TIALN_SUPERA = 'TiAlN-SuperA'
    TICN = 'TiCN'
    TICN_AL2O3_TIN = 'TiCN+Al2O3+TiN'
    TICN_TIN = 'TiCN+TiN'
    TICNO = 'TiCNO'
    TIN = 'TiN'
    TIN_GS = 'TiN GS'
    TISI = 'TiSi'
    TISIN = 'TiSiN'
    ZENIT = 'Zenit'
    ZOX = 'ZOX'
    NANOFIRE = 'nanoFIRE'
    NITR_ = 'nitr.'
    OBELAGD = 'obelagd'
    ANGANLOPT = 'ånganlöpt'

    def to_json(self):
        return {"name": self.name, "value": self.value}

class DrillLengthCategory(models.TextChoices):
    CAT_3xd = '3xD'
    CAT_5xd = '5xD'
    CAT_7xd = '7xD'
    CAT_8xd = '8xD'
    CAT_10xd = '10xD'
    CAT_12xd = '12xD'
    CAT_15xd = '15xD'
    CAT_20xd = '20xD'

class TapType(models.TextChoices):
    UNKNOWN = Strings.UNKNOWN
    CUT = 'Cut'
    SPIRAL = 'Spiral'
    FORM = 'Form'

class HolderType(models.TextChoices):
    ER = 'ER'
    WELDON = 'Weldon'
    SHRINK = 'Shrink'

class ColletType(models.TextChoices):
    ER8 = 'ER8'
    ER11 = 'ER11'
    ER16 = 'ER16'
    ER20 = 'ER20'
    ER25 = 'ER25'
    ER32 = 'ER32'
    ER40 = 'ER40'

class Facet():
    categorical = 'categorical'
    numerical = 'numerical'
    boolean = 'boolean'


SELENIUM_MANUFACTURERS = [Manufacturer.SANDVIK, Manufacturer.CERATIZIT, Manufacturer.TUNGALOY]
BS_MANUFACTURERS = [Manufacturer.HOFFMANN, Manufacturer.GUEHRING]

# These classes are used only for scraping
# This class is used only for scraping
class ToolMaterial_enum(Enum):
    UNDEFINED = 'Undefined'
    CARBIDE = 'Carbide'
    HSS = 'HSS'
    HSS_E = 'HSS-E'
    HSS_E_PM = 'HSS-E-PM'
    HSS_PM = 'HSS-PM'
    CERMET = 'Cermet'
    CERAMIC = 'Ceramic'
    CBN = 'CBN'
    PCD = 'PCD'
    DIAMOND = 'Diamond'
    CARBIDE_TIPPED = 'Carbide tipped'
    CARBIDE_TIPPED_HSS = 'Carbide tipped HSS'
    CARBIDE_TIPPED_HSS_E = 'Carbide tipped HSS-E'
    CARBIDE_TIPPED_HSS_E_PM = 'Carbide tipped HSS-E-PM'
    CARBIDE_TIPPED_HSS_PM = 'Carbide tipped HSS-PM'
    CARBIDE_TIPPED_CERMET = 'Carbide tipped Cermet'
    CARBIDE_TIPPED_CERAMIC = 'Carbide tipped Ceramic'
    CARBIDE_TIPPED_CBN = 'Carbide tipped CBN'
    CARBIDE_TIPPED_PCD = 'Carbide tipped PCD'
    CARBIDE_TIPPED_DIAMOND = 'Carbide tipped Diamond'
    HSS_CARBIDE = 'HSS Carbide'
    HSS_E_CARBIDE = 'HSS-E Carbide'
    HSS_E_PM_CARBIDE = 'HSS-E-PM Carbide'
    HSS_PM_CARBIDE = 'HSS-PM Carbide'
    CERMET_CARBIDE = 'Cermet Carbide'
    CERAMIC_CARBIDE = 'Ceramic Carbide'
    CBN_CARBIDE = 'CBN Carbide'
    PCD_CARBIDE = 'PCD Carbide'
    DIAMOND_CARBIDE = 'Diamond Carbide'
    HSS_CARBIDE_TIPPED = 'HSS Carbide tipped'
    HSS_E_CARBIDE_TIPPED = 'HSS-E Carbide tipped'
    HSS_E_PM_CARBIDE_TIPPED = 'HSS-E-PM Carbide tipped'
    HSS_PM_CARBIDE_TIPPED = 'HSS-PM Carbide tipped'
    
    def to_json(self):
        return {"name": self.name, "value": self.value}

# Material to be machined
Tool_material = namedtuple('Tool_material', ['name', 'color', 'group'])

# This class is used only for scraping
class Mtbm(Enum):
    UNDEFINED = Tool_material('Undefined', 'black', 'U')
    STEEL = Tool_material('Steel', 'blue', 'P')
    STAINLESS_STEEL = Tool_material('Stainless steel', 'yellow', 'M')
    CAST_IRON = Tool_material('Cast iron', 'red', 'K')
    NON_FERROUS_METAL = Tool_material('Non-ferrous metal', 'green', 'N')
    SUPERALLOY = Tool_material('Superallyos', 'brown', 'S') # Superalloys and titanium
    HARDENED_MATERIAL = Tool_material('Hardened material', 'grey', 'H')
    NON_METALLIC_MATERIAL = Tool_material('Non-metallic material', 'white', 'O')

    def to_json(self) -> Dict:
        tool_material = self.value._asdict()  # Converts namedtuple to a dict
        return {
            "name": self.name,  # This is the name of the Enum member (e.g., "STEEL")
            "tool_material": tool_material  # This is the dict of the Tool_material namedtuple
        }
    
    @classmethod
    def all_mtbm(self) -> list:
        res = [mtbm for mtbm in Mtbm if mtbm != Mtbm.UNDEFINED]
        return res

