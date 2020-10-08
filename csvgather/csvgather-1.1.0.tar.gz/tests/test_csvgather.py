import csv
from docopt import DocoptExit
import pytest
import subprocess
import tempfile
import warnings

def test_cli() :
    from csvgather import main

    with tempfile.NamedTemporaryFile() as f :
        with pytest.raises(DocoptExit) :
            p = main(
                ['-j','0','-j','1','-f','counts',
                '-t','s:counts:{basename}_counts:',
                'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
                '-o',f.name
                ],
            )

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','counts',
            '-t','s:counts:{basename}_counts:',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter='\t')
            assert next(r) == ['ID','sample_A_counts','sample_B_counts','sample_C_counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','counts',
            '-t','s:counts:{basename}_counts:',
            '-t','s:_counts::',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '--dryrun'
            ],
        )
        
        # uncomment if you want to see the output of --dryrun
        #assert False

def test_cli_delim() :
    from csvgather import main
    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','counts',
            '-t','s:counts:{basename}_counts:',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',','
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['ID','sample_A_counts','sample_B_counts','sample_C_counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

def test_cli_fieldspec():
    from csvgather import main
    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','1',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',','
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['ID','counts','counts','counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            [# no field specified, 
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',','
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['ID','counts','counts','counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            [# no field specified, 
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',',',
            '--no-header'
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['col0','col1','col1','col1']
            assert next(r) == ['ID','counts','counts','counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            [# no field specified, 
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',',',
            '--no-header',
            '--join-column-name=ID'
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['ID','col1','col1','col1']
            assert next(r) == ['ID','counts','counts','counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','col1',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-t','s:col1:{basename}:',
            '-o',f.name,
            '-d',',',
            '--no-header'
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['col0','sample_A','sample_B','sample_C']
            assert next(r) == ['ID','counts','counts','counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']
