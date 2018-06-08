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
        new_services = self.options['<service>']
        clean = self.options['--clean']
        for service in new_services:
            if(os.path.exists('./'+service) and not clean):
                continue
            if service in WEB_APP:
                doc['services'][service] = {
                    'image': DOCKER_HUB + service,
                    'volumes': [os.getcwd()+':/cumulus'],
                    'ports': ['8080:8080']
                }
            if service in DATABASE:
                doc['services'][service] = {
                    'image': service
                }

        # Load yml if exists and add to doc
        if(os.path.exists('docker-compose.yml') and os.stat('docker-compose.yml').st_size != 0):
            compose_tree = yaml.load(open('docker-compose.yml', 'r'))
            existing_services = compose_tree['services']

            for service in existing_services:
                if service not in doc['services']:
                    doc['services'][service] = existing_services[service]

        with open('docker-compose.yml', 'w') as outfile:
            yaml.dump(doc, outfile, default_flow_style=False)

    def run(self):
        self.init_docker_compose()
        for service in self.options['<service>']:
            init_container(service)
