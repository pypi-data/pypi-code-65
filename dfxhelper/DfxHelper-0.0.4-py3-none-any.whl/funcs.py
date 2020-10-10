import random, string


def random_str(length: int) -> str:
    seed = string.digits + string.ascii_letters
    return ''.join([
        random.choice(seed)
    for i in range(length)])
