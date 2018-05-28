FROM python

MAINTAINER Stratocumulus

# Install required packages

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y

# Put webapp code in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

ENTRYPOINT ["bash", "docker_entrypoint.sh"]
