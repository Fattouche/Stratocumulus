#!/bin/bash
DJANGO_PROJECT_NAME="cumulus_web_app"


if [ "$CUMULUS_MODE" == "INIT" ]
then

  # User's cumulus config and code is mounted into /cumulus
  cd /cumulus

  # Only run if django folder doesn't already exist
  if [ ! -d "django" ]
  then
    mkdir django
    cd django

    django-admin startproject ${DJANGO_PROJECT_NAME}
  fi

  # Perform any configuration necessary to communicate with neighbouring services
  for service in ${CUMULUS_SERVICES//,/ }  # iterate over comma-separated string
  do
    if [ "${service}" == "mysql" ]
    then

    fi
  done

else
  cd /cumulus
  cd "django/${DJANGO_PROJECT_NAME}"

  python manage.py runserver 0.0.0.0:8080
fi
