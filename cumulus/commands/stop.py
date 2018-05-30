"""The stop command."""

from .base import Base


class Stop(Base):

    def run(self):
        print('Stopping')
