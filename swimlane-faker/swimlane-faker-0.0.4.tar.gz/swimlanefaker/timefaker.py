import pendulum
from .base import Base


class TimeFaker(Base):

    __pendulum = pendulum

    def __force_integer_in_pendulum_kwargs(self, params):
        return_dict = {}
        for key,val in params.items():
            if key in ['years', 'months', 'weeks','days', 'hours', 'minutes', 'seconds']:
                return_dict[key] = int(val)
        return return_dict

    def generate(self, value):
        new_values = value.split('.')
        new_values.pop(0)
        if new_values[0].startswith('now'):
            now = getattr(self.__pendulum, 'now')()
            if len(new_values) >= 2:
                if new_values[1].startswith('add'):
                    params = self.generate_kwargs(new_values[1], 'add')
                    if params:
                        params = self.__force_integer_in_pendulum_kwargs(params)
                        return getattr(now, 'add')(**params).to_iso8601_string()
                    else:
                        return getattr(now, 'add')().to_iso8601_string()
                elif new_values[1].startswith('subtract'):
                    params = self.generate_kwargs(new_values[1], 'subtract')
                    if params:
                        params = self.__force_integer_in_pendulum_kwargs(params)
                        return getattr(now, 'subtract')(**params).to_iso8601_string()
                    else:
                        return getattr(now, 'subtract')().to_iso8601_string()
            else:
                return getattr(self.__pendulum, 'now')().to_iso8601_string()
