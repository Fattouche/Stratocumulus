"""
cumulus
Usage:
  cumulus start [<service>...]
  cumulus init (<service>...) [--clean]
  cumulus stop [<service>...]
  cumulus restart [<service>...] [--clean]
  cumulus logs [<service>] [-f]
  cumulus -h | --help
  cumulus --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
Examples:
  cumulus start
  cumulus start django
  cumulus init django, mysql
  cumulus stop -a
  cumulus restart --all --clean
  cumulus logs -f
Help:
  For bugs using this tool, please open an issue on the Github repository:
  https://github.com/fattouche/stratocumulus
"""

from inspect import getmembers, isclass
from docopt import docopt
import os
import subprocess
import yaml
import sys


DOCKER_HUB = "strcum/"
DOCKER_COMPOSE = "docker-compose"
DOCKER = "docker"
ENTRYPOINT = "./docker_entrypoint.sh"
LOGFILE = "docker-compose-log.out"
VERSION = '1.0.0'
DATABASE = ["mysql", "postgres"]
WEB_APP = ["django", "rails"]
PORTS = {"django": "41000", "rails": "41001"}
COMMANDS = {"django": "python manage.py runserver 0:{0}".format(PORTS["django"]),
            "rails": "rails server -b 0.0.0.0:{0}".format(PORTS["rails"])}
DOCKER_COMPOSE_VERSION = '3.6'


def main():
    """Main CLI entrypoint."""
    import commands
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


def start_container(service):
    if service:
        subprocess.call([DOCKER_COMPOSE, "up", "-d", service])
    else:
        subprocess.call([DOCKER_COMPOSE, "up", "-d"])


def stop_container(service):
    if service:
        subprocess.call([DOCKER_COMPOSE, "down", service])
    else:
        subprocess.call([DOCKER_COMPOSE, "down"])


def restart_container(service):
    if service:
        subprocess.call([DOCKER_COMPOSE, "restart", service])
    else:
        subprocess.call([DOCKER_COMPOSE, "restart"])


def init_container(service):
    subprocess.call([DOCKER_COMPOSE, "run", service, "INIT"])
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


def notify_active_port():
    web_app_name = ""
    addresses = []
    with open("docker-compose.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            services = data['services']
            for service in services:
                if service.split('_', 1)[-1] in WEB_APP:
                    web_app_name = service
                    raw = subprocess.check_output([DOCKER, "port", services
                                                   [service]['container_name']])
                    mappings = raw.decode("utf-8").split("\n")
                    for mapping in mappings[:-1]:
                        port = mapping.split(":")[1]
                        addresses.append("localhost:{0}".format(port))
            if(len(addresses) == 0):
                if(web_app_name != ""):
                    print("{0} app unreachable, no exposed ports".format(
                        web_app_name))
                else:
                    print("No web app seen in project")
            elif(len(addresses) == 1):
                print("{0} app available at {1}".format(
                    web_app_name, addresses[0]))
            else:
                print("{0} app available at one of {1}".format(web_app_name,
                                                               ', '.join(addresses)))
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    main()
