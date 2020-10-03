import json

class connect:
    def __init__(self, name="index", *, path=""):
        self.name = name
        self.path = path
        self.cache = []

        if self.cache.__len__() > 20:
            self.cache.pop(0)

        try:
            r = open(f"{self.path}/{self.name}.json", "r").read()
        except FileNotFoundError:
            w = open(f"{self.path}/{self.name}.json", "w+").write("{}")
            r = open(f"{self.path}/{self.name}.json", "r").read()

        self.database = json.loads(r)


    def get(self, *, printf=False):
        if printf: print(self.database)
        return self.database

    def save(self):
        return json.dump(self.database, open(f"{self.path}/{self.name}.json", "w+"), indent=4)

    def get_item(self, key, *, printf=False):
        if type(key) is str:
            if printf: print(self.database[key])
            return self.database[key]
        else:
            keys = ""
            for i in range(key.__len__()):
                keys += f"[\"{key[i]}\"]"
            if printf: print(eval(f"self.database{keys}"))
            return eval(f"self.database{keys}")

    def set_item(self, key, value):
        if type(key) is str:
            self.database[key] = value
            self.cache.append({"key": key, "value": value})
        else:
            keys = ""
            for i in range(key.__len__()):
                keys += f"[\"{key[i]}\"]"
            exec(f"self.database{keys} = value")
            self.cache.append({"key": key[-1], "value": value})

    def del_item(self, key):
        if type(key) is str:
            del self.database[key]
        else:
            keys = ""
            for i in range(key.__len__()):
                keys += f"[\"{key[i]}\"]"
            exec(f"del self.database{keys}")

    def find_cache(self, key):
        result = []
        for i in self.cache:
            if i["key"] == key:
                result.append(i)
        return result
