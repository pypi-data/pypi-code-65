import json

class Resource():
    """
    base object for all Resources
    """
    def __len__(self):
        """
        """
        return len(self.data)

    def __setattr__(self, name, value):
        """
        """
        self.data[name] = value

    def __getattr__(self, item):
        """
        tries to return members of the data dict
        """
        try:
            return self.data[item]
        except:
            pass
        return self.data[item[0].upper() + item[1:]]

    def __str__(self):
        return self.pretty()

    def serialize(self, obj):
        """
        """
        return obj.data

    def pretty(self, sort=False):
        """
        pretty print data dict
        """
        return json.dumps(self.data, indent=4, sort_keys=sort, default=self.serialize)
