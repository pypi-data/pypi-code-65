import pandas as pd


class Header( object ):
    def __init__( self ):
        self._secstr = None

    @property
    def secondary_structures(self):
        return self._secstr


class HeaderFactory( object ):
    @staticmethod
    def factory( mmjson ):
        h = Header()
        h._secstr = HeaderFactory()._get_sse(mmjson)

        return h

    def _get_sse( self, mmjson ):
        a = pd.DataFrame(mmjson["_struct_sheet_range"])
        a["conf_type_id"] = ["STRN", ] * len(a["id"])
        return pd.concat([pd.DataFrame(mmjson["_struct_conf"]), a])
