"""The stop command."""

from .base import *


class Stop(Base):

    def run(self):
        stop_container()
