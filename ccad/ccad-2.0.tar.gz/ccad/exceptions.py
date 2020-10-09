#!/usr/bin/python
# coding: utf-8


class ChemCadError(Exception):

    pass


class IncompatibilityError(ChemCadError):

    pass


class ImpossibleAction(ChemCadError):

    pass


class ImpossibleConnection(ChemCadError):

    pass


class MissingConnector(ChemCadError):

    pass


class ConstraintError(ChemCadError):

    pass


if __name__ == "__main__":
    pass
