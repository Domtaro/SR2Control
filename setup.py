#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
import os
import sys
import re
from pkg_resources import get_distribution
from cx_Freeze import setup, Executable

def get_version():
    try:
        directory = os.path.dirname(__file__)
    except NameError:
        directory = os.getcwd()
    path = os.path.join(directory, "version.txt")
    version_string = open(path).readline()
    match = re.match(r"\s*(?P<rel>(?P<ver>\d+\.\d+)(?P<verjp>\.\S+)*)\s*", version_string)
    # version = match.group("ver")
    # version_jp = match.group("verjp")
    release = match.group("rel")
    return release

def collect_dist_info(packages):
    """
    Recursively collects the path to the packages' dist-info.
    """
    if not isinstance(packages, list):
        packages = [packages]
    dirs = []
    for pkg in packages:
        distrib = get_distribution(pkg)
        for req in distrib.requires():
            dirs.extend(collect_dist_info(req.key))
        dirs.append((distrib.egg_info, os.path.join('Lib', os.path.basename(distrib.egg_info))))
    return dirs

def grammar_modules():
    """
    Gets list of grammar modules (src_dir, dst_dir)
    """
    src_dst_dirs = []
    try:
        path = os.path.dirname(__file__)
    except NameError:
        path = os.getcwd()
    grammar_path = os.path.join(path, os.path.relpath("sr2ctrl/grammar/"))
    for filename in os.listdir(grammar_path):
        file_path = os.path.abspath(os.path.join(grammar_path, filename))
        # Only apply _*.py to files, not directories.
        is_file = os.path.isfile(file_path)
        if not is_file:
            continue
        # if is_file and not (os.path.basename(file_path).startswith("_") and
        #                     os.path.splitext(file_path)[1] == ".py"):
        if is_file and not (os.path.splitext(file_path)[1] == ".py"):
            continue
        src_dst = (file_path, 
                   os.path.join(os.path.relpath("sr2ctrl/grammar/"), os.path.basename(file_path))
            )
        src_dst_dirs.append(src_dst)
    return src_dst_dirs

include_files = []
include_files.extend(grammar_modules())
include_files.append("README.md")
include_files.append("LICENSE.txt")
include_files.append(("licenses/pkg_licenses_notices.txt", "licenses/pkg_licenses_notices.txt"))
include_files.append(("licenses/pkg_licenses_summary.md", "licenses/pkg_licenses_summary.md"))
include_files.append("launchers/_Start_KeyNameCheck.cmd")
include_files.append("launchers/_Start_RoN_Default.cmd")
include_files.append("launchers/_Start_RoN_Test.cmd")

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [],
    "include_files": include_files,
    "bin_path_excludes": "C:/Program Files/",
    "excludes": ["tkinter", 
                 "sqlite3",
                 "asyncio",
                 # "collections",
                 "concurrent",
                 "email",
                 # "encodings",
                 "html",
                 "http",
                 # "json",
                 # "lib2to3",
                 # "logging",
                 # "multiprocessing",
                 "pydoc_data",
                 # "pywin",
                 "pip-licenses",
                 "prettytable",
                 # "re",
                 "test",
                 "unittest",
                 # "urllib",
                 # "xml",
                 # "xmlrpc",
                 ],
    "include_msvcr": False,
}

setup(
    name="SR2Control",
    version=get_version(),
    description="Speech Recognition to Control tool",
    options={"build_exe": build_exe_options},
    executables=[Executable(script="cli.py", 
                            target_name="SR2Control", 
                            copyright="© Copyright 2024 by Domtaro"
                            )],
)
