from .base import *
import yaml


class Start(Base):

    def run(self):
        if not self.options['<service>']:
            start_container("")
        else:
            for service in self.options['<service>']:
                start_container(service)
        port = active_port()
        if port == "":
            print("Error: no port exposed in web app")
        elif port == "none":
            print("No web app to be shown")
        else:
            print("app available at localhost:"+port)


def active_port():
    with open("docker-compose.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            for service in data['services']:
                if service in WEB_APP:
                    raw = data['services'][service]['ports'][0]
                    if not raw:
                        return ""
                    return raw.split(":")[0]
            return "none"
        except yaml.YAMLError as exc:
            print(exc)
