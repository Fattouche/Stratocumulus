#!/bin/bash

# Copy default config into the mounted drive, and then link the mysql
# config location to the mounted drive so that the mounted drive is the source
# of truth (and users can modify the config on their host machine)
cp -r /etc/mysql /cumulus/
rm -r /etc/mysql
ln -s /cumulus/mysql /etc/mysql

CUMULUS_MYSQL_CONFIG_FILE="/cumulus/mysql/conf.d/cumulus.cnf"

# Check if the cumulus config file exists
if [ ! -f "${CUMULUS_MYSQL_CONFIG_FILE}" ]; then
    touch ${CUMULUS_MYSQL_CONFIG_FILE}
    echo "[mysqld]" >> ${CUMULUS_MYSQL_CONFIG_FILE}
    # This is required for Django - I think the underlying reason is that the
    # mysql image uses mysql 8.0, which the mysqlclient python module doesn't support
    echo "default_authentication_plugin=mysql_native_password" >> ${CUMULUS_MYSQL_CONFIG_FILE}
fi
