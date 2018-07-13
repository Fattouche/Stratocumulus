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
import yaml
import sys
import prerequisite
from collections import defaultdict

START_SHELL = "./start_shell.sh"
DOCKER_HUB = "strcum/"
DOCKER_COMPOSE = "docker-compose"
DOCKER = "docker"
ENTRYPOINT = "./docker_entrypoint.sh"
LOGFILE = "docker-compose-log.out"
VERSION = '1.0.0'
DATABASE = ["mysql"]
WEB_APP = ["django", "rails"]
SHELLS = ["bash", "zsh", "sh"]
MISC = ["redis", "elasticsearch", "memcached"]
NEED_INIT = WEB_APP+DATABASE
SUPPORTED = WEB_APP+DATABASE+MISC
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

# Gets project name from docker-compose.yml
# If it's not there, simply use the user's working directory as the project name
def get_project_name():
    compose_tree = {}
    project = ''

    if (os.path.exists('docker-compose.yml') and os.stat('docker-compose.yml').st_size != 0):
        compose_tree = yaml.load(open('docker-compose.yml', 'r'))
        if 'x-project-name' in compose_tree:
            project = compose_tree['x-project-name']
    
    if not project:
        project = os.getcwd().split(os.sep)[-1]

    return project


def get_service_start_params(service):
    service_start_params = []

    if service.lower() == 'django':
        # Need to do this due to the bug in the MySQL docker container
        # see https://github.com/docker-library/mysql/issues/448#issuecomment-403552073
        # 
        # Once this is fixed, the database name can instead be passed to MySQL
        # during init (possibly into the docker-compose file, if we want to 
        # expose it to the user), and written to the user's MySQL config file, which
        # Django will then read from (as set up in Django's settings.py)
        service_start_params.insert('-e')
        base = Init
        project_name = base.get_and_set_project(None, None)
        service_start_params.insert('MYSQL_DATABASE={}_default'.format(
            get_project_name()
        ))

def start_container(service):
    service_map = parse_services()

    docker_compose_call = [DOCKER_COMPOSE, "up", "-d"]

    docker_compose_call.insert('-e')
    cumulus_mode_string = 'CUMULUS_SERVICES='
    for other_service in service_map.values():
        cumulus_mode_string += other_service
        cumulus_mode_string += ','
    docker_compose_call.insert(cumulus_mode_string)

        
    if service:
        docker_compose_call += get_service_start_params(service)
        docker_compose_call.insert(service)
        subprocess.call(docker_compose_call)
    else:
        for service in service_map.values():
            docker_compose_call += get_service_start_params(service)
        subprocess.call(docker_compose_call)


def stop_container():
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
    service_map = defaultdict(list)
    with open("docker-compose.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            services = data['services']
            for service in services:
                if service in WEB_APP:
                    service_map["WEB_APP"].append(service)
                elif service in DATABASE:
                    service_map["DATABASE"].append(service)
                elif service in SUPPORTED:
                    service_map["OTHER_SUPPORTED"].append(service)
                else:
                    service_map["UNSUPPORTED"].append(service)
                

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


if __name__ == "__main__":
    main()
