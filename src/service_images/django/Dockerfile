FROM python:3.6.5

RUN mkdir /service
WORKDIR /service

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Put webapp code in /service
COPY . /service

ENTRYPOINT ["bash", "cumulus-docker-entrypoint.sh"]
