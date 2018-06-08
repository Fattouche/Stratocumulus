"""The init command."""

from .base import Base
import yaml
import os


class Init(Base):

    def init_docker_compose(self):
        doc = {
            'version': Base.DOCKER_COMPOSE_VERSION,
            'services': {}
        }
        services = self.options['<service>']
        clean = self.options['--clean']
        for service in services:
            if(os.path.exists('./'+service) and not clean):
                continue
            if service in Base.WEB_APP:
                doc['services'][service] = {
                    # 'image': Base.DOCKER_HUB + service,
                    'build': {'context': './service_images/django'},
                    'volumes': [os.getcwd()+':/cumulus'],
                    'ports': ['8080:8080']
                }
            if service in Base.DATABASE:
                doc['services'][service] = {
                    'image': service
                }

        with open('docker-compose.yml', 'w') as outfile:
            yaml.dump(doc, outfile, default_flow_style=False)

    def run(self):
        self.init_docker_compose()
        for service in self.options['<service>']:
            Base.start_container(self.__class__.__name__, service)
