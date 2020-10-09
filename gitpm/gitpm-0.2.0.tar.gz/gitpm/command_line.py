import gitpm, sys, os


def main():
    gitpm.GitPM.run(os.getcwd(), sys.argv[1:])


if __name__ == "__main__":
    main()
