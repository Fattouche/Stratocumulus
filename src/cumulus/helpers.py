import os
import yaml
import subprocess
from collections import defaultdict

DOCKER = "docker"

SHELLS = ["bash", "zsh", "sh"]

DATABASE = ["mysql"]
WEB_APP = ["django", "rails"]
OTHER_SUPPORTED = ["redis", "elasticsearch", "memcached"]
SUPPORTED = WEB_APP + DATABASE + OTHER_SUPPORTED
NEED_INIT = WEB_APP + DATABASE
HAS_CUMULUS_IMAGE = ["mysql", "django", "rails"]
SUPPORTED_BUT_NO_CUMULUS_IMAGE = {
    "redis": "redis", "elasticsearch": "docker.elastic.co/elasticsearch/elasticsearch:6.3.1", "memcached": "memcached"}


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


# Gets all the services from docker-compose.yml, organized into various
# categories
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
                elif service in OTHER_SUPPORTED:
                    service_map["OTHER_SUPPORTED"].append(service)
                else:
                    service_map["UNSUPPORTED"].append(service)

        except yaml.YAMLError as exc:
            print(exc)

    return service_map


# Gets any docker-compose environment variables that must be defined for a
# particular service
def get_service_environment_vars(service, all_services):
    environment_vars = {}

    if service.lower() == 'django':
        environment_vars['CUMULUS_PROJECT_NAME'] = get_project_name()

        wait_for_string = ''
        for other_service in all_services:
            if other_service in DATABASE:
                wait_for_string += other_service
                wait_for_string += ','

        if wait_for_string:
            # remove the last comma from the string
            environment_vars['CUMULUS_WAIT_FOR'] = wait_for_string[:-1]
    if service.lower() == 'mysql':
        # Need to do this due to the bug in the MySQL docker container
        # see https://github.com/docker-library/mysql/issues/448#issuecomment-403552073
        #
        # Once this is fixed, the database name could instead be written to the
        # user's MySQL config file during init
        # (Although, having it in the docker-compose.yml like it is now will
        # expose it to the user, which may be desirable)
        environment_vars['MYSQL_DATABASE'] = '{}_default'.format(
            get_project_name())
    
    if service.lower() == 'rails':
        environment_vars['CUMULUS_PROJECT_NAME'] = get_project_name()

    return environment_vars


# Gets the shell that the user is currently using
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
