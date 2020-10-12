import pendulum
from .base import Base


class RandomFaker(Base):

    def generate(self, value):
        striped_value = value.strip('[').strip(']')
        if '|' in striped_value:
            striped_values = striped_value.split('|')
            return self.random.choice(striped_values)
        elif 'int:' in striped_value:
            striped_values = striped_value.strip('int:')
            return self.random.randint(int(striped_values.split('-')[0]), int(striped_values.split('-')[1]))
        elif 'datetime:' in striped_value:
            date_time = striped_value.split('datetime:')[1]
            if '+' in date_time:
                start,end = date_time.split('+')
                return self.__generate_datetime(start,end, '+')
            if '-' in date_time:
                start,end = date_time.split('-')
                return self.__generate_datetime(start,end, '-')
        
    def __generate_datetime(self, start, end, expression):
        start_range = None
        end_range = None
        if start == 'now':
            start_range = pendulum.now()
            if expression is '-':
                if 'd' in end and end[0].isdigit():
                    return start_range.subtract(days=int(end[0])).to_iso8601_string()
                elif 'h' in end and end[0].isdigit():
                    return start_range.subtract(hours=int(end[0])).to_iso8601_string()
                elif 'm' in end and end[0].isdigit():
                    return start_range.subtract(minutes=int(end[0])).to_iso8601_string()
                elif 's' in end and end[0].isdigit():
                    return start_range.subtract(seconds=int(end[0])).to_iso8601_string()
            if expression is '+':
                if 'd' in end and end[0].isdigit():
                    return start_range.add(days=int(end[0])).to_iso8601_string()
                elif 'h' in end and end[0].isdigit():
                    return start_range.add(hours=int(end[0])).to_iso8601_string()
                elif 'm' in end and end[0].isdigit():
                    return start_range.add(minutes=int(end[0])).to_iso8601_string()
                elif 's' in end and end[0].isdigit():
                    return start_range.add(seconds=int(end[0])).to_iso8601_string()