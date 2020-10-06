import sys

__all__ = ['export']

def export(code):
    globals()[code.__name__] = code
    __all__.append(code.__name__)
    return code

@export
class MyFinder:
    def find_module(self, fullname, path):
        print(fullname, path)
        return None
    
    def install(self):
        try:
            import sys
            sys.meta_path.insert(0, MyFinder())
        except:
            sys.meta_path.insert(0, MyFinder())