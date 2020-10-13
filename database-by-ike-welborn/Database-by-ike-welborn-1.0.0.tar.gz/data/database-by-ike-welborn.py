def random(data):
    from random import choice
    print(choice(data))
def store(data):
    open("data.txt", "x")
    with open("data.txt", "w") as dat:
        dat.write(str(data))
