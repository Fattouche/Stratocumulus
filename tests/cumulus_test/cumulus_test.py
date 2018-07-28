"""
cumulus_test
Usage:
  cumulus_test start [<service>...] [--latest]
  cumulus_test init (<service>...) [--clean] [--project-name=<project>]
  cumulus_test stop
  cumulus_test kill
  cumulus_test restart [<service>...]
  cumulus_test logs [<service>] [-f]
  cumulus_test shell [<service>] [--shell=<shell>]
  cumulus_test -h | --help
  cumulus_test --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
Examples:
  cumulus_test start
  cumulus_test start django
  cumulus_test init django, mysql
  cumulus_test stop
  cumulus_test kill
  cumulus_test restart --all --clean
  cumulus_test logs -f
  cumulus_test shell django --shell=zsh
Help:
  For bugs using this tool, please open an issue on the Github repository:
  https://github.com/fattouche/stratocumulus_test
"""

import sys
import os
from docopt import docopt
from inspect import getmembers, isclass


path = os.path.join(os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"), "cumulus")
sys.path.append(path)

import cli


def execute_test():
    options = docopt(__doc__)
    # Call the actual CLI
    cli.main(options)
    import test_commands
    for (k, v) in options.items():
        if hasattr(test_commands, k) and v:
            module = getattr(test_commands, k)
            commands = getmembers(module, isclass)
            command = [command[1]
                       for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
            return
