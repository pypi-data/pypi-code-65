'''
Usage: csvgather.py [options] [-j PATT]... [-f PATT]... [-t STR]... <csv_fn>...

Options:
  -h --help               This helpful help help help help is a weird word
  -d STR --delimiter=STR  Character(s) to use as the delimiter in the output,
                          can be multiple characters [default: \t]
  -o PATH --output=PATH   Output to file [default: stdout]
  -j COL --join=COL       Column to join on. Can take one of two forms:
                            - 0-based integer indicating column index, can be
                              negative to index from the end of the columns
                            - a regular expression that will use any columns it
                              matches as the join columns
                          Only one join column may be specified. [default: 0]
  --join-column-name=COL  Replace the selected join column name with COL.
  -f COL --field=COL      Column(s) to select fields for concatenation. Uses
                            - 0-based integer indicating column index, can be
                              negative to index from the end of the columns
                            - a half closed interval of 0-based integers to
                              specify a range of columns (e.g. 0:4 or 0:-1)
                            - a regular expression that will use any columns it
                              matches as the join columns
                            - a pair of regular expressions to specify a range
                              of columns (e.g. geneName:strand will start with
                              the column geneName and end with column strand)
                          May be specified multiple times and any matching
                          columns will be included. Column selection occurs
                          before application of transformations (-t). Joined
                          columns are not included in the field match [default: 1:]
  --no-header -n          Assume files have no header row and label them like
                          col0, col1, col2... -j, -f, and -t then work on
                          these column names.
  -t STR --transform=STR  A string of the form "s:patt:repl:[gi]" to apply to
                          every column name. The special strings {path}, {dir},
                          {fn}, and {basename} can be used in the repl string to
                          refer to the full path, parent directory name, file
                          name, and filename without extension (i.e. [.][^.]*$)
                          repl may be empty. If specified more than once, each
                          subsequent transform will be applied to the previously
                          transformed sample names in the order provided on the
                          command line
  --join-type=STR         Type of join, one of 'outer', 'inner', or 'left'.
                          outer will create a row for every distinct value in
                          the -j column(s), inner will report only rows that
                          are found in all files, and left will join files from
                          left to right [default: outer]
  --empty-val=VAL         The value to use when an outer or left join does not
                          find a corresponding row in a file [default: ]
  --comment=CHAR          Lines starting with CHAR are considered comments in
                          input files and will be skipped [default: #]
  --dryrun                Print out info about what will be done to join and
                          select columns
'''

#TODO
'''
  --strict                Fail on any of the following:
                            - specified join columns do not exist in all files
                            - -j or -f columns do not match any fields in any
                              single file
                            - -t does not apply to any columns
'''

from collections import defaultdict
import csv
from docopt import docopt, DocoptExit
import os
import pandas
from pprint import pprint
import re
import sys
import warnings

# ignore pandas parsing warnings since we are sniffing on our own
warnings.filterwarnings(action='ignore',message='Conflicting values for')

def unique(l) :
    '''Return only unique elements of l in place'''
    if not l :
        return []
    else :
        if l[-1] in l[:-1] :
            return unique(l[:-1])
        else :
            return unique(l[:-1])+[l[-1]]

index_re = re.compile(r'(?P<start>[-]?\d+)(:(?P<end>[-]?\d+))?')
regex_re = re.compile(     r'(?P<start>[^:]*(\[:\])?[^:]+)'
                                             r'(:(?P<end>.*(\[:\])?.+))?')
def parse_spec(spec) :

    if index_re.match(spec) :
         m = index_re.match(spec)
         col_start = int(m.group('start'))
         col_end = m.group('end')
         col_end = int(col_end) if col_end is not None else col_end
    elif regex_re.match(spec) :
         m = regex_re.match(spec)
         col_start = re.compile(m.group('start'))
         col_end = m.group('end')
         col_end = re.compile(col_end) if col_end is not None else col_end
    else :
        raise Exception('Could not understand column spec: {}'.format(spec))

    return col_start, col_end

def filter_columns(cols,spec) :
    filt_cols = []
    for col_st, col_en in spec :
        if isinstance(col_st,int) : # indices
            if col_en is not None :
                filt_cols.extend(cols[col_st:col_en])
            else :
                filt_cols.append(cols[col_st])
        else : # regex
            if col_en is not None :
                st_matches = [cols.index(_) for _ in cols if col_st.search(_)]
                en_matches = [cols.index(_) for _ in cols if col_en.search(_)]
                filt_cols.extend(cols[min(st_matches):max(en_matches)+1])
            else :
                st_matches = [_ for _ in cols if col_st.search(_)]
                filt_cols.extend(st_matches)

    filt_cols = unique(filt_cols)

    return filt_cols

def main(args=sys.argv[1:]) :

    args = docopt(__doc__,argv=args)

    # validate args
    if len(args['--join']) > 1 :
        raise DocoptExit('--join may be specified only once')

    try:
        join_col_spec = parse_spec(args['--join'][0])
    except Exception as e:
        raise DocoptExit('--join: '+e.msg)

    field_col_spec = []
    for field_spec in args['--field'] :
        try:
            field_col_spec.append(parse_spec(field_spec))
        except Exception as e:
            raise DocoptExit('--field: '+e.msg)

    # transform
    transforms = []
    transf_re = re.compile(r'^s:(?P<patt>[^:]*(\[[:*+[]|]\])?[^:]+)+'
                                                     r':(?P<repl>[^:]*(\[[:*+[]|]\])?[^:]+)*'
                                                     ':(?P<mode>g?i?)$')
    for transf_spec in args['--transform'] :
        m = transf_re.match(transf_spec)
        if m :
            transforms.append((m.group('patt'),m.group('repl'),m.group('mode')))
        else :
            raise DocoptExit('Could not understand the transformation spec: {}'.format(transf_spec))

    # join type
    if args['--join-type'] not in ('outer','inner','left') :
        raise DocoptExit('--join-type must be one of outer, inner, or left')

    merged = None

    # by default column names are passed through unmodified
    # doing pandas.merge adds suffixes to duplicate column names
    # maintain the actual possibly duplicated column names so
    # they may be correctly set later
    join_cols = []
    final_select_col_names = []

    debug_transform_paths = defaultdict(lambda: defaultdict(list))
    for fn in args['<csv_fn>'] :
        with open(fn,'rt') as f :
          # sniffing formats in the presence of comments is really hard
          # apparently, scan to the middle of the file for a sample
          lines = []
          for l in f :
            if l[0] not in args['--comment'] :
              lines.append(l)
            if len(lines) == 1000 :
              break
          if len(lines) == 0 :
            warnings.warn('{} had no non-comment lines, skipping'.format(fn))
            continue
          sniff = csv.Sniffer().sniff(''.join(lines),delimiters=',\t')
          f.seek(0)

          names = None

          if args['--no-header'] :
              row = next(csv.reader(f,dialect=sniff))
              f.seek(0)

              names = ['col{}'.format(_) for _ in range(len(row))]

          nrows = None
          if args['--dryrun'] :
              nrows = 3 # only read in a couple lines if doing dryrun

          df = pandas.read_csv(f,dialect=sniff,names=names,nrows=nrows,comment='#') 

        # select join columns
        join_col = filter_columns(df.columns.tolist(),[join_col_spec])
        if len(join_col) == 0 :
            raise Exception('No join columns were selected, aborting')
        if len(join_col) > 1 :
            raise Exception('More than one join column was selected from join col spec, aborting')

        join_cols.append(join_col)

        # selected fields
        select_cols = filter_columns(df.columns.tolist(),field_col_spec)

        # if the arguments selected the same column as a join and field
        # prioritize join but warn the user
        # TODO bail if --strict supplied
        if not set(join_col).isdisjoint(select_cols) :
            warnings.warn('-j and -f specified have overlapping columns, '
                    'prioritizing join fields'
                    )
            select_cols = [_ for _ in select_cols if _ not in join_col]

        df.index = df[join_col]
        df.drop(columns=join_col,inplace=True)
        df = df[select_cols]

        # transform fields
        fn_dir, fn_base = os.path.split(fn)
        fn_basename, fn_ext = os.path.splitext(fn_base)
        for patt, repl, mode in transforms :
            count = 0 if 'g' in mode else 1
            flag = re.I if 'i' in mode else 0
            if repl is None : # repl was empty
              repl = ''
            else:
              repl = repl.replace('{path}',fn)
              repl = repl.replace('{dir}',fn_dir)
              repl = repl.replace('{fn}',fn_base)
              repl = repl.replace('{basename}',fn_basename)
              repl = repl.replace('&',r'\g<0>')

            for i, colname in enumerate(select_cols) :
                new_col = re.sub(patt,repl,colname,count,flag)
                df.rename(
                    columns={colname:new_col},
                    inplace=True
                )
                debug_transform_paths[fn][i].append(
                    (colname,'s:{}:{}:{}'.format(patt,repl,mode),new_col)
                )

            select_cols = df.columns

        final_select_col_names.extend(select_cols)

        if merged is None :
          merged = df
        else :
          merged = pandas.merge(merged,df,
                  how=args['--join-type'],
                  left_index=True,
                  right_index=True
          )

    merged.fillna(args['--empty-val'],inplace=True)

    join_col = join_cols[0]
    if args['--join-column-name'] is not None :
        join_col = [args['--join-column-name']]

    if args['--dryrun'] :
        print('Column name transformations:')
        for fn, flds in debug_transform_paths.items() :
            print(fn)
            for i, path in flds.items() :
                sys.stdout.write('  {}: '.format(i))
                for before, trans, after in path :
                    sys.stdout.write('{} -({})> '.format(before,trans))
                sys.stdout.write(path[-1][-1]+'\n')

        print('Final columns')
        for i, col in enumerate(join_col+final_select_col_names) :
            print('  {}: {}'.format(i,col))

    else :

        out_f = sys.stdout if args['--output'] == 'stdout' else open(args['--output'],'wt')

        out_csv = csv.writer(out_f,delimiter=args['--delimiter'])
        out_csv.writerow(join_col+final_select_col_names)
        for k, row in merged.iterrows() :
          out_csv.writerow(list(k)+row.tolist())

if __name__ == '__main__' :


    main()
