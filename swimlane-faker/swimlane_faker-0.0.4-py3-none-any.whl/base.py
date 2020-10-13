import random


class Base:

    random = random

    def generate_kwargs(self, value, method_call):
        kwargs = {}
        params = value.split(method_call)[1].strip('(').strip(')')
        if params:
            key_vals = params.split(',')
            if len(key_vals) > 1:
                for item in key_vals:
                    if isinstance(item.split('=')[1], int):
                        kwargs[item.split('=')[0]] = int(item.split('=')[1])
                    else:
                        kwargs[item.split('=')[0]] = item.split('=')[1]
            else:
                if isinstance(key_vals[0].split('=')[1], int):
                    kwargs[key_vals[0].split('=')[0]] = int(key_vals[0].split('=')[1])
                else:
                    kwargs[key_vals[0].split('=')[0]] = key_vals[0].split('=')[1]
            return kwargs
        else:
            return None