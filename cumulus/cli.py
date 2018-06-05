"""
cumulus
Usage:
  cumulus start (<service>... | (-a | --all))
  cumulus init (<service>...) [--clean]
  cumulus stop (<service>... | (-a | --all))
  cumulus restart (<service>... | (-a | --all)) [--clean]
  cumulus -h | --help
  cumulus --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
  -a --all                          Run all
Examples:
  cumulus start django 
  cumulus init django, mysql
  cumulus stop -a
  cumulus restart --all --clean
Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/fattouche/stratocumulus
"""


from inspect import getmembers, isclass

from docopt import docopt

from __init__ import __version__ as VERSION
import os


def main():
    """Main CLI entrypoint."""
    import commands

    if(not os.path.isfile('./cumulus.yml') or not os.path.isfile('./cumulus.yaml')):
        print("error: cumulus commands must be run inside directory containing a cumulus.yml file.")
        return

    options = docopt(__doc__, version=VERSION)
    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(commands, k) and v:
            module = getattr(commands, k)
            commands = getmembers(module, isclass)
            command = [command[1]
                       for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
            return
