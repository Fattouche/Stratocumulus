FROM python

MAINTAINER Stratocumulus

# In future, may only want to install mysqlclient if mysql is being used
RUN pip install django mysqlclient

# Put webapp code in /service
RUN mkdir /service
COPY . /service
WORKDIR /service

EXPOSE 8080

ENTRYPOINT ["bash", "docker-entrypoint.sh"]
