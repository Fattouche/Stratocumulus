#!/bin/bash
cd /cumulus/django

if [ "$1" == "zsh" ]
then 
    echo "zsh is not installed, installing..."
    location="$(which zsh)"
    if [[ -z "$location" ]] 
    then
        apt-get update
        apt-get upgrade
        apt-get install zsh
    fi
    exec "zsh"

elif [ "$1" == "bash" ]
then
    exec "bash"
else
    exec "sh"
fi



