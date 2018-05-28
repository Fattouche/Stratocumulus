#!/bin/bash

if [ $CUMULUS_MODE == "INIT" ]
then
  # User's cumulus config and code is mounted into /cumulus
  cd /cumulus
  mkdir django
  cd django

  # django-admin startproject cumulus_web_app
fi
