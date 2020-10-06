def extract(self, **kwargs):
    return (
        f'i am {self.name}, anything can call me, '
        f'but I have a unique address: {self.nested_name()}, '
        'I also have a dag name depending on what the root node is: '
        f'{self.tree_name()}, because I was called by {self.caller}')

def transform(e: str, **kwargs):
    return e.upper()
