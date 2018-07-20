FROM ruby:2.5

RUN apt-get update -qq && apt-get install -y build-essential tzdata libpq-dev nodejs
RUN mkdir /service
WORKDIR /service

COPY ./Gemfile .
COPY ./Gemfile.lock .
RUN bundle install

COPY . /service

RUN ["chmod", "+x", "cumulus-rails-docker-entrypoint.sh"]

ENTRYPOINT ["bash", "cumulus-rails-docker-entrypoint.sh"]