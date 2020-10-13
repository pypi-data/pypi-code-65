import random


async def stringify(num):
    """
    makes a number a string
    """
    return f"{num}"
    pass


def concat(str1, str2, seperator: str = None):
    """
    concatenates 2 strings if there is a seperator joins them with it
    """
    if seperator == None:
        return f"{str1}{str2}"
    else:
        return f"{str1}{seperator}{str2}"
    pass


def random_num_goal(minN: int, maxN: int, goal: int, tries: int = None):
    """
    will return how many tries it took to get `goal`\n
    if there is `tries` will try that many times to get it, if it doesnt get it it will return `None`
    """
    if minN > maxN:
        raise ValueError("minN must be lower or equal to maxN")
    if goal >= minN and goal <= maxN:
        fails = 0
        while True:
            if tries != None:
                if fails == tries:
                    return None
                    break
            num = random.randint(minN, maxN)
            if num == goal:
                return fails
                break

            fails += 1
            pass

    else:
        raise ValueError(
            "goal parameter must be higher than or equal to maxN and lower than or equal to minN")
        pass
    pass


print(random_num_goal(1,100,100))
