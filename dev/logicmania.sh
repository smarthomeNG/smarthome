#!/bin/sh
#

VERSION=0

INDEX=0
CONF=/usr/local/smarthome/etc/logic.conf

while [ $INDEX -le 1000 ] ; do
    echo "[logicmania$INDEX]" >> $CONF
    echo "  filename = thread_test.py" >> $CONF
    echo "  cycle = 30" >> $CONF
    INDEX=$(($INDEX+1))
done
