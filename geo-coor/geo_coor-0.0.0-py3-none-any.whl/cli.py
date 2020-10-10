from geo_coor import __version__
from geo_coor.core import GeoCoordinate
from geo_coor.api.utils import work_dir
import importlib.machinery
from pathlib import Path
import types
from typing import Any


def main(input_setting_path=None):
    import inspect
    import argparse
    if input_setting_path is None:
        arg_parser = argparse.ArgumentParser(prog='geo_coor.exe',
                                             formatter_class=argparse.RawTextHelpFormatter)  # allow \n \t ...
        arg_parser.add_argument('--version', action='version', version='%(prog)s:' + f'{__version__}')
        arg_parser.add_argument('setting', type=Path,
                                help="path of setting.py")  # default=Path(__file__).parent / Path('config.py')
        args = arg_parser.parse_args()
    else:
        args = types.SimpleNamespace(**dict(setting=input_setting_path))
        if not isinstance(args.setting, Path):
            raise RuntimeError

    with work_dir(args.setting.parent):
        loader = importlib.machinery.SourceFileLoader('setting', args.setting.name)
        config = setting_module = types.ModuleType(loader.name)  # type: Any
        loader.exec_module(setting_module)

        """
        # Solve the problem of the relative path.
        [setattr(setting_module, member_name, str(member.resolve())) for member_name, member in
         inspect.getmembers(setting_module) if not member_name.startswith('_') and isinstance(member, Path)]
        """

        source_csv: Path = config.SOURCE_CSV
        if not source_csv.exists() or not source_csv.is_file() or source_csv.suffix.upper() != '.CSV':
            raise FileNotFoundError(config.SOURCE_CSV)

        cvt = GeoCoordinate.CSVConverter
        with cvt(config.SOURCE_CSV).enter(
            config.COL_X, config.COL_Y, config.NEW_COL_X, config.NEW_COL_Y, config.FMT,
                output_path=config.OUTPUT_FILE, columns=getattr(config, 'COLUMNS', None)) as df:
            ...
            print('done')


if __name__ == '__main__':
    main()
