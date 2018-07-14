FROM mysql:8.0.11

# Put service code (eg, entrypoint script) in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

ENTRYPOINT ["bash", "cumulus-docker-entrypoint.sh"]
