def empty_call(*args, **kwargs):
    """
    Do nothing
    """
    pass


def empty_call_true(*args, **kwargs) -> bool:
    """
    Do nothing and return True
    """
    return True


def empty_call_false(*args, **kwargs) -> bool:
    """
    Do nothing and return False
    """
    return False