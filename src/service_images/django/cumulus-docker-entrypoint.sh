#!/bin/bash
DJANGO_PROJECT_NAME="cumulus_web_app"


if [ "$1" == "INIT" ]
then

  # User's cumulus config and code is mounted into /cumulus
  cd /cumulus

  if [ ! -d "django" ]
  then
    mkdir django
  fi

  # Only run if Django project folder doesn't already exist
  if [ ! -d "django/${DJANGO_PROJECT_NAME}" ]
  then
    cd django

    django-admin startproject ${DJANGO_PROJECT_NAME}
  fi

  # Perform any configuration necessary to communicate with neighbouring services
  for service in ${CUMULUS_SERVICES//,/ }  # iterate over comma-separated string
  do
    if [ "${service}" == "mysql" ]
    then
      cd /service
      python modify-django-settings.py /cumulus/django/${DJANGO_PROJECT_NAME}/${DJANGO_PROJECT_NAME}/settings.py \
        --mysql-config-path /cumulus/mysql/my.cnf \
        --mysql-db ${MYSQL_DATABASE}
        
      bash wait-for-it.sh
    fi
  done

else
  cd /cumulus
  cd "django/${DJANGO_PROJECT_NAME}"

  # Wait for any services that we need to wait for
  for service in ${CUMULUS_SERVICES//,/ }
  do
    if [ "${service}" == "mysql" ]
    then        
      # Somehow this works with port 3306, even if the port on mysql on the
      # host is not 3306
      bash /service/wait-for-it.sh mysql:3306 --timeout=300
    fi
  done

  exec "$@"
fi
