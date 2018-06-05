"""The init command."""

from .base import Base
import yaml
import os


class Init(Base):

    def run(self):
        doc = {
            'version': Base.DOCKER_COMPOSE_VERSION,
            'services': {}
        }
        services = self.options['<service>']
        clean = self.options['--clean']
        for service in services:
            if(os.path.exists('./'+service)):
                continue
            if service in Base.WEB_APP:
                doc['services']['web_app'] = {
                    'image': "stratocumulus/"+service,
                    'volumes': [os.getcwd()+':/cumulus'],
                    'ports': ['80:80']
                }
            if service in Base.DATABASE:
                doc['services']['database'] = {
                    'image': service
                }

        with open('docker-compose.yml', 'w') as outfile:
            yaml.dump(doc, outfile, default_flow_style=False)
