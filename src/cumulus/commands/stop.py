"""The stop command."""

from .base import *


class Stop(Base):

    @staticmethod
    def stop_containers():
        subprocess.call([DOCKER_COMPOSE, "stop"])

    def run(self):
        Stop.stop_containers()
