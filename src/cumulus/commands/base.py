"""The base command."""
from subprocess import call

DOCKER_HUB = "fattouche/stratocumulus_"
DOCKER_COMPOSE = "docker-compose"
ENTRYPOINT = "./docker_entrypoint.sh"


class Base(object):
    """A base command."""

    DATABASE = ["mysql", "postgres"]
    WEB_APP = ["django", "rails"]
    DOCKER_COMPOSE_VERSION = '3.6'

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError(
            'You must implement the run() method yourself!')

    def start_container(mode, service):
        call([DOCKER_COMPOSE, "build"])
        call([DOCKER_COMPOSE, "run", "--name", service+mode, service,
              ENTRYPOINT, mode])
