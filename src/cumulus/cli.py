"""
cumulus
Usage:
  cumulus start [<service>...]
  cumulus init (<service>...) [--clean] [--project-name=<project>]
  cumulus stop
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
PORTS = {"django": "41000", "rails": "41001", "redis": "6379", "mysql": "3306"}
COMMANDS = {"django": "python manage.py runserver 0:{0}".format(PORTS["django"]),
            "rails": "rails server -b 0.0.0.0:{0}".format(PORTS["rails"]),
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


def start_containers(service=None):
    docker_compose_call = [DOCKER_COMPOSE, "up", "-d"]
        
    if service:
        docker_compose_call.append(service)

    subprocess.call(docker_compose_call)


def stop_containers():
    subprocess.call([DOCKER_COMPOSE, "down"])


def restart_containers(service=None):
    if service:
        subprocess.call([DOCKER_COMPOSE, "restart", service])
    else:
        subprocess.call([DOCKER_COMPOSE, "restart"])


def init_container(service, all_services):
    docker_compose_run_command = [
        DOCKER_COMPOSE, "run",
        "-e", "CUMULUS_SERVICES={}".format(",".join(all_services)),
        service, "INIT"
    ]

    subprocess.call(docker_compose_run_command)
    subprocess.call([DOCKER_COMPOSE, "rm", "-f", service])


def display_logs(service, follow):
    if service:
        command = [DOCKER_COMPOSE, "logs", service]
    else:
        command = [DOCKER_COMPOSE, "logs"]
    if follow:
        command.append("-f")
    try:
        subprocess.call(command)
    except KeyboardInterrupt:  # Need to just return from the subprocess
        return


def start_shell(service, shell):
    if service:
        subprocess.call([DOCKER_COMPOSE, "exec", service, START_SHELL, shell])
    else:
        service = parse_services()["WEB_APP"]
        if(len(service) == 1):
            subprocess.call(
                [DOCKER_COMPOSE, "exec", service[0], START_SHELL, shell])
        else:
            print("Shell command defaults to web_app, however no such service was found")

if __name__ == "__main__":
    main()
