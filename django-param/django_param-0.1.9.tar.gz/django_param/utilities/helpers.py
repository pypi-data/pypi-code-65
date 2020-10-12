"""
Various helper functions for the ParamForm.
"""


def clean_data(in_data, is_dict=False):
    """
    Clean data from form field submission, converting to Python values if necessary.

    Args:
        in_data (list, tuple, or str): The data either as a list/tuple of string values or a single string value.
        is_dict (bool): Set to True if data is a dictionary. Defaults to False.

    Returns:
        various: the cleaned data.
    """
    if isinstance(in_data, (list, tuple)):
        out_data = []
        for data in in_data:
            out_data.append(convert_string(data))
        if not is_dict:
            out_data = tuple(out_data)
    else:
        out_data = convert_string(in_data)
        if is_dict:
            temp_data = list()
            temp_data.append(out_data)
            out_data = temp_data
    return out_data


def convert_string(data):
    """
    Convert string values to Python value (e.g.: "True" => True, "1.3" => 1.3).

    Args:
        data (str): The data string (e.g. "True", "2", "1.5").

    Returns:
        various: The value if it is a number or boolean, else the original string is returned.
    """
    if is_number(data):
        if "." in data:
            data = float(data)
        else:
            data = int(data)
    if data == 'True' or data == 'on':
        data = True
    if data == 'False':
        data = False
    return data


def is_number(s):
    """
    Determine if a string is a numeric string (e.g. "1.4" and "2").

    Args:
        s (str): The string.

    Returns:
        bool: True if the string is a numeric string.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_boolean(s):
    """
    Determine if a string is a boolean string (e.g.: "True" or "False").

    Args:
        s (str): The string.

    Returns:
        bool: True if the string is a boolean string.
    """
    if str(s).lower() in ['true', 'false']:
        return True
    else:
        return False


def is_checkbox(s):
    """
    Determine if given string represents a checkbox field name.

    Args:
        s (str): The string.

    Returns:
        bool: True if the given string is a checkbox field name.
    """
    if str(s).lower() in ['__checkbox_end__', '__checkbox_begin__']:
        return True
    else:
        return False


def get_dataframe_name(s):
    """
    Split dataframe and variable name from dataframe form field names (e.g. "___<var_name>___<dataframe_name>__").

    Args:
        s (str): The string

    Returns:
        2-tuple<str>: The name of the variable and name of the dataframe. False if not a properly formatted string.
    """
    # Return tuple with variable_name, and dataframe_name if the type is dataframe.
    if s[-2:] == "__":
        s = s[:-2]
        dataframe_name = s.split("___")[-1]
        variable_name = s.split("___")[0]
        return variable_name, dataframe_name
    else:
        return False


def remove_item_tuple(data, index):
    """
    Remove an item from the given tuple.

    Args:
        data (tuple): The tuple with item to remove.
        index (int): The index of item to remove from tuple.

    Returns:
        tuple: A new tuple with the item at index removed.
    """
    list_data = list(data)
    del list_data[index]
    new_tuple = tuple(list_data)
    return new_tuple


def update_item_tuple(data, index, value):
    """
    Update the value of an item in a tuple.

    Args:
        data (tuple): The tuple with item to update.
        index (int): The index of the item to update.
        value (various): The new value for the item to be updated.

    Returns:
        tuple: A new tuple with the updated value.
    """
    list_data = list(data)
    list_data[index] = value
    new_tuple = tuple(list_data)
    return new_tuple
