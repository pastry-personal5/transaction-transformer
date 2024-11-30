#!/usr/bin/env bash

# This shell scripts is to run mariadb procedure "InsertMonthlySums."
# Please modify the command line below.
mysql -u your_user -pYourPassword -h your_host your_database -e "CALL InsertMonthlySums();"
