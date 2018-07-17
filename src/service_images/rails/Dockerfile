FROM ruby:2.5

RUN apt-get update -qq && apt-get install -y build-essential tzdata
RUN mkdir /service
WORKDIR /service

COPY ./Gemfile .
COPY ./Gemfile.lock .
RUN bundle install

COPY . /service

ENTRYPOINT ["bash", "cumulus-rails-docker-entrypoint.sh"]