#!/bin/bash

containsElement() {
    local e match="$1"
    shift
    for e
    do 
        [[ "$e" == "$match" ]] && return 0
    done
    return 1
}

if [ "$1" == "INIT" ]
then
    # User's cumulus config and code is mounted into /cumulus
    cd /cumulus

    # Create folder for project's code, if one doesn't already exits
    if [ ! -d "rails" ]
    then
        mkdir rails
    fi

    # Only run if Rails project directory doesn't alredy exist 
    if [ ! -d "rails/${CUMULUS_PROJECT_NAME}" ]
    then
        cd rails
        containsElement "mysql" ${CUMULUS_PROJECT_NAME}
        if [ $? ]
        then
            rails new ${CUMULUS_PROJECT_NAME} -d mysql
        else
            rails new ${CUMULUS_PROJECT_NAME}
        fi
    fi

    for service in ${CUMULUS_SERVICES//,/ }
    do
        # Modify Rails database config file to connect to MySQL container
        if [ "${service}" == "mysql" ]
        then

            MYSQL_DATABASE="${CUMULUS_PROJECT_NAME}_default"
            ruby /service/modify-rails-database-config.ru ${MYSQL_DATABASE}
        fi
    done

else
    cd "/cumulus/rails/${CUMULUS_PROJECT_NAME}"
    bundle install

    for service in ${CUMULUS_WAIT_FOR//,/ }
    do
        if ["${service}" == "mysql" ]
        then
            bash /service/wait-for-it.sh mysql:3306 --timeout=300
        fi
    done
    
    exec "$@"
fi
