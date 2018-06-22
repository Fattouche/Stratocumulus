"""The init command."""

from .base import *
import yaml
import os
import sys


class Init(Base):
    def init_docker_compose(self, working_dir):
        doc = {
            'version': DOCKER_COMPOSE_VERSION,
            'services': {}
        }

        self.already_started = []
        new_services = self.options['<service>']
        clean = self.options['--clean']

        for service in new_services:
            if(os.path.exists('./{}'.format(service)) and not clean):
                continue

            doc['services'][service] = {
                'image': '{docker_hub_repo}/{image}'.format(
                                docker_hub_repo=DOCKER_HUB,
                                image=service
                ),
                'volumes': [
                    '{host_path}/{service_name}:/cumulus'.format(
                        host_path=working_dir,
                        service_name=service)
                ],
                'environment': {
                    'CUMULUS_MODE': 'START'
                }

            if service in WEB_APP:
                doc['services'][service]['ports'] = ['8080:8080']

            if service == 'mysql':
                doc['services'][service]['ports'] = ['3306']

                doc['services'][service] \
                    ['environment']['MYSQL_RANDOM_ROOT_PASSWORD'] = 'yes'

                doc['services'][service]['command'] = ['bash', 'cumulus-docker-entrypoint.sh']


        # Load yml if exists and add to doc
        if(os.path.exists('docker-compose.yml') and os.stat('docker-compose.yml').st_size != 0):
            compose_tree = yaml.load(open('docker-compose.yml', 'r'))

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

        for service in new_services:
            service_directory = '{}/{}'.format(working_dir, service)
            if not os.path.exists(service_directory):
                os.makedirs(service_directory)


    def run(self):
        working_dir = os.getcwd()

        self.prepare_working_directory(working_dir)
        self.init_docker_compose(working_dir)

        for service in self.options['<service>']:
            if service not in self.already_started:
                init_container(service)
