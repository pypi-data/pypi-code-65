from tabulate import tabulate


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def describe_person(self):
        print(f'This person is called {self.name} and is {self.age} years old')

    def print_table(self):
        print(tabulate([[self.name, self.age], ['Bob', 19]], headers=['Name', 'Age']))
