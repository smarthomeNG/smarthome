#!/bin/sh
#

VERSION=0

BASE=/var/www/visu
EX=/usr/local/smarthome/etc/manifest.exclude
MANIFEST="$BASE/smarthome.manifest"

echo "CACHE MANIFEST" > $MANIFEST
echo "CACHE:\r\n/" >> $MANIFEST
for FILE in $(find $BASE -type f | grep -v -f $EX | sort); do
    echo ${FILE#$BASE} >> $MANIFEST
done
