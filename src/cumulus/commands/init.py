"""The init command."""

from .base import *
import yaml
import os
import sys


class Init(Base):

    def init_docker_compose(self):
        doc = {
            'version': DOCKER_COMPOSE_VERSION,
            'services': {}
        }
        project = "example"
        hostname = "{0}.cumulus.com".format(project)
        self.already_started = []
        new_services = self.options['<service>']
        clean = self.options['--clean']
        for service in new_services:
            if(os.path.exists('./{0}'.format(service)) and not clean):
                self.already_started.append(service)
                continue
            name = "{0}_{1}".format(project, service)
            if service in WEB_APP:
                doc['services'][service] = {
                    # 'image': "{0}{1}".format(DOCKER_HUB, service),
                    'container_name': name,
                    'build': {'context': './service_images/django'},
                    'volumes': ['{0}:/cumulus'.format(os.getcwd())],
                    'ports': ['{0}:{1}'.format(PORTS[service], PORTS[service])],
                    'command': COMMANDS[service]}
            if service in DATABASE:
                doc['services'][service] = {
                    'container_name': name,
                    'image': service,
                    'ports': ['{0}:{1}'.format(PORTS[service], PORTS[service])]
                }

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

    def run(self):
        self.init_docker_compose()
        for service in self.options['<service>']:
            if service not in self.already_started:
                init_container(service)
