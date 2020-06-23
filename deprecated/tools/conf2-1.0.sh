#!/bin/sh
#

SCRIPT=$(basename $0)

for CONF in items/*.conf etc/*.conf; do
    if ! grep -q "$SCRIPT" "$CONF"; then
        sed -i.bak \
                -e '/crontab *=/s/ *| */ | /g' \
                -e '/dmx_ch\|knx_\|watch_item/s/, */ | /g' \
                -e '/tcp_acl\|udp_acl\|http_acl\|smarttv/s/, */ | /g' \
                -e "/\[\|filename/s/'//g" \
                -e '/sv_widget/s/" *, *"/" | "/g' \
                -e '/sv_widget/s/"//g' \
                -e "/tz *=/s/'//g" \
                -e "/host *=/s/'//g" \
                -e "/visu *=/s/visu *= *yes/visu_acl = rw/g" \
                -e "/history *=/s/history *=/sqlite =/g" \
                -e "/ip *=/s/'//g" \
                -e '/knx_dpt/s/4002/4.002/g' \
                -e '/knx_dpt/s/5001/5.001/g' \
                -e '/knx_dpt/s/16000/16/g' \
                -e '/knx_dpt/s/16001/16.001/g' \
                -e '/eval *=/s/"//g' $CONF
        echo "# $SCRIPT - marker to run conversion script only once" >> $CONF
    fi
done

for CONF in scenes/*; do
    if [ "${CONF##*.}" != "conf" ]; then
        mv $CONF $CONF.conf
    fi
done
