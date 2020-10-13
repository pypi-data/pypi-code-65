import shlex
from functools import reduce
from socfaker import SocFaker
from .base import Base


class DataFaker(Base):

    soc_faker = SocFaker()

    def __check_socfaker_property(self, obj, value):
        if hasattr(obj, value):
            self.__check_socfaker_property(obj.value, )
        pass
        # if self.soc_faker

    def __check_if_integer(self, value):
        try:
            int(value)
            return int(value)
        except:
            return value

    def get_attr(self, obj, attr, default, asString=False, silent=True):
        """
        Gets any attribute of obj.
        Recursively get attributes by separating attribute names with the .-character.        
        Calls the last attribute if it's a function.

        Usage: get_attr(obj, 'x.y.z', None)
        """
        attr_list = []
        optional_param_dict = {}
        required_params = None
        params = None
        if '(' in attr and ')' in attr:
            attr, params = attr.split('(')
            params = params.strip(')')
        for item in attr.split('.'):
            if params and not optional_param_dict:
                attr_list.append(item)
                if '=' not in params:
                    required_params = params
                else:
                    optional_param_dict = dict(x.split('=') for x in params.split(','))
            else:
                attr_list.append(item)
        if optional_param_dict:
            params = {}
            for k,v in optional_param_dict.items():
                params[k] = self.__check_if_integer(v)
            attr = '.'.join([x for x in attr_list])
            attr = reduce(getattr, attr.split("."), obj)(**params)
        elif required_params:
            attr = '.'.join([x for x in attr_list])
            attr = reduce(getattr, attr.split("."), obj)(required_params.rstrip("'").lstrip("'"))
        else:
            attr = reduce(getattr, attr.split("."), obj)

        if hasattr(attr, '__call__'):
            attr = attr()
        if attr is None:
            return default
        else:
            return attr

    def generate(self, value):
        new_values = value.split('.')
        new_values.pop(0)
        new_values = '.'.join([x for x in new_values])        
        return self.get_attr(self.soc_faker, new_values, None)
