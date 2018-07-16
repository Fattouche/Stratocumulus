import sys
import subprocess
import os


def check_docker():
    try:
        with open(os.devnull, 'w') as devnull:
            raw = subprocess.check_output(
                ["docker", "info"], stderr=devnull)
    except subprocess.CalledProcessError as grepexc:
        print("Docker daemon must be started in order to use cumulus.")
        sys.exit()
