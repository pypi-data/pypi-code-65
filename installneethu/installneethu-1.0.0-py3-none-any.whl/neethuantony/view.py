import string
import random


def main():
    size = int(input("enter the string length"))
    char = string.ascii_uppercase + string.ascii_lowercase
    test = "".join(random.choice(char) for _ in range(size))
    return test


if __name__ == "__main__":
    main()

