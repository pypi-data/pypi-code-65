
from generallibrary import deco_cache


class Path_Spreadsheet:
    """ Spreadsheet methods for Path. """
    @property
    @deco_cache()
    def spreadsheet(self):
        """ Easy access to a dynamically one-time created Spreadsheet class, initalized with self (Path). """
        return self._spreadsheet()(self)

    @staticmethod
    @deco_cache()
    def _spreadsheet():
        class Spreadsheet:
            import pandas
            pd = pandas

            def __init__(self, path):
                self.path = path

            def write(self, df=None, overwrite=False):
                with WriteContext(self.path, overwrite=overwrite) as write_path:
                    pass

            def read(self):
                with ReadContext(self.path) as read_path:
                    pass

        return Spreadsheet


from generalfile.path_operations import WriteContext, ReadContext






































