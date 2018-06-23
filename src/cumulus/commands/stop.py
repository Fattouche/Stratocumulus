"""The stop command."""

from .base import *


class Stop(Base):

    def run(self):
        if not self.options['<service>']:
            stop_container("")
        else:
            for service in self.options['<service>']:
                stop_container(service)
