FROM ruby:2.5

RUN apt-get update -qq && apt-get install -y build-essential tzdata libpq-dev nodejs mysql-client default-libmysqlclient-dev
RUN mkdir /service
WORKDIR /service

COPY ./Gemfile .
COPY ./Gemfile.lock .
RUN bundle install

COPY . /service

RUN ["chmod", "+x", "cumulus-docker-entrypoint.sh"]

ENTRYPOINT ["bash", "cumulus-docker-entrypoint.sh"]