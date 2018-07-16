"""The init command."""

from .base import *
import yaml
import os
import sys


class Init(Base):

    @staticmethod
    def init_container(service, all_services):
        docker_compose_run_command = [
            DOCKER_COMPOSE, "run",
            "-e", "CUMULUS_SERVICES={}".format(",".join(all_services)),
            service, "INIT"
        ]
        with open(LOGFILE, 'a+') as log_file:
            log_time_string = '\n\n{0}\n'.format(datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
            log_file.write(log_time_string)
        with open(LOGFILE, 'a') as log_file:
            print ('Initializing {0}...'.format(service))
            return_code1 = subprocess.call(docker_compose_run_command, stdout=log_file, stderr=subprocess.STDOUT)
            return_code2 = subprocess.call([DOCKER_COMPOSE, "rm", "-f", service], stdout=log_file, stderr=subprocess.STDOUT)
            if not return_code1 and not return_code2:
                print ("{0} initialized! \nRun 'cumulus start <service>' to start the container".format(service))
            else:
                print ("Error initializing {0}. Check docker-compose-log.out for more details.".format(service))             

    def get_and_set_project(self, doc, clean):
        compose_tree = {}
        temp_name = None
        if(os.path.exists('docker-compose.yml') and os.stat('docker-compose.yml').st_size != 0):
            compose_tree = yaml.load(open('docker-compose.yml', 'r'))
            temp_name = compose_tree['x-project-name']

        if temp_name is not None:
            if(clean and self.options['--project-name'] is not None):
                project = self.options['--project-name']
            else:
                project = temp_name
        elif self.options['--project-name']:
            project = self.options['--project-name']
        else:
            project = os.getcwd().split(os.sep)[-1]
        doc['x-project-name'] = project
        return project

    @staticmethod
    def get_image_name(service):
        if service in HAS_CUMULUS_IMAGE:
            return '{docker_hub_repo}{image}'.format(
                docker_hub_repo=DOCKER_HUB,
                image=service
            )
        elif service in SUPPORTED_BUT_NO_CUMULUS_IMAGE:
            return SUPPORTED_BUT_NO_CUMULUS_IMAGE[service]
        else:
            return service

    @staticmethod
    def update_web_app(doc, service, working_dir):
        Init.update_supported(doc, service, working_dir)

    @staticmethod
    def update_database(doc, service, working_dir):
        Init.update_supported(doc, service, working_dir)
        if service == 'mysql':
            doc['services'][service]['environment'] = {
                'MYSQL_ALLOW_EMPTY_PASSWORD': 'yes'}

    @staticmethod
    def update_supported(doc, service, working_dir):
        doc['services'][service]['image'] = Init.get_image_name(service)

        doc['services'][service]['ports'] = ['{0}'.format(PORTS[service])]
        if service in WEB_APP or service in DATABASE:
            doc['services'][service]['volumes'] = [
                '{host_path}/{service_name}:/cumulus'.format(
                    host_path=working_dir,
                    service_name=service)
            ]
            doc['services'][service]['command'] = COMMANDS[service]

    @staticmethod
    def update_unsupported(doc, service, working_dir):
        print("Warning: service {0} is unsupported.".format(service))
        doc['services'][service]['image'] = service

    def init_docker_compose(self, working_dir, not_previously_created):
        doc = {
            'version': DOCKER_COMPOSE_VERSION,
            'services': {}
        }
        clean = self.options['--clean']
        project = self.get_and_set_project(doc, clean)
        hostname = "{0}.cumulus.com".format(project)
        self.already_started = []
        new_services = self.options['<service>']
        clean = self.options['--clean']
        for service in new_services:

            if(os.path.exists('./{}'.format(service)) and not clean and service not in not_previously_created):
                self.already_started.append(service)
                continue

            name = "{}_{}".format(project, service)

            doc['services'][service] = {
                'container_name': name,
            }
            if service in WEB_APP:
                Init.update_web_app(doc, service, working_dir)
            elif service in DATABASE:
                Init.update_database(doc, service, working_dir)
            elif service in SUPPORTED:
                Init.update_supported(doc, service, working_dir)
            else:
                Init.update_unsupported(doc, service, working_dir)

            service_env_vars = get_service_environment_vars(
                service, new_services)
            if service_env_vars:
                if 'environment' not in doc['services'][service]:
                    doc['services'][service]['environment'] = {}

                doc['services'][service]['environment'].update(
                    service_env_vars)

        # Load yml if exists and add to doc
        if(os.path.exists('docker-compose.yml') and os.stat('docker-compose.yml').st_size != 0):
            compose_tree = yaml.load(open('docker-compose.yml', 'r'))

            if not clean:
                for config_attribute in compose_tree:
                    if config_attribute not in doc:
                        doc[config_attribute] = compose_tree[config_attribute]
                    else:
                        if isinstance(compose_tree[config_attribute], dict):
                            for item in compose_tree[config_attribute]:
                                doc[config_attribute][item] = compose_tree[config_attribute][item]
                        else:
                            doc[config_attribute] = compose_tree[config_attribute]

        with open('docker-compose.yml', 'w') as outfile:
            yaml.dump(doc, outfile, default_flow_style=False)

    # Makes a directory for each service, in the working directory
    # These will be used by the service to store configuration that should
    # be exposed to the user

    def prepare_working_directory(self, working_dir):
        new_services = self.options['<service>']
        not_previously_created = []
        for service in new_services:
            if(service not in NEED_INIT):
                continue
            service_directory = '{}/{}'.format(working_dir, service)
            if not os.path.exists(service_directory):
                not_previously_created.append(service)
                os.makedirs(service_directory)
        return not_previously_created

    def run(self):
        working_dir = os.getcwd()

        not_previously_created = self.prepare_working_directory(working_dir)
        self.init_docker_compose(working_dir, not_previously_created)

        for service in self.options['<service>']:
            if service not in self.already_started and service in NEED_INIT:
                Init.init_container(service, self.options['<service>'])
