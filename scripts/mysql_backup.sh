#!/bin/bash

# modify the following to suit your environment
export DB_BACKUP="/backup/mysql_backup"
export DB_USER="root"
export DB_PASSWD="********"

# title and version
echo ""
echo "mySQL_backup"
echo "----------------------"
echo "* Rotating backups..."
rm -rf $DB_BACKUP/04
mv $DB_BACKUP/03 $DB_BACKUP/04
mv $DB_BACKUP/02 $DB_BACKUP/03
mv $DB_BACKUP/01 $DB_BACKUP/02
mkdir $DB_BACKUP/01 

echo "* Creating new backup..."
mysqldump --user=$DB_USER --password=$DB_PASSWD --all-databases | bzip2 > $DB_BACKUP/01/mysql-`date +%Y-%m-%d`.bz2
echo "----------------------"
echo "Done"
exit 0
