import pandas as pd
import subprocess
import string
import io
import sacct.util


def split_steps(buf):
    for line in buf.readlines():
        s = line.split('|')
        if '.' in s[0]:
            yield '|'.join(s[0].split('.') + s[1:])


def option_string(k, v):
    if type(v) == bool:
        if v:
            return f"--{k}"
    elif type(v) == list:
        return f"--{k}={','.join(v)}"
    else:
        return f"--{k}={v}"


def build_command(options):
    cmd = ["sacct"]
    for k, v in options.items():
        opt = option_string(k, v)
        if opt is not None:
            cmd.append(opt)
    return cmd


class Sacct:
    def __init__(self, **kwargs):
        self.options = {
            "format": ["jobidraw", "start", "end", "nodelist"],
            "noheader": True,
            "parsable2": True,
            "truncate": True,
            "allocations": False
        }
        self.options.update(kwargs)

        for k in {"starttime", "endtime"}:
            if k in self.options:
                try:
                    self.options[k] = self.options[k].isoformat()
                except AttributeError:
                    pass

        self.cmd = build_command(self.options)

    def __str__(self):
        return ' '.join(self.cmd)

    def execute(self):
        stdout = subprocess.check_output(self.cmd)

        names = self.options['format'].copy()

        if not self.options['allocations']:
            names.insert(1, 'step')
            buf = io.StringIO('\n'.join(
                split_steps(io.StringIO(stdout.decode('utf8', 'ignore')))))
        else:
            buf = io.StringIO(stdout.decode('utf8', 'ignore'))

        df = pd.read_csv(buf, sep='|', header=None, names=names)

        # work around a Slurm bug with job steps and --truncate
        if not self.options['allocations'] and self.options['truncate']:
            if 'start' in df.columns and 'starttime' in self.options:
                starttime = self.options['starttime']
                df.loc[df['start'] == 'Unknown', 'start'] = starttime
            if 'end' in df.columns and 'endtime' in self.options:
                endtime = self.options['endtime']
                df.loc[df['end'] == 'Unknown', 'end'] = endtime

        for field in ['start', 'end', 'submit', 'eligible']:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field])

        for field in ['elapsed', 'reserved', 'timelimit']:
            if field in df.columns:
                df[field] = df[field].apply(sacct.util.str_to_timedelta)

        if 'nodelist' in df.columns:
            # another sacct bug, sometimes NodeList entries are truncated
            m = (df['nodelist'].str.contains("\\[") &
                 ~df['nodelist'].str.endswith(']'))
            df.loc[m, 'nodelist'] += ']'

        return df
