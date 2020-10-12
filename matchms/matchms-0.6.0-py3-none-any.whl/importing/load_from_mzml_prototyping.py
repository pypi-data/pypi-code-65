# from typing import Generator
import numpy
import pyteomics
# from pyteomics import mzml
from matchms.Spectrum import Spectrum


# def load_from_mzml(filename: str) -> Generator[Spectrum, None, None]:
"""Load spectrum(s) from mgf file."""
filename = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\Deoxyuridine_1975_gc_ms.mzML"



#%%
!pip list

#%%
from pyteomics import mzml

#%%
# file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\Deoxyuridine_1975_gc_ms.mzML"
file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\testfile.mzML"
# file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\tiny.pwiz.1.1.mzML"
# file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\Beer_multibeers_3_T10_POS.mzML"

for pyteomics_spectrum in mzml.read(file_mzml, dtype=dict): 
    #test = pyteomics_spectrum._get_info()
    metadata = parse_mzml_mzxml_metadata(pyteomics_spectrum)
    mz = pyteomics_spectrum["m/z array"]
    intensities = pyteomics_spectrum["intensity array"]
  
#%%
file_mzxml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\theogallin.mzXML"
from pyteomics import mzxml
# testspec = mzxml.read(file_mzxml, dtype=dict)

#testlist=list(testspec)
metadata = None

for pyteomics_spectrum in mzxml.read(file_mzxml, dtype=dict):
    #test = pyteomics_spectrum._get_info()
    metadata = parse_mzml_mzxml_metadata(pyteomics_spectrum)
    mz = pyteomics_spectrum["m/z array"]
    intensities = pyteomics_spectrum["intensity array"]


#%%
charge = None
title = None
precursor_mz = None
scan_time = None

spec_mzxml = pyteomics_spectrum


first_search = list(find_by_key(spec_mzxml, "precursor"))
if not first_search:
    first_search = list(find_by_key(spec_mzxml, "precursorMz"))
if first_search:
    precursor_mz_search = list(find_by_key(first_search, "selected ion m/z"))
    if not precursor_mz_search:
        precursor_mz_search = list(find_by_key(first_search, "precursorMz"))
    if precursor_mz_search:
        precursor_mz = float(precursor_mz_search[0])
        
precursor_charge = list(find_by_key(first_search, "charge state"))
if precursor_charge:
    charge = int(precursor_charge[0])            
    
if "spectrum title" in spec_mzxml:
    title = spec_mzml["spectrum title"]

scan_time = list(find_by_key(spec_mzxml, "scan start time"))



#%%
test = parse_mzml_mzxml_metadata(pyteomics_spectrum)


#%%
def load_file(self):
    reader = pymzml.run.Reader(self.file_name, obo_version = '4.1.12')
    scan_no = 0
    for scan in reader:
        rt = scan.scan_time_in_minutes()
        ms_level = scan.ms_level
        peaks = scan.peaks('centroided')
        if ms_level == 2:
            precursor_mz = scan.selected_precursors[0]['mz']
        else:
            precursor_mz = None
        self.scans.append(MZMLScan(scan_no,self.file_name,
                          ms_level,peaks,rt,precursor_mz))
        scan_no += 1
    print("Loaded {} scans".format(scan_no))


#%%
def find_by_key(data, target):
    if hasattr(data,'items'):
        for key, value in data.items():
            if isinstance(value, dict):
                yield from find_by_key(value, target)
            elif isinstance(value, list):
                for val in value:
                    # print(val)
                    for result in find_by_key(val, target):
                        yield result
                        #yield from find_by_key(result, target)
            elif key == target:
                yield value

print(list(find_by_key(pyteomics_spectrum, "precursorMz")))


#%%
def gen_dict_extract(var, key):
    if hasattr(var,'iteritems'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result
                        
                        

#%%
# file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\Beer_multibeers_3_T10_POS.mzML"
file_mzml = "C:\\OneDrive - Netherlands eScience Center\\Project_Wageningen_iOMEGA\\matchms\\tests\\testdata.mzML"
# file_mzml = mzml_file
ms_level = 2

# def load_from_mzml(filename: str, ms_level: int = 2) -> Generator[Spectrum, None, None]:
"""Load spectrum(s) from mzml file.

Parameters
----------
filename:
    Filename for mzml file to import.
ms_level:
    Specify which ms level to import. Default is 2.
"""


spectrums = []
for pyteomics_spectrum in list(mzml.read(file_mzml, dtype=dict)):
    if "ms level" in pyteomics_spectrum and pyteomics_spectrum["ms level"] == ms_level:
        metadata = parse_mzml_mzxml_metadata(pyteomics_spectrum)
        mz = numpy.asarray(pyteomics_spectrum["m/z array"], dtype="float")
        intensities = numpy.asarray(pyteomics_spectrum["intensity array"], dtype="float")   

        if isinstance(mz, numpy.ndarray):
            # Sort by mz (if not sorted already)
            if not numpy.all(mz[:-1] <= mz[1:]):
                idx_sorted = numpy.argsort(mz)
                mz = mz[idx_sorted]
                intensities = intensities[idx_sorted]
    
            spectrums.append(Spectrum(mz=mz, intensities=intensities, metadata=metadata))



#%%
spectrums = []
for pyteomics_spectrum in mzml.read(filename, dtype=dict):

    metadata = pyteomics_spectrum.get("params", None)
    mz = pyteomics_spectrum["m/z array"]
    intensities = pyteomics_spectrum["intensity array"]

    # Sort by mz (if not sorted already)
    if not numpy.all(mz[:-1] <= mz[1:]):
        idx_sorted = numpy.argsort(mz)
        mz = mz[idx_sorted]
        intensities = intensities[idx_sorted]

    spectrum.append(Spectrum(mz=mz, intensities=intensities, metadata=metadata))


#%%
import pymzml
run = pymzml.run.Reader(file_mzml,
                        MS_precisions = {1: 5e-6,
                                         2: 20e-6})

for spectrum in run:
    pass