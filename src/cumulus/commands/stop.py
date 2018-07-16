"""The stop command."""

from .base import *


class Stop(Base):

    @staticmethod
    def stop_containers(service=None):
        docker_compose_call = [DOCKER_COMPOSE, "stop"]
        if service:
            docker_compose_call.append(service)
        subprocess.call(docker_compose_call)

    def run(self):
        if not self.options['<service>']:
            Stop.stop_containers()
        else:
            for service in self.options['<service>']:
                Stop.stop_containers(service=service)

        