import gitpm, sys, os

def main():
  gitpm.run(os.getcwd(), sys.argv[1:])
