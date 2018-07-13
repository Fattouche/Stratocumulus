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

    def init_docker_compose(self):
        doc = {
            'version': DOCKER_COMPOSE_VERSION,
            'services': {}
        }
        clean = self.options['--clean']
        project = self.get_and_set_project(doc, clean)
        hostname = "{0}.cumulus.com".format(project)
        self.already_started = []
        new_services = self.options['<service>']
        for service in new_services:
            if(os.path.exists('./{0}'.format(service)) and not clean):
                self.already_started.append(service)
                continue
            name = "{0}_{1}".format(project, service)
            if service in WEB_APP:
                doc['services'][service] = {
                    'image': "{0}{1}".format(DOCKER_HUB, service),
                    'container_name': name,
                    'volumes': ['{0}:/cumulus'.format(os.getcwd())],
                    'ports': ['{0}'.format(PORTS[service])],
                    'command': COMMANDS[service]}
            else:
                doc['services'][service] = {
                    'container_name': name,
                    'image': service,
                    'ports': ['{0}'.format(PORTS[service])]
                }

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

    def run(self):
        self.init_docker_compose()
        for service in self.options['<service>']:
            if service not in self.already_started and service in NEED_INIT:
                init_container(service)
