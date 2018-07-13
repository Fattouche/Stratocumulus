"""The logs command."""

from .base import *


class Logs(Base):

    def run(self):
        follow = self.options['-f']
        if not self.options['<service>']:
            display_logs("", follow)
        else:
            display_logs(self.options['<service>'], follow)
