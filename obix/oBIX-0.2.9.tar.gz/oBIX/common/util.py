from oBIX.common.point import Point
from oBIX.common.data_type import DataType


class Util(object):

    @staticmethod
    def parse_data_type(data_type_str: str):
        data_type_str = data_type_str.lower()
        if data_type_str == DataType.real:
            return "real"
        elif data_type_str == DataType.bool:
            return "bool"
        elif data_type_str == DataType.int:
            return "int"
        elif data_type_str == DataType.str:
            return "str"
        else:
            return "str"

    @staticmethod
    def parse_point(point_dict: dict, data_type_str: str):
        try:
            if "@is" not in point_dict:
                return None
            if "obix:Point" not in point_dict["@is"]:
                return None
            point = Point()
            point.val = point_dict["@val"]
            # point.status = point_dict["@status"]
            point.href = point_dict["@href"]
            point.display = point_dict["@display"]
            point.name = str(point_dict["@href"]).split("/")[-2]
            point.data_type = Util.parse_data_type(data_type_str)
            slots = point_dict[data_type_str]

            for slot in slots:
                name = slot["@name"]
                value_str = None
                # @display is null but val has value
                # In this case, the final value is treated as None.
                if "{null}" not in slot["@display"]:
                    value_str = slot["@val"]
                setattr(point, name, value_str)
            return point
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def parse_points(points: object, data_type_str: str):
        result = []
        if isinstance(points, list):
            for data in points:
                point = Util.parse_point(data, data_type_str)
                if point is not None:
                    result.append(point)
        else:
            point = Util.parse_point(points, data_type_str)
            if point is not None:
                result.append(point)
        return result
