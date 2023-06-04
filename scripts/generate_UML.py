#!/usr/bin/python3
"""Generates UML diagrams for all the subfolders of the root folder of the project.

This script is a wrapper for the pyreverse command line tool. pyreverse is quite
limited with respect to output folder and package selection. This script
overcomes these limitations."
"""
import os
import argparse
import subprocess

if __name__ == "__main__":
    # configuration of the generation
    COMMAND_MASK = "pyreverse -o pdf -p {basename} {files}"
    EXCLUDE_DIRS = [
        "migrations",
        "scripts",
    ]
    EXCLUDE_FILES = [
        "manage.py",
    ]

    # parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory", help="the directory to generate the UML diagrams for"
    )
    parser.add_argument(
        "-o", "--output_dir", help="directory to save the generated files in"
    )
    args = parser.parse_args()

    # set the default values to command line arguments
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.getcwd()

    # generate the list of files to consider
    files_to_analyse = []

    cwd = os.getcwd()

    for dirpath, dirnames, filenames in os.walk(cwd):
        # check whether ignore this subdir
        parent_dir = dirpath.split("/")[-1]
        if parent_dir in EXCLUDE_DIRS:
            continue

        # check for each file if it is to exclude
        for filename in filenames:
            if filename[-3:] == ".py" and not filename in EXCLUDE_FILES:
                files_to_analyse.append(os.path.join(dirpath, filename))

    # group the files by folder
    groups_of_files = {}
    i = 0
    while i < len(files_to_analyse):
        # strip off filename
        current_dir = "/".join(files_to_analyse[i].split("/")[:-1])
        print(current_dir)

        # get a list of all files in this subfolder
        files_in_current_dir = [files_to_analyse[i]]
        while i + 1 < len(files_to_analyse) and files_to_analyse[i + 1].startswith(
            current_dir
        ):
            files_in_current_dir.append(files_to_analyse[i + 1])
            i = i + 1
        # no more files in this sub folder
        group_name = current_dir.split("/")[-1]
        groups_of_files[group_name] = files_in_current_dir

        i = i + 1

    # actually generate the diagrams
    for folder, files in groups_of_files.items():
        files = " ".join(files)
        CMD = COMMAND_MASK.format(basename=folder, files=files)
        subprocess.run(CMD.split(" "), cwd=output_dir)
