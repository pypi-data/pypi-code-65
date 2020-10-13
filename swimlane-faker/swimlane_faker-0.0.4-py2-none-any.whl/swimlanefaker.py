from .randomfaker import RandomFaker
from .timefaker import TimeFaker
from .datafaker import DataFaker


class SwimlaneFaker:

    def get(self, value):
        if value is 'True':
            return value
        elif value.startswith('[') and value.endswith(']'):
            return RandomFaker().generate(value)
        elif value.startswith('<<') and value.endswith('>>'):
            striped_value = value.replace('<<','').replace('>>','')
            if striped_value.lower().startswith('socfaker'):
                return DataFaker().generate(striped_value)
            if striped_value.lower().startswith('pendulum'):
                return TimeFaker().generate(striped_value)
