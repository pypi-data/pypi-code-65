import random
import string

""" This module generates a random password consisting of special characters, letters and digits. """


def __checker(input_int):
    lock = True
    while lock != False:
        if 8 <= input_int <= 20:
            return int(input_int)
        else:
            raise ValueError(
                "Input number must be an integer with size in the range of 8 to 20")


def generate(input_int):
    """ Parameters:
        input_int: must be an integer showing the number of characters required in the password
        return type: generate() returns a randomly generated password
    """
    try:
        __checker(input_int)
    except ValueError as e:
        print(e)
    except TypeError as t:
        print(t)
    else:
        generated_password = "".join(random.choices(
            string.ascii_letters+string.digits+"!@#$%^&*", k=input_int))
        print(f"Suggested Password for you : {generated_password}")
