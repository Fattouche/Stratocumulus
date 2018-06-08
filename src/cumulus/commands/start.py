from .base import Base


class Start(Base):

    def run(self):
        for service in self.options['<service>']:
            Base.start_container(self.__class__.__name__, service)
