import sys

from geringoso import geringoso

def main():
    print(" ".join(geringoso(word) for word in sys.argv[1:]))

if __name__ == '__main__':
    main()
