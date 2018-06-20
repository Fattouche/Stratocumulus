"""The restart command."""

from .base import Base


class Restart(Base):

    def run(self):
        if not self.options['<service>']:
            restart_container("")
        else:
            for service in self.options['<service>']:
                restart_container(service)
