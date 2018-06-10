#!/bin/bash
set -e

if [ "$CUMULUS_MODE" == "INIT" ]
then
  # User's django code is mounted into /cumulus/django
  cd /cumulus/django

  django-admin startproject cumulus_web_app
else
  cd /cumulus
  cd django/cumulus_web_app

  python manage.py runserver 0.0.0.0:8080
fi
