#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os

def pip_install():
    subprocess.run([sys.executable, "-m", "pip", "install", "./super32utils", "./super32assembler", "./super32emu"])

def pyinstaller():
    _ = os.pathsep
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "-n", "super32emu", "--windowed",
        "-i", "./super32emu/super32emu/resources/logo_color.ico",
        "--add-data", f"./super32emu/super32emu/instructionset.json{_}super32emu",
        "--add-data", f"./super32emu/super32emu/resources{_}super32emu/resources",
        "--add-data", f"./examples{_}super32emu/examples",
        "./super32emu/runner.py"
        ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package script for super32 tools")
    parser.add_argument("-i", "--install", action="store_true", help="Install pip packages")
    parser.add_argument("-s", "--standalone", action="store_true", help="Create standalone executables")
    arguments = parser.parse_args()

    if arguments.install or arguments.standalone:
        pip_install()

    if arguments.standalone:
        pyinstaller()
