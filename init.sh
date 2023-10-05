#!/usr/bin/env bash
# Load geodata, create tables and upload the data from csv

cd `dirname $0`
if [ ! -f ./cities15000.txt ]; then
  curl -O https://download.geonames.org/export/dump/cities15000.zip
  unzip cities15000.zip
fi

export PGHOST=localhost
export PGUSER="${PGUSER:=postgres}"
export PGPASSWORD="${PGPASSWORD:=12345}"

createdb "${DB:=postman}"
psql "${DB:=postman}" < ./schema.sql
psql $DB -c "\copy geonames FROM 'cities15000.txt' with delimiter E'\t' null as ''"
psql "${DB:=postman}" < ./migration_01.sql
psql "${DB:=postman}" < ./migration_02.sql
psql "${DB:=postman}" < ./migration_03.sql
psql "${DB:=postman}" < ./migration_04.sql
psql "${db:=postman}" < ./migration_05.sql
