'''
#
# PROTEIN
#
'''

'''
CODING TRANSFORMATION
http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/
'''
import six
if six.PY2:
    from .AminoAcids import AminoAcids
    from .Element import PeriodicTable
from .Alphabet import *
from .Properties import *


aminoacids3to1 = {
    'ALA': 'A', 'AZT': 'A', 'CHA': 'A', 'HPH': 'A', 'NAL': 'A', 'AIB': 'A', 'BAL': 'A',
    'DHA': 'A', 'BB9': 'A', 'ALM': 'A', 'AYA': 'A', 'BNN': 'A', 'CHG': 'A', 'CSD': 'A',
    'DAL': 'A', 'DNP': 'A', 'FLA': 'A', 'HAC': 'A', 'MAA': 'A', 'PRR': 'A', 'TIH': 'A',
    'TPQ': 'A', 'BB9': 'A',
    'ARG': 'R', 'ORN': 'R', 'ACL': 'R', 'ARM': 'R', 'AGM': 'R', 'HAR': 'R', 'HMR': 'R',
    'DAR': 'R',
    'ASN': 'N', 'MEN': 'N',
    'ASP': 'D', 'ASZ': 'D', '2AS': 'D', 'ASA': 'D', 'ASB': 'D', 'ASK': 'D', 'ASL': 'D',
    'ASQ': 'D', 'BHD': 'D', 'DAS': 'D', 'DSP': 'D',
    'ASX': 'B',
    'CYS': 'C', 'CYD': 'C', 'CYO': 'C', 'HCY': 'C', 'CSX': 'C', 'SMC': 'C', 'BCS': 'C',
    'BUC': 'C', 'C5C': 'C', 'C6C': 'C', 'CCS': 'C', 'CEA': 'C', 'CME': 'C', 'CSO': 'C',
    'CSP': 'C', 'CSS': 'C', 'CSW': 'C', 'CY1': 'C', 'CY3': 'C', 'CYG': 'C', 'CYM': 'C',
    'CYQ': 'C', 'DCY': 'C', 'OCS': 'C', 'SOC': 'C', 'EFC': 'C', 'PR3': 'C', 'SCH': 'C',
    'SCS': 'C', 'SCY': 'C', 'SHC': 'C', 'PEC': 'C',
    'GLN': 'Q', 'DGN': 'Q',
    'GLU': 'E', 'GLA': 'E', 'PCA': 'E', '5HP': 'E', 'CGU': 'E', 'DGL': 'E', 'GGL': 'E',
    'GMA': 'E',
    'GLX': 'Z',
    'GLY': 'G', 'GL3': 'G', 'GLZ': 'G', 'GSC': 'G', 'SAR': 'G', 'MPQ': 'G', 'NMC': 'G',
    'MSA': 'G', 'DBU': 'G',
    'HIS': 'H', 'HSD': 'H', 'HI0': 'H', 'HIP': 'H', 'HID': 'H', 'HIE': 'H',
    '3AH': 'H', 'MHS': 'H', 'DHI': 'H', 'HIC': 'H', 'NEP': 'H', 'NEM': 'H',
    'ILE': 'I', 'IIL': 'I', 'DIL': 'I',
    'LEU': 'L', 'NLE': 'L', 'LOV': 'L', 'NLN': 'L', 'NLP': 'L', 'MLE': 'L', 'BUG': 'L',
    'CLE': 'L', 'DLE': 'L', 'MLU': 'L',
    'LYS': 'K', 'LYZ': 'K', 'ALY': 'K', 'TRG': 'K', 'SHR': 'K', 'LYM': 'K', 'LLY': 'K',
    'KCX': 'K', 'LLP': 'K', 'DLY': 'K', 'DM0': 'K',
    'MET': 'M', 'MSE': 'M', 'CXM': 'M', 'FME': 'M', 'OMT': 'M',
    'PHE': 'F', 'DAH': 'F', 'HPQ': 'F', 'DPN': 'F', 'PHI': 'F', 'PHL': 'F',
    'PRO': 'P', 'HYP': 'P', 'DPR': 'P', 'ECQ': 'P', 'POM': 'P', 'H5M': 'P',
    'SER': 'S', 'HSE': 'S', 'STA': 'S', 'SVA': 'S', 'SAC': 'S', 'SEL': 'S', 'SEP': 'S',
    'SET': 'S', 'OAS': 'S', 'DSN': 'S', 'MIS': 'S',
    'THR': 'T', 'PTH': 'T', 'ALO': 'T', 'TPO': 'T', 'BMT': 'T', 'DTH': 'T', 'CTH': 'T',
    'TRP': 'W', 'TPL': 'W', 'TRO': 'W', 'DTR': 'W', 'HTR': 'W', 'LTR': 'W',
    'TYR': 'Y', 'TYQ': 'Y', 'TYS': 'Y', 'TYY': 'Y', 'TYB': 'Y', 'STY': 'Y', 'PTR': 'Y',
    'PAQ': 'Y', 'DTY': 'Y', 'IYR': 'Y', 'GHP': 'Y', 'D3P': 'Y', 'D4P': 'Y', 'OMZ': 'Y',
    'OMY': 'Y',
    'VAL': 'V', 'NVA': 'V', 'DVA': 'V', 'DIV': 'V', 'MVA': 'V',
    'SEC': 'U',
    'PYL': 'O',
    'XLE': 'J',
    'ACE': 'X', '3FG': 'X', 'UNK': 'X'
}

aminoacids1to3 = dict([[v, k] for k, v in aminoacids3to1.items()])
aminoacids1to3['A'] = 'ALA'
aminoacids1to3['N'] = 'ASN'
aminoacids1to3['R'] = 'ARG'
aminoacids1to3['D'] = 'ASP'
aminoacids1to3['C'] = 'CYS'
aminoacids1to3['Q'] = 'GLN'
aminoacids1to3['E'] = 'GLU'
aminoacids1to3['G'] = 'GLY'
aminoacids1to3['H'] = 'HIS'
aminoacids1to3['I'] = 'ILE'
aminoacids1to3['J'] = 'XLE'
aminoacids1to3['L'] = 'LEU'
aminoacids1to3['K'] = 'LYS'
aminoacids1to3['M'] = 'MET'
aminoacids1to3['F'] = 'PHE'
aminoacids1to3['O'] = 'PYL'
aminoacids1to3['P'] = 'PRO'
aminoacids1to3['S'] = 'SER'
aminoacids1to3['T'] = 'THR'
aminoacids1to3['U'] = 'SEC'
aminoacids1to3['W'] = 'TRP'
aminoacids1to3['Y'] = 'TYR'
aminoacids1to3['V'] = 'VAL'

'''
REGULAR AMINOACIDS IDENTIFICATION
'''
aminoacids_main3 = set(['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLX', 'GLY', 'HIS', 'ILE', 'LEU',
                        'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL', 'SEC', 'PYL', 'XLE'])

aminoacids_main1 = set(['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V'])

'''
PROPERTIES
'''
aminoacids_surface = {
    'A': 115, 'C': 149, 'D': 170, 'E': 207, 'F': 230, 'G': 86,  'H': 206,
    'I': 187, 'K': 222, 'L': 192, 'M': 210, 'N': 184, 'P': 140, 'Q': 208,
    'R': 263, 'S': 140, 'T': 164, 'V': 161, 'W': 269, 'Y': 257,
}

aminoacids_polarity_boolean = {
    'A': False, 'C': False, 'D': True,  'E': True,  'F': False, 'G': False, 'H': True,
    'I': False, 'K': True,  'L': False, 'M': False, 'N': True,  'P': False, 'Q': True,
    'R': True,  'S': True,  'T': True,  'V': False, 'W': False, 'Y': True
}

'''
#
# DNA/RNA
#
'''
nucleic_main = set(['DA', 'A', 'DC', 'C', 'DG', 'G', 'DI', 'I', 'DT', 'T', 'DU', 'U'])
nucleic2to1  = {
    'DA': 'A', 'A': 'A', 'A44': 'A', '6HA': 'A', 'APN': 'A',
    'DC': 'C', 'C': 'C', '5CM': 'C', 'MCY': 'C', 'OMC': 'C', 'C43': 'C', '6HC': 'C',
    'CPN': 'C',
    'DG': 'G', 'G': 'G', 'OMG': 'G', 'G48': 'G', '6HG': 'G', 'GPN': 'G',
    'DI': 'I', 'I': 'I',
    'DT': 'T', 'T': 'T', '6HT': 'T', 'TPN': 'T',
    'DU': 'U', 'U': 'U', 'U36': 'U', '5IU': 'U',
    'N': 'N'
}

'''
CRYSTALOGRAPHIC METHODS
'''
crystal_method_has_resolution = set(['X-RAY DIFFRACTION', 'ELECTRON MICROSCOPY', 'NEUTRON DIFFRACTION',
                                     'FIBER DIFFRACTION', 'ELECTRON CRYSTALLOGRAPHY'])

crystal_method_not_resolution = set(['SOLUTION NMR', 'POWDER DIFFRACTION', 'SOLUTION SCATTERING', 'SOLID-STATE NMR',
                                     'INFRARED SPECTROSCOPY', 'FLUORESCENCE TRANSFER'])

crystal_method                = crystal_method_has_resolution.union(crystal_method_not_resolution)
