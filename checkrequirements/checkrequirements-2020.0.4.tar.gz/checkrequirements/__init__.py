"""Check that your requirements.txt is up to date with the most recent package
versions
"""
from __future__ import annotations

import argparse
from metprint import LogType
import requirements
from requirements.requirement import Requirement
import requests
try:
	from metprint import LAZY_PRINT
except ModuleNotFoundError:
	LAZY_PRINT = None


def semver(version: str) -> list[str]:
	"""Convert a semver/ pythonver string to a list in the form major, minor,
	patch ...

	Args:
		version (str): The version to convert

	Returns:
		list[str]: A list in the form major, minor, patch ...
	"""
	return version.split(".")


def semPad(ver: list[str], length: int) -> list[str]:
	"""Pad a semver list to the required size. e.g. ["1", "0"] to ["1", "0", "0"]

	Args:
		ver (list[str]): the semver representation
		length (int): the new length

	Returns:
		list[str]: the new semver
	"""
	char = "0"
	if ver[-1] == "*":
		char = "*"
	return ver + [char] * (length - len(ver))


def partCmp(verA: str, verB: str) -> int:
	"""Compare parts of a semver

	Args:
		verA (str): lhs part to compare
		verB (str): rhs part to compare

	Returns:
		int: 0 if equal, 1 if verA > verB and -1 if verA < verB
	"""
	if verA == verB or verA == "*" or verB == "*":
		return 0
	if int(verA) > int(verB):
		return 1
	return -1


def _doSemCmp(semA: list[str], semB: list[str], sign: str) -> bool:
	"""compare two semvers of equal length. e.g. 1.1.1 and 2.2.2

	Args:
		semA (list[str]): lhs to compare
		semB (list[str]): rhs to compare
		sign (str): string sign. one of ==, ~=, <=, >=, <, >

	Raises:
		ValueError: if the sign is not one of the following. or the semvers
		have differing lengths

	Returns:
		bool: true if the comparison is met. e.g. 1.1.1, 2.2.2, <= -> True
	"""
	if len(semA) != len(semB):
		raise ValueError
	# Equal. e.g. 1.1.1 == 1.1.1
	if sign == "==":
		for index, _elem in enumerate(semA):
			if partCmp(semA[index], semB[index]) != 0:
				return False
		return True
	# Compatible. e.g. 1.1.2 ~= 1.1.1
	if sign == "~=":
		for index, _elem in enumerate(semA[:-1]):
			if partCmp(semA[index], semB[index]) != 0:
				return False
		if partCmp(semA[-1], semB[-1]) < 0:
			return False
		return True
	# Greater than or equal. e.g. 1.1.2 >= 1.1.1
	if sign == ">=":
		for index, _elem in enumerate(semA):
			if partCmp(semA[index], semB[index]) < 0:
				return False
		return True
	# Less than or equal. e.g. 1.1.1 <= 1.1.2
	if sign == "<=":
		for index, _elem in enumerate(semA):
			if partCmp(semA[index], semB[index]) > 0:
				return False
		return True
	# Greater than. e.g. 1.1.2 > 1.1.1
	if sign == ">":
		for index, _elem in enumerate(semA[:-1]):
			if partCmp(semA[index], semB[index]) < 0:
				return False
		if partCmp(semA[-1], semB[-1]) != 1:
			return False
		return True
	# Less than. e.g. 1.1.1 < 1.1.2
	if sign == "<":
		for index, _elem in enumerate(semA[:-1]):
			if partCmp(semA[index], semB[index]) > 0:
				return False
		if partCmp(semA[-1], semB[-1]) != -1:
			return False
		return True
	raise ValueError


def semCmp(versionA: str, versionB: str, sign: str) -> bool:
	"""compare two semvers of any length. e.g. 1.1 and 2.2.2

	Args:
		semA (list[str]): lhs to compare
		semB (list[str]): rhs to compare
		sign (str): string sign. one of ==, ~=, <=, >=, <, >

	Raises:
		ValueError: if the sign is not one of the following.

	Returns:
		bool: true if the comparison is met. e.g. 1.1.1, 2.2.2, <= -> True
	"""
	semA = semver(versionA)
	semB = semver(versionB)
	semLen = max(len(semA), len(semB))
	return _doSemCmp(semPad(semA, semLen), semPad(semB, semLen), sign)


def updateCompatible(req: Requirement) -> dict:
	"""Check if the most recent version of a python requirement is compatible
	with the current version

	Args:
		req (Requirement): the requirement object as parsed by requirements_parser

	Returns:
		dict: return a dict of the most recent version (ver) and
		is our requirement from requirements.txt or similar compatible
		with the new version per the version specifier (compatible)
	"""
	url = "https://pypi.org/pypi/" + req.name + "/json"
	request = requests.get(url)
	updateVer = request.json()["info"]["version"]
	for spec in req.specs:
		if not semCmp(updateVer, spec[1], spec[0]):
			return {"ver": updateVer, "compatible": False}
	return {"ver": updateVer, "compatible": True}


def checkRequirements(requirementsFile: str) -> dict:
	"""Check that your requirements.txt is up to date with the most recent package
	versions. Put in a function so dependants can use this function rather than
	reimplement it themselves

	Args:
		requirementsFile (str): file path to the requirements file

	Returns:
		dict: dictionary containing info on each requirement such as the name,
		specs (from requirements_parser), ver (most recent version), compatible
		(is our version compatible with ver)
	"""
	reqsDict = {}
	with open(requirementsFile, 'r') as requirementsTxt:
		for req in requirements.parse(requirementsTxt):
			reqsDict[
			req.name] = {"name": req.name, "specs": req.specs, **updateCompatible(req)}
	return reqsDict


def cli():
	""" cli entry point """
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--requirements-file", "-r", help="requirements file")
	args = parser.parse_args()
	reqsDict = checkRequirements(args.requirements_file
	if args.requirements_file else "requirements.txt")
	if len(reqsDict) == 0:
		_ = (print("/  WARN: No requirements") if LAZY_PRINT is None else LAZY_PRINT(
			"No requirements", LogType.WARNING))
	for req in reqsDict:
		name = reqsDict[req]["name"]
		if reqsDict[req]["compatible"]:
			_ = (print("+    OK: " + name) if LAZY_PRINT is None else LAZY_PRINT(
			name, LogType.SUCCESS))
		else:
			_ = (print("+ ERROR: " + name) if LAZY_PRINT is None else LAZY_PRINT(
			name, LogType.ERROR))
