import gitpm, sys, os

try:
    import readline
except:
    pass  # readline not available


def main():
    gitpm.GitPM.run(os.getcwd(), sys.argv[1:])


if __name__ == "__main__":
    main()
