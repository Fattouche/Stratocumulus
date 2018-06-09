FROM mysql

# Put service code (eg, entrypoint script) in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

# We want to use the mysql docker-entrypoint, so don't put an entrypoint here
# If an entrypoint is ommitted, the entrypoint of the base image will be used
