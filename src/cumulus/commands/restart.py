"""The restart command."""

from .base import *


class Restart(Base):

    def run(self):
        if not self.options['<service>']:
            restart_containers()
        else:
            for service in self.options['<service>']:
                restart_containers(service)
