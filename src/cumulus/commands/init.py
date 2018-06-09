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
        self.already_started = []
        new_services = self.options['<service>']
        clean = self.options['--clean']
        for service in new_services:
            if(os.path.exists('./'+service) and not clean):
                self.already_started.append(service)
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

        #Load yml if exists and add to doc
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
                # Base.start_container(self.__class__.__name__, service)
