from unittest import TestCase
import unittest
import os
from types import ModuleType
from pathlib import Path
import csv

if 'env path':
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from geo_coor import (
        __version__,
    )
    from geo_coor.core import GeoCoordinate, OutputFormat
    from geo_coor.cli import main as cli_main
    from geo_coor.api.utils import after_end

    sys.path.remove(sys.path[0])


class CoreTests(TestCase):
    def test_basic(self):
        gc = GeoCoordinate()
        for tx, ty in [
            (550000, 2200000),  # http://lovegeo.blogspot.com/2015/08/l2_8.html
            (125000, 2750000)
        ]:
            print(gc.twd97_2_wgs84(tx, ty))

        for x, y in [
            (120.622139, 23.793658),  # 211511.90374706167 2644257.5998054836
            (120.621997, 23.792663)
        ]:
            tx, ty = gc.wgs84_2_twd97(x, y)
            print(tx, ty)
            _x, _y = gc.twd97_2_wgs84(tx, ty)
            self.assertTrue(x == _x and y == _y)

    def test_csv(self):
        gc = GeoCoordinate()
        for tx, ty in [
            (211494.579140393, 2632222.87049796),
        ]:
            print(gc.twd97_2_wgs84(tx, ty))

        with open(Path("./asset/csv/WGS84_TWD97.csv"), 'r', encoding='utf-8', newline='') as csv_file, \
            open(Path('./temp.output.csv'), 'w', encoding='utf-8',
                 newline='') as wf:  # newline = '' Avoid unnecessary blank lines

            csv_writer = csv.writer(wf, delimiter=",")  # init
            csv_writer.writerow(['tx (E)', 'ty (N)', 'x (latitude)', 'y (longitude)'])
            csv_file.readline()  # skip header
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row_list in csv_reader:
                ty, tx = n, e = row_list
                x, y = gc.twd97_2_wgs84(float(tx), float(ty))
                csv_writer.writerow([tx, ty, x, y])


class CSVConverterTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cvt = GeoCoordinate.CSVConverter(Path(r'./asset/csv/WGS84_TWD97.csv'))

    def test_csv(self):
        # with self.cvt.enter(1, 0, 2, 3, OutputFormat.WGS84) as df:  # specific column with int
        # with self.cvt.enter('E', 'N', 2, 3, Path('./Output.temp.csv'), OutputFormat.WGS84) as df:

        with self.cvt.enter(
            'E', 'N', 2, 3, OutputFormat.WGS84, Path('./Output.temp.csv'),

            # If you use int as the name of the new column, .then x will be __x__, and y will be __y__
            columns=['E', '__x__', 'N', '__y__']
        ) as df:
            ...

    def test_xlsx_output_file(self):
        with self.cvt.enter('E', 'N', 'x', 'y', OutputFormat.WGS84,
                            Path('./Output.temp.csv'), columns=['E', 'x', 'N', 'y']  # <-- options
                            ) as df:
            ...

    def test_xlsx_no_output(self):
        with self.cvt.enter('E', 'N', 'x', 'y', OutputFormat.WGS84,
                            columns=['E', 'x', 'N', 'y']  # <-- options
                            ) as df:
            ...


class CLITests(unittest.TestCase):

    def test_show_version(self):
        self.assertTrue(len(__version__) > 0)

    def test_feed_setting_file(self):
        setting_file_path = Path(__file__).parent / Path('setting.py')
        with after_end(cb_fun=lambda: os.remove(setting_file_path)) as _:
            with open(Path(__file__).parent.parent / Path('config.py'), 'r', encoding='utf-8') as config, \
                   open(setting_file_path, 'w', encoding='utf-8') as setting:
                data = config.read().replace('use default config', 'use test setting.py')
                # data = data.replace("SOURCE_CSV = Path('')", "SOURCE_CSV = Path('./asset/csv/WGS84_TWD97.csv')")
                setting.write(data)
                # setting.write("OUTPUT_FILE = Path('./temp.output.xlsx')\n")  # xlsx
                # setting.write("OUTPUT_FILE = Path('./temp.output.csv')\n")  # csv
                setting.write("COLUMNS = [COL_X, NEW_COL_X, COL_Y, NEW_COL_Y]\n")
            cli_main(setting_file_path)


def test_setup():
    # suite_list = [unittest.TestLoader().loadTestsFromTestCase(class_module) for class_module in (CLITests, )]
    # suite_class_set = unittest.TestSuite(suite_list)

    suite_function_set = unittest.TestSuite()
    suite_function_set.addTest(CLITests('test_show_version'))

    suite = suite_function_set  # pick one of two: suite_class_set, suite_function_set
    # unittest.TextTestRunner(verbosity=1).run(suite)  # self.verbosity = 0  # 0, 1, 2.  unittest.TextTestResult
    return suite


def run_all_tests_case(module: ModuleType):
    """
    It's better to run this function if you modify old source code, to check all services have exceptional.

    USAGE:

        1. run_all_tests_case(sys.modules[__name__])
        2. run_all_tests_case(your_test_module)
    """
    from console_color import create_print, RGB, cprint, Style
    import inspect
    cur_module = module
    print(f'working on {cprint(cur_module.__file__, RGB.GREEN, pf=False)}')
    bp = create_print(fore=RGB.BLUE, bg=RGB.YELLOW, style=Style.ITALIC, pf=False)

    def blue_print(msg):
        return bp(' ' + str(msg) + ' ')

    tests_class_list = [the_class for class_name, the_class in inspect.getmembers(cur_module, inspect.isclass) if
                        class_name.endswith('Tests')]
    suite_list = [unittest.TestLoader().loadTestsFromTestCase(class_module) for class_module in tests_class_list]
    suite_class_set = unittest.TestSuite(suite_list)

    # suite_function_set = unittest.TestSuite()
    # suite_function_set.addTest(CLITests('test_show_version'))

    suite = suite_class_set  # pick one of two: suite_class_set, suite_function_set
    result = unittest.TextTestRunner(verbosity=1).run(suite)  # self.verbosity = 0  # 0, 1, 2.  unittest.TextTestResult
    print('\n'.join([
        f'Run {blue_print(str(result.testsRun))} tests',
        f'errors: {blue_print(str(len(result.errors)))}',
        f'failures: {blue_print(str(len(result.failures)))}']))
    return result


def main():
    # CSVConverterTests().test_xlsx_no_output()
    CLITests().test_feed_setting_file()


if __name__ == '__main__':
    # run_all_tests_case(sys.modules[__name__])
    main()
    ...
