"""The restart command."""

from .base import *


class Restart(Base):

    @staticmethod
    def restart_containers(service=None):
        if service:
            subprocess.call([DOCKER_COMPOSE, "restart", service])
        else:
            subprocess.call([DOCKER_COMPOSE, "restart"])

    def run(self):
        if not self.options['<service>']:
            Restart.restart_containers()
        else:
            for service in self.options['<service>']:
                Restart.restart_containers(service)
