"""The stop command."""

from .base import *


class Kill(Base):

    @staticmethod
    def kill_containers():
        subprocess.call([DOCKER_COMPOSE, "down"])

    def run(self):
        Kill.kill_containers()
