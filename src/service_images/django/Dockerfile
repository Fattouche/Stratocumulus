FROM python

MAINTAINER Stratocumulus

RUN pip install django

# Put webapp code in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

ENTRYPOINT [ "bash", "docker_entrypoint.sh" ]

