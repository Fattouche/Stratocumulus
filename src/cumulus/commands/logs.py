"""The logs command."""

from .base import *


class Logs(Base):

    @staticmethod
    def display_logs(service, follow):
        command = [DOCKER_COMPOSE, "logs"]
        if follow:
            command.append("-f")
        if service:
            command.extend(service)
        try:
            subprocess.call(command)
        except KeyboardInterrupt:  # Need to just return from the subprocess
            return

    def run(self):
        follow = self.options['-f']
        if not self.options['<service>']:
            Logs.display_logs("", follow)
        else:
            Logs.display_logs(self.options['<service>'], follow)
