## generic modules
import time
import multiprocessing
import pandas as pd
import sys
import gzip
from multiprocessing.pool import ThreadPool



#RDkit specific modules
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import PandasTools
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors

#MolVS specific modules

import molvs
from molvs import Standardizer
from molvs import Validator
# from molvs.fragment import LargestFragmentChooser
# from molvs.fragment import FragmentRemover
# or eventually load the local (modified) fragment.py
#import fragment
# from .fragment import LargestFragmentChooser
# from .fragment import FragmentRemover
from .fragment import LargestFragmentChooser
from .fragment import FragmentRemover
from molvs.charge import Uncharger



# custom functions 


def printer(inchi):
    print(inchi)

def MolFromInchi_fun(inchi):
    m = Chem.MolFromInchi(inchi)
    if m:
        return m
    return None

def MolFromSmiles_fun(smiles):
    m = Chem.MolFromSmiles(smiles)
    if m:
        return m
    return None

def MolToSmiles_fun(romol):
    m = Chem.MolToSmiles(romol)
    if m:
        return m
    return None

def MolToInchi_fun(romol):
    m = Chem.MolToInchi(romol)
    if m:
        return m
    return None

def MolToInchi_fun_safe(smiles, romol):
    #print(smiles) (beware as too much print statement will crash \\
    # interactve python console such as the one in vscode)
    if '[O]' not in smiles:
        m = Chem.MolToInchi(romol)
        if m:
            return m
        return None
    else:
        print('Sayonara Robocop !')
        return None

def MolToIK_fun(romol):
    m = Chem.MolToInchiKey(romol)
    if m:
        return m
    return None

def MolToIK_fun_safe(smiles, romol):
    #print(smiles) (beware as too much print statement will crash \\
    # interactve python console such as the one in vscode)
    if '[O]' not in smiles:
        m = Chem.MolToInchiKey(romol)
        if m:
            return m
        return None
    else:
        print('Sayonara Babeee !')
        return None


def MolToMF_fun(romol):
    m = rdMolDescriptors.CalcMolFormula(romol)
    if m:
        return m
    return None

def MolToEmass_fun(romol):
    m = Descriptors.ExactMolWt(romol)
    if m:
        return m
    return None

def MolToLogP_fun(romol):
    m = Chem.Crippen.MolLogP(romol)
    if m:
        return m
    return None



# defining the validator log output format
fmt = '%(asctime)s - %(levelname)s - %(validation)s - %(message)s'

# save the Standardizer and LargestFragmentChooser classes as variables

def validator_fun(romol):
    print(romol.GetNumAtoms)
    m = Validator(log_format=fmt).validate(romol)
    if m:
        return m
    return None

def standardizor_fun(romol):
    print('standardizer ' + str(romol.GetNumAtoms))
    m = Standardizer().standardize(romol)
    if m:
        return m
    return None

def fragremover_fun(romol):
    print('fragremover ' + str(romol.GetNumAtoms))
    m = FragmentRemover().remove(romol)
    if m:
        return m
    return None

def uncharger_fun(romol):
    print('uncharger ' + str(romol.GetNumAtoms))
    m = Uncharger().uncharge(romol)
    if m:
        return m
    return None

# generic function 

def gzipper(input_file_path, in_sep_type, out_sep_type):
    
    """
    A function to compress a file

    ...

    Attributes
    ----------
    input_file_path : str
        the input file path
    in_sep_type : str
        the type of separator to parse the input file (choose between ',' and '\t')
    out_sep_type : str
        the type of separator to write the output file (choose between ',' and '\t')

    Example 
    -------
    gzipper('path/to/your_file.tsv', sep = '\t')

    """

    df = pd.read_csv(
    input_file_path,
    sep = in_sep_type)

    df.to_csv(
    str(input_file_path + '.gz'), 
    sep = out_sep_type, 
    index = False,
    compression = 'gzip'
    )


def chemo_sanitizer_thread(input_file_path, output_file_path, smiles_column_header, struct_type, cpus ):
    """
    '''Please add input and output file path as first and second argument, InChI column header as third argument and finally the number of cpus you want to use.
        Example :
        python chemosanitizer.py ~/translatedStructureRdkit.tsv ./test.tsv structureTranslated 6'''
    """
        
    myZip = gzip.open(input_file_path)

    df = pd.read_csv(
        myZip,
        sep = '\t')


    df = df[~df[smiles_column_header].isnull()]

    df.columns
    df.info()

    # the full df is splitted and each subdf are treated sequentially as df > 900000 rows retruned errors 
    # (parralel treatment of these subdf should improve performance)
    n = 20000  # chunk row size
    list_df = [df[i:i+n] for i in range(0,df.shape[0],n)]

    # timer is started
    start_time = time.time()

    for i in range(0, len(list_df)):

        # here we define the multiprocessing wrapper for the function. Beware to set the number of running tasks according to your cpu number

    # if __name__ == "__main__":
        # with multiprocessing.Pool(multiprocessing.cpu_count() - 2 ) as pool:
        with ThreadPool(int(cpus)) as pool:

            # # we generate ROMol object from smiles and or inchi
            list_df[i]['ROMol'] = pool.map(MolFromSmiles_fun, list_df[i][smiles_column_header])
            # # we eventually remove rows were no ROMol pobject was generated
            list_df[i] = list_df[i][~list_df[i]['ROMol'].isnull()]
            # # and now apply the validation, standardization, fragment chooser and uncharging scripts as new columns.
            # # Note that these are sequentially applied
            list_df[i]['validatorLog'] = pool.map(validator_fun, list_df[i]['ROMol'])
            list_df[i]['ROMolSanitized'] = pool.map(standardizor_fun, list_df[i]['ROMol'])
            list_df[i].drop('ROMol', axis=1, inplace=True)
            list_df[i]['ROMolSanitizedLargestFragment'] = pool.map(fragremover_fun, list_df[i]['ROMolSanitized'])
            list_df[i].drop('ROMolSanitized', axis=1, inplace=True)
            list_df[i]['ROMolSanitizedLargestFragmentUncharged'] = pool.map(uncharger_fun, list_df[i]['ROMolSanitizedLargestFragment'])
            list_df[i].drop('ROMolSanitizedLargestFragment', axis=1, inplace=True)
            # # outputting smiles, inchi, molecular formula, exact mass and protonated and deprotonated exactmasses from the latest object of the above scripts
            list_df[i]['smilesSanitized'] = pool.map(MolToSmiles_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            # for the inchi and IK since some specific structures are raising issues we use the ***_fun_safe functions (see associated chemosanitizer_function.py)
            # list_df[i]['inchi_sanitized'] = pool.map(MolToInchi_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            list_df[i]['inchiSanitized'] = pool.starmap(MolToInchi_fun_safe, zip(list_df[i]['smilesSanitized'], list_df[i]['ROMolSanitizedLargestFragmentUncharged']))
            #list_df[i]['inchikeySanitized'] = pool.map(MolToIK_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            list_df[i]['inchikeySanitized'] = pool.starmap(MolToIK_fun_safe, zip(list_df[i]['smilesSanitized'], list_df[i]['ROMolSanitizedLargestFragmentUncharged']))
            list_df[i]['shortikSanitized'] = list_df[i]['inchikeySanitized'].str.split("-", n=1, expand=True)[0]
            list_df[i]['formulaSanitized'] = pool.map(MolToMF_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            list_df[i]['exactmassSanitized'] = pool.map(MolToEmass_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            list_df[i]['xlogpSanitized'] = pool.map(MolToLogP_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
            list_df[i].drop('ROMolSanitizedLargestFragmentUncharged', axis=1, inplace=True)
            
            pool.close()
            pool.join()

            # list_df[i].to_csv(
            #     "/home/EPGL.UNIGE.LOCAL/allardp/opennaturalproductsdb/data/interim/tables/2_cleaned/structure/oouthoupla_%i.csv" % i , 
            #     sep = '\t', 
            #     index = False,
            #     compression = 'gzip'
            #     )

    # timer is stopped
    print(" Above command executed in --- %s seconds ---" %
        (time.time() - start_time))

    # we merge the previously obtained df
    df = pd.concat(list_df)

    # # dropping some irrelevant columns prior to export
    # colstodrop = ['ROMol',
    #               'ROMolSanitized',
    #               'ROMolSanitizedLargestFragment',
    #               'ROMolSanitizedLargestFragmentUncharged'
    #               ]
    # colstodrop = ['ROMolSanitizedLargestFragmentUncharged']
    # df.drop(colstodrop, axis=1, inplace=True)

    df.info()

    # exporting df
    import os
    import errno
    filename = output_file_path
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
                
    # df.to_csv(ouput_file_path, sep='\t', index=False)
    df.to_csv(
        output_file_path, 
        sep = '\t', 
        index = False,
        compression = 'gzip'
        )


def chemo_sanitizer_fun(input_file_path, output_file_path, struct_column_header, struct_type, cpus ):
    """
    A function to sanitize a gzipped table contaning SMILES or InChI encoded chemical structures

    ...

    Attributes
    ----------
    input_file_path : str
        the input file path
    output_file_path : str
        the output file path
    struct_column_header : str
        the chemical structure column header
    struct_type : str
        the type of encoding of the chemical structure field (choose between 'SMILES' and 'InChI'). Beware it's case sensitive for now.
    cpus : int
        the number of cores to parallelize the calculation on. Try to set to less than the maximum

    Example 
    -------
    chemo_sanitizer('path/to/your_file.tsv.gz', 'path/to/your_file_sanitized.tsv.gz', 'smiles_column', 'SMILES', 12)

    """

        
    myZip = gzip.open(input_file_path)

    df = pd.read_csv(
        myZip,
        sep = '\t')


    df = df[~df[struct_column_header].isnull()]

    df.columns
    df.info()

    # the full df is splitted and each subdf are treated sequentially as df > 900000 rows retruned errors 
    # (parralel treatment of these subdf should improve performance)
    n = 20000  # chunk row size
    list_df = [df[i:i+n] for i in range(0,df.shape[0],n)]

    # timer is started
    start_time = time.time()

    for i in range(0, len(list_df)):

        # here we define the multiprocessing wrapper for the function. Beware to set the number of running tasks according to your cpu number

        if __name__ == "__main__":
            # with multiprocessing.Pool(multiprocessing.cpu_count() - 2 ) as pool:
            with multiprocessing.Pool(int(cpus)) as pool:
                if struct_type == 'SMILES':
                # # we generate ROMol object from smiles and or inchi
                    list_df[i]['ROMol'] = pool.map(MolFromSmiles_fun, list_df[i][struct_column_header])
                elif struct_type == 'InChI':
                    # # we generate ROMol object from smiles and or inchi
                    list_df[i]['ROMol'] = pool.map(MolFromInchi_fun, list_df[i][struct_column_header])
                # # we eventually remove rows were no ROMol pobject was generated
                list_df[i] = list_df[i][~list_df[i]['ROMol'].isnull()]
                # # and now apply the validation, standardization, fragment chooser and uncharging scripts as new columns.
                # # Note that these are sequentially applied
                list_df[i]['validatorLog'] = pool.map(validator_fun, list_df[i]['ROMol'])
                list_df[i]['ROMolSanitized'] = pool.map(standardizor_fun, list_df[i]['ROMol'])
                list_df[i].drop('ROMol', axis=1, inplace=True)
                list_df[i]['ROMolSanitizedLargestFragment'] = pool.map(fragremover_fun, list_df[i]['ROMolSanitized'])
                list_df[i].drop('ROMolSanitized', axis=1, inplace=True)
                list_df[i]['ROMolSanitizedLargestFragmentUncharged'] = pool.map(uncharger_fun, list_df[i]['ROMolSanitizedLargestFragment'])
                list_df[i].drop('ROMolSanitizedLargestFragment', axis=1, inplace=True)
                # # outputting smiles, inchi, molecular formula, exact mass and protonated and deprotonated exactmasses from the latest object of the above scripts
                list_df[i]['smilesSanitized'] = pool.map(MolToSmiles_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                # for the inchi and IK since some specific structures are raising issues we use the ***_fun_safe functions (see associated chemosanitizer_function.py)
                # list_df[i]['inchi_sanitized'] = pool.map(MolToInchi_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                list_df[i]['inchiSanitized'] = pool.starmap(MolToInchi_fun_safe, zip(list_df[i]['smilesSanitized'], list_df[i]['ROMolSanitizedLargestFragmentUncharged']))
                #list_df[i]['inchikeySanitized'] = pool.map(MolToIK_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                list_df[i]['inchikeySanitized'] = pool.starmap(MolToIK_fun_safe, zip(list_df[i]['smilesSanitized'], list_df[i]['ROMolSanitizedLargestFragmentUncharged']))
                list_df[i]['shortikSanitized'] = list_df[i]['inchikeySanitized'].str.split("-", n=1, expand=True)[0]
                list_df[i]['formulaSanitized'] = pool.map(MolToMF_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                list_df[i]['exactmassSanitized'] = pool.map(MolToEmass_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                list_df[i]['xlogpSanitized'] = pool.map(MolToLogP_fun, list_df[i]['ROMolSanitizedLargestFragmentUncharged'])
                list_df[i].drop('ROMolSanitizedLargestFragmentUncharged', axis=1, inplace=True)
                
                pool.close()
                pool.join()

                # list_df[i].to_csv(
                #     "/home/EPGL.UNIGE.LOCAL/allardp/opennaturalproductsdb/data/interim/tables/2_cleaned/structure/oouthoupla_%i.csv" % i , 
                #     sep = '\t', 
                #     index = False,
                #     compression = 'gzip'
                #     )

    # timer is stopped
    print(" Above command executed in --- %s seconds ---" %
        (time.time() - start_time))

    # we merge the previously obtained df
    df = pd.concat(list_df)

    # # dropping some irrelevant columns prior to export
    # colstodrop = ['ROMol',
    #               'ROMolSanitized',
    #               'ROMolSanitizedLargestFragment',
    #               'ROMolSanitizedLargestFragmentUncharged'
    #               ]
    # colstodrop = ['ROMolSanitizedLargestFragmentUncharged']
    # df.drop(colstodrop, axis=1, inplace=True)

    df.info()

    # exporting df
    import os
    import errno
    filename = output_file_path
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
                
    # df.to_csv(ouput_file_path, sep='\t', index=False)
    df.to_csv(
        output_file_path, 
        sep = '\t', 
        index = False,
        compression = 'gzip'
        )
