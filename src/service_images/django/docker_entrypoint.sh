#!/bin/bash
if [[ $1 == "Init" ]]
then
  # User's cumulus config and code is mounted into /cumulus
  cd /cumulus
  mkdir django
  cd django 

  django-admin startproject cumulus_web_app
elif [[ $1 == "Start" ]]
then
  cd /cumulus
  cd django/cumulus_web_app

  python manage.py runserver 0.0.0.0:8080
fi
