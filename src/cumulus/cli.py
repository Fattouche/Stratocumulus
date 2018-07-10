"""
cumulus
Usage:
  cumulus start [<service>...]
  cumulus init (<service>...) [--clean]
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
import yaml
import sys
from datetime import datetime
from io import StringIO


START_SHELL = "./start_shell.sh"
DOCKER_HUB = "strcum/"
DOCKER_COMPOSE = "docker-compose"
DOCKER = "docker"
ENTRYPOINT = "./docker_entrypoint.sh"
LOGFILE = "docker-compose-log.out"
VERSION = '1.0.0'
DATABASE = ["mysql", "postgres"]
WEB_APP = ["django", "rails"]
SHELLS = ["bash", "zsh", "sh"]
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
            clean_logs()
            return
    exit(__doc__)


def start_container(service):
    if service:
        print ('Starting {0}...'.format(service))
        subprocess.call([DOCKER_COMPOSE, "up", "-d", service])#, stdout=log_file, stderr=subprocess.STDOUT)
        print ('{0} Started!'.format(service))
        #output, _ = subprocess.Popen([DOCKER_COMPOSE, "up", "-d", service], stdout=log_file, stderr=subprocess.STDOUT).communicate()
        #log_file.write(StringIO(output))
    else:
        subprocess.call([DOCKER_COMPOSE, "up", "-d"])


def stop_container():
    subprocess.call([DOCKER_COMPOSE, "down"])


def restart_container(service):
    if service:
        subprocess.call([DOCKER_COMPOSE, "restart", service])
    else:
        subprocess.call([DOCKER_COMPOSE, "restart"])


def init_container(service):
    log_time_string = '\n\n{0}\n'.format(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
    with open(LOGFILE, 'a') as log_file:
        log_file.write(log_time_string)
        print ('Initializing {0}...'.format(service))
        subprocess.call([DOCKER_COMPOSE, "run", service, "INIT"], stdout=log_file, stderr=subprocess.STDOUT)
        subprocess.call([DOCKER_COMPOSE, "rm", "-f", service], stdout=log_file, stderr=subprocess.STDOUT)
        print ("{0} initialized! \nRun 'cumulus start <service>' to start the container".format(service))


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


def parse_services():
    service_map = {}
    with open("docker-compose.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            services = data['services']
            for service in services:
                if service in WEB_APP:
                    if "WEB_APP" not in service_map:
                        service_map["WEB_APP"] = []
                    service_map["WEB_APP"].append(service)
                if service in DATABASE:
                    if "DATABASE" not in service_map:
                        service_map["DATABASE"] = []
                    service_map["DATABASE"].append(service)
        except yaml.YAMLError as exc:
            print(exc)
    return service_map


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


def current_shell():
    raw = os.getenv("SHELL")
    if raw is None:
        print("Your current shell is unsupported, defaulting to sh. Please see documentation for supported shells.")
        shell = "sh"
        return shell
    shell = raw.split('/', 1)[-1]
    if shell not in SHELLS:
        print("Your current shell is unsupported, defaulting to sh. Please see documentation for supported shells.")
        shell = "sh"
    return shell

# Clean garbage (docker ansi color logs) out of log file
def clean_logs():
    with open(LOGFILE, 'r+') as log_file:
        lines = log_file.readlines()
        log_file.seek(0)
        for line in lines:
            if '\x1b' not in line:
                log_file.write(line)
        log_file.truncate()


if __name__ == "__main__":
    main()
