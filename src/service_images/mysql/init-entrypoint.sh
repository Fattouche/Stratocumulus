#!/bin/bash

cp -r /etc/mysql /cumulus/
rm -r /etc/mysql
ln -s /cumulus/mysql /etc/mysql
