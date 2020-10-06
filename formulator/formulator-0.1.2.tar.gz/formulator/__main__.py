## Standard Lib
import logging

##TTILS:
from .nodes import A, B

__all__ = []
 
def main():
    a = A(parent="Apar", edges=2, child="Node D")  # , big_chungus=True
    print(vars(a))
    b = B(100, 24, "This is the payload")
    print(vars(b))
    # c=C()
    # print(help(B))
    
if __name__ == "__main__":
    logging.basicConfig(filename='./example.log',
                        level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p',
                        filemode='w')
    logging.getLogger('ttils').addHandler(logging.NullHandler())
    logging.logThreads = 0
    logging.logProcesses = 0
    logging._srcfile = None
    main()
