#!/bin/bash

if [ "$1" == "INIT" ]
then
    cd /cumulus

    if [ ! -d "rails" ]
    then
        mkdir rails
    fi

    if [ ! -d "rails/${CUMULUS_PROJECT_NAME}" ]
    then
        cd rails
        rails new ${CUMULUS_PROJECT_NAME}
        bundle install
    fi

else
    cd "/cumulus/rails/${CUMULUS_PROJECT_NAME}"
    bundle install
    exec "$@"
fi
