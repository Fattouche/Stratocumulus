"""The init command."""

from .base import *
import os
import sys


class Init(Base):

    def run(self):
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        services = self.options['<service>']
        for service in services:
            if(service in cli.NEED_INIT):
                directory_exists = os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))), service))
                if(not directory_exists):
                    print("Init test failed to find directory for {}".format(service))
                    return
        docker_compose_exists = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "docker-compose.yml"))
        if(not docker_compose_exists):
            print("Init test failed to find docker-compose.yml {}".format(service))
            return
        print("Init test passed!")
