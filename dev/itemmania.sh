#!/bin/sh
#

INDEX=0
CONF=/usr/local/smarthome/items/itemmania.conf

echo "[itemmania]" >> $CONF
while [ $INDEX -le 1000 ] ; do
    echo "  [[item$INDEX]]" >> $CONF
    echo "    type = num" >> $CONF
    echo "    visu = div" >> $CONF
    echo "    history = yes" >> $CONF
    INDEX=$(($INDEX+1))
done
