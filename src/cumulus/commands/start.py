from .base import *


class Start(Base):

    @staticmethod
    def start_containers(service=None, latest=None):
        docker_compose_call = [DOCKER_COMPOSE, "up", "-d"]
        if(latest):
            subprocess.call([DOCKER_COMPOSE, "pull"])

        if service:
            docker_compose_call.append(service)
        subprocess.call(docker_compose_call)

    def run(self):
        latest = self.options['--latest']
        if not self.options['<service>']:
            Start.start_containers(latest=latest)
        else:
            for service in self.options['<service>']:
                Start.start_containers(service=service, latest=latest)
        notify_active_port()
        print("logs available using `cumulus logs [<service>] [-f]`")
