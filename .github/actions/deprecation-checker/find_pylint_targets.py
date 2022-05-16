"""
Find Python files on which to run the Context API checker.
"""
import argparse
import glob
import os
import sys
from typing import List

from setuptools import find_packages


def main(args: List[str]) -> None:
    """Print the top level Python packages to run pylint on."""
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_")
    parser.add_argument("out")
    parsed_args = parser.parse_args(args)

    python_packages = find_packages(where=os.path.relpath(parsed_args.dir_, "."))
    top_level_packages = [package for package in python_packages if "." not in package]
    top_level_python_files = glob.glob("*.py")
    with open(
        parsed_args.out, "w", encoding="utf-8"
    ) as fp:  # pylint: disable=invalid-name
        fp.write(" ".join((*top_level_python_files, *top_level_packages)))


if __name__ == "__main__":
    main(sys.argv[1:])
