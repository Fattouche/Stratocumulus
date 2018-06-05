FROM python

MAINTAINER Stratocumulus

RUN pip install django mysqlclient

# Put webapp code in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

EXPOSE 8080

ENTRYPOINT ["bash", "docker_entrypoint.sh"]
