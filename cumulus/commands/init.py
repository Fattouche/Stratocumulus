"""The init command."""

from .base import Base
import yaml
import os


class Init(Base):

    def run(self):
        doc = {
            'version': self.options['--version'],
            'services': {}
        }

        for service in self.options['<service>']:
            doc['services'] = {
                'name': service,
                'build': {'context': '.'},
                'volumes': [service+'-volume:'+os.getcwd()],
                'environment': {'CUMULUS_MODE': self.__class__.__name__}
            }
        with open('docker-compose.yml', 'w') as outfile:
            yaml.dump(doc, outfile, default_flow_style=False)
