#!/bin/bash
set -e

# This should be called at the very end of the mysql docker-entrypoint.sh
# The docker-entrypoint.sh included in the mysql image will exec any input
# arguments automatically at the very end of the script, so to do this simply
# execute `docker-compose run mysql bash init-entrypoint.sh`

if [ "$CUMULUS_MODE" == "INIT" ]
then
  # Copy default config into the mounted drive
  cp -r /etc/mysql /cumulus/

  CUMULUS_MYSQL_CONFIG_FILE="/cumulus/mysql/conf.d/cumulus.cnf"

  # Check if the cumulus config file exists
  if [ ! -f "${CUMULUS_MYSQL_CONFIG_FILE}" ]; then
      touch ${CUMULUS_MYSQL_CONFIG_FILE}
      echo "[mysqld]" >> ${CUMULUS_MYSQL_CONFIG_FILE}
      # This is required for Django - I think the underlying reason is that the
      # mysql image uses mysql 8.0, which the mysqlclient python module doesn't support
      echo "default_authentication_plugin=mysql_native_password" >> ${CUMULUS_MYSQL_CONFIG_FILE}
  fi
else
  # Link the mysql config location to the mounted drive so that the mounted
  # drive is the source of truth (and users can modify the config on their host machine)
  rm -rf /etc/mysql
  ln -s /cumulus/mysql /etc/mysql
fi
