# Stratocumulus

Some notes:
- In this repo we'll have a folder for each service, which defines the dockerfile for that
service. The images created by these dockerfiles will be uploaded to a
Stratocumulus docker repository, and then the stratocumulus executable will
generate docker-compose files that pull images from that repository
- The docker-compose file will also run containers with some sort of "MODE"
environment variable, which can be passed as "init", "start" or other options.
The value of this variable will be available to the startup scripts that the
containers use as their entrypoint, and the scripts will behave differently
depending on what mode is passed in
- The docker-compose files will run the containers with the user's app directory
mounted into `/app` (with read and write access). This will allow the container
to create new config files on `init`, and use existing config files on `start`
