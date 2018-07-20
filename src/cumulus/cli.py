"""
cumulus
Usage:
  cumulus start [<service>...]
  cumulus init (<service>...) [--clean] [--project-name=<project>]
  cumulus stop
  cumulus kill
  cumulus restart [<service>...] [--clean]
  cumulus logs [<service>] [-f]
  cumulus shell [<service>] [--shell=<shell>]
  cumulus -h | --help
  cumulus --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
Examples:
  cumulus start
  cumulus start django
  cumulus init django, mysql
  cumulus stop
  cumulus kill
  cumulus restart --all --clean
  cumulus logs -f
  cumulus shell django --shell=zsh
Help:
  For bugs using this tool, please open an issue on the Github repository:
  https://github.com/fattouche/stratocumulus
"""

from inspect import getmembers, isclass
from docopt import docopt
import os
import subprocess
import prerequisite
from collections import defaultdict

from helpers import *

START_SHELL = "./start_shell.sh"
DOCKER_HUB = "strcum/"
DOCKER_COMPOSE = "docker-compose"
ENTRYPOINT = "./docker_entrypoint.sh"
LOGFILE = "docker-compose-log.out"
VERSION = '1.0.0'
PORTS = {"django": "41000", "rails": "41001",
         "redis": "6379", "mysql": "3306", "elasticsearch": "9200", "memcached": "11211"}
COMMANDS = {"django": "python manage.py runserver 0:{0}".format(PORTS["django"]),
            "rails": "rails server -p {0} -b 0.0.0.0".format(PORTS["rails"]),
            "mysql": "mysqld"}
DOCKER_COMPOSE_VERSION = '3.6'


def main():
    """Main CLI entrypoint."""
    import commands
    prerequisite.check_docker()
    options = docopt(__doc__, version=VERSION)
    for (k, v) in options.items():
        if hasattr(commands, k) and v:
            module = getattr(commands, k)
            commands = getmembers(module, isclass)
            command = [command[1]
                       for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
            return

    exit(__doc__)


if __name__ == "__main__":
    main()
