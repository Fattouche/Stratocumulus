"""The init command."""

from .base import *
import yaml
import os
import sys


class Init(Base):

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

    def update_web_app(self, doc, service, working_dir):
        self.update_supported(doc, service, working_dir)

    def update_database(self, doc, service, working_dir):
        self.update_supported(doc, service, working_dir)
        if service == 'mysql':
            doc['services'][service]['environment'] = {
                'MYSQL_RANDOM_ROOT_PASSWORD': 'yes'}

    def update_supported(self, doc, service, working_dir):
        doc['services'][service]['image'] = '{docker_hub_repo}{image}'.format(
            docker_hub_repo=DOCKER_HUB,
            image=service
        )
        doc['services'][service]['ports'] = ['{0}'.format(PORTS[service])]
        if service in WEB_APP or service in DATABASE:
            doc['services'][service]['volumes'] = [
                '{host_path}/{service_name}:/cumulus'.format(
                    host_path=working_dir,
                    service_name=service)
            ]
            doc['services'][service]['command'] = COMMANDS[service]

    def update_unsupported(self, doc, service, working_dir):
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
                self.update_web_app(doc, service, working_dir)
            elif service in DATABASE:
                self.update_database(doc, service, working_dir)
            elif service in SUPPORTED:
                self.update_supported(doc, service, working_dir)
            else:
                self.update_unsupported(doc, service, working_dir)

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
                init_container(service)
