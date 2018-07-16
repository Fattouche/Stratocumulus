from .base import *


class Start(Base):

    @staticmethod
    def start_containers(service=None):
        docker_compose_call = [DOCKER_COMPOSE, "up", "-d"]
        if service:
            docker_compose_call.append(service)
        subprocess.call(docker_compose_call)

    def run(self):
        if not self.options['<service>']:
            Start.start_containers()
        else:
            for service in self.options['<service>']:
                Start.start_containers(service=service)
        notify_active_port()
        print("logs available using `cumulus logs [<service>] [-f]`")
