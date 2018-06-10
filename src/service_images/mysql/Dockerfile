FROM mysql

# Put service code (eg, entrypoint script) in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

# The mysql docker-entrypoint execs any input arguments at the very end of
# the script

# We want the mysql docker-entrypoint to run (since it does some critical
# mysql intialization), before running our docker-entrypoint

# So, don't put an entrypoint here - this will cause docker to use the base
# image entrypoint
