"""Control the execution of program flow."""

import argparse

allowed_shapes: tuple = ("square", "triangle", "random")

parser = argparse.ArgumentParser(
    description="Accept command line arguments for making the boss happy"
)
