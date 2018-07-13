from .base import *


class Shell(Base):

    def run(self):
        service = self.options['<service>']
        shell = self.options['--shell']
        if not shell or shell not in SHELLS:
            shell = current_shell()
        if not service:
            start_shell("", shell)
        elif (len(service) == 1):
            start_shell(service, shell)
        else:
            print("Shell command can only be specified for at most one service")
