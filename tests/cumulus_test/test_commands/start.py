from .base import *
from shutil import copyfile
import subprocess

django_connection_test_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "django_connection_test.py")

src_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
django_manage_location = os.path.join(os.path.join(os.path.join(
    os.path.join(os.path.join(src_dir, "django")), "django"), "tests"), "manage.py")

path_to_files = {'django': django_manage_location}
file_replacements = {'django': django_connection_test_file}


class Start(Base):

    def run(self):
        services = self.options['<service>']
        if(not services):
            services = cli.parse_services()
        else:
            # Still doesn't work for some reason
            for service in services:
                if service in cli.WEB_APP:
                    if('WEB_APP' not in services):
                        services['WEB_APP'] = []
                    services['WEB_APP'].append(service)
                    # bad way to do it

        for service in services['WEB_APP']:
            copyfile(file_replacements[service], path_to_files[service])
            raw_command = cli.COMMANDS[service]
            command = raw_command.split(' ')
            p = subprocess.Popen(
                command, cwd=os.path.dirname(path_to_files[service]))
            p.wait()
