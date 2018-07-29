#!/bin/bash

if [ "$1" == "INIT" ]
then
  # User's cumulus config and code is mounted into /cumulus
  cd /cumulus

  if [ ! -d "django" ]
  then
    mkdir django
  fi

  # Only run if Django project folder doesn't already exist
  if [ ! -d "django/${CUMULUS_PROJECT_NAME}" ]
  then
    cd django

    django-admin startproject ${CUMULUS_PROJECT_NAME}
  fi

  # Perform any configuration necessary to communicate with neighbouring services
  for service in ${CUMULUS_SERVICES//,/ }  # iterate over comma-separated string
  do
    if [ "${service}" == "mysql" ]
    then
      # Need to do this due to the bug in the MySQL docker container
      # see https://github.com/docker-library/mysql/issues/448#issuecomment-403552073
      # 
      # Once this is fixed, the database name can instead be passed to MySQL
      # during init (possibly into the docker-compose file, if we want to 
      # expose it to the user), and written to the user's MySQL config file, which
      # Django will then read from (as set up in Django's settings.py)
      MYSQL_DATABASE="${CUMULUS_PROJECT_NAME}_default"

      cd /service
      python modify-django-settings.py /cumulus/django/${CUMULUS_PROJECT_NAME}/${CUMULUS_PROJECT_NAME}/settings.py \
        --mysql-config-path /cumulus/mysql/my.cnf \
        --mysql-db ${MYSQL_DATABASE}
    fi

    if [ "${service}" == "memcached" ]
    then
      cd /cumulus/django/${CUMULUS_PROJECT_NAME}
      pip install python-memcached
      cd /service
      python modify-django-settings.py /cumulus/django/${CUMULUS_PROJECT_NAME}/${CUMULUS_PROJECT_NAME}/settings.py \
        --memcached
    
    fi

    if [ "${service}" == "elasticsearch" ]
    then
      cd /cumulus/django/${CUMULUS_PROJECT_NAME}
      pip intsall elasticsearch_dsl==6.1.0  #Due to issue https://github.com/sabricot/django-elasticsearch-dsl/issues/119
      pip install django-elasticsearch-dsl
      cd /service
      python modify-django-settings.py /cumulus/django/${CUMULUS_PROJECT_NAME}/${CUMULUS_PROJECT_NAME}/settings.py \
        --elastic-search
    
    fi

    if [ "${service}" == "redis" ]
    then
      cd /cumulus/django/${CUMULUS_PROJECT_NAME}
      pip install django-rq

      cd /service
      python modify-django-settings.py /cumulus/django/${CUMULUS_PROJECT_NAME}/${CUMULUS_PROJECT_NAME}/settings.py \
        --redis=/cumulus/django/${CUMULUS_PROJECT_NAME}/${CUMULUS_PROJECT_NAME}/urls.py
    
    fi


  done

else
  cd /cumulus
  cd "django/${CUMULUS_PROJECT_NAME}"

  # Wait for any services that we need to wait for
  for service in ${CUMULUS_WAIT_FOR//,/ }
  do
    if [ "${service}" == "mysql" ]
    then        
      # Somehow this works with port 3306, even if the port on mysql on the
      # host is not 3306
      bash /service/wait-for-it.sh mysql:3306 --timeout=300
    fi

    if [ "${service}" == "memcached" ]
    then        
      pip install python-memcached        #Just in case
      bash /service/wait-for-it.sh memcached:11211 --timeout=300
    fi

    if [ "${service}" == "elasticsearch" ]
    then        
      pip install django-elasticsearch-dsl        #Just in case
      bash /service/wait-for-it.sh elasticsearch:9200 --timeout=300
    fi

    if [ "${service}" == "redis" ]
    then        
      pip install django-rq        #Just in case
      bash /service/wait-for-it.sh redis:6379 --timeout=300
    fi
  done

  exec "$@"
fi
