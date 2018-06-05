from .base import Base


class Start(Base):

    def run(self):
        print(self.options['<service>'][0])
        print('Starting')
