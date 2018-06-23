from .base import *


class Start(Base):

    def run(self):
        if not self.options['<service>']:
            start_container("")
        else:
            for service in self.options['<service>']:
                start_container(service)
        notify_active_port()
        print("logs available using `cumulus logs [<service>] [-f]`")
