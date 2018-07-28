from .base import *


class Shell(Base):

    @staticmethod
    def start_shell(service, shell):
        if service:
            subprocess.call(
                [DOCKER_COMPOSE, "exec", service[0], START_SHELL, shell])
        else:
            service = parse_services()["WEB_APP"]
            if(len(service) == 1):
                subprocess.call(
                    [DOCKER_COMPOSE, "exec", service[0], START_SHELL, shell])
            else:
                print(
                    "Shell command defaults to web_app, however no such service was found")

    def run(self):
        service = self.options['<service>']
        shell = self.options['--shell']
        if not shell or shell not in SHELLS:
            shell = current_shell()
        if not service:
            Shell.start_shell("", shell)
        elif (len(service) == 1):
            Shell.start_shell(service, shell)
        else:
            print("Shell command can only be specified for at most one service")
