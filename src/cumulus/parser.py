import yaml

CONFIG_PATH = '../../config.yml'

class Parser:

    def __init__(self, config=None):
        self.params = []
        if config:
            self.config_path = config 
        else:
             self.config_path = CONFIG_PATH
        
    def parse(self):
        with open(self.config_path, 'r') as cf:
            self.config = yaml.load(cf)

    def services(self):
        services = []
        for service, v in self.config['services'].items():
            services.append(service)
        return services


if __name__ == '__main__':
    parser = Parser()
    parser.parse()