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
            rails new ${CUMULUS_PROJECT_NAME} -d mysql
        else
            rails new ${CUMULUS_PROJECT_NAME}
        fi
    fi

else
    cd "/cumulus/rails/${CUMULUS_PROJECT_NAME}"
    bundle install
    exec "$@"
fi
