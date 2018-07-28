FROM python:3.6.5

RUN mkdir /service
WORKDIR /service

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Put webapp code in /service
COPY . /service
RUN ["chmod", "+x", "cumulus-docker-entrypoint.sh", "start_shell.sh", "wait-for-it.sh"]

ENTRYPOINT ["bash", "cumulus-docker-entrypoint.sh"]
