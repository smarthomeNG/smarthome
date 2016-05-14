#!/usr/bin/env python3
#

if trigger['value'] == 'init':
    h = random.randrange(2, 5)
    m = random.randrange(0, 59)
    sh.scheduler.change(logic.name, cron="{} {} * *".format(m, h))
    exit()

import hashlib
import urllib.parse

import lib.www

## check version
data = {}
try:
    data['up'] = int((sh.now() - sh.env.core.start()).total_seconds() / 86400)
    data['it'] = sh.item_count
    data['pl'] = len(sh._plugins._plugins)
    __ = sh.version.split('.')
    lmajor = int(__[0])
    lminor = int(__[1])
    lchange = int(__[2])
    data['ma'] = lmajor
    data['mi'] = lminor
    data['ch'] = lchange
    if len(__) == 4:
        data['br'] = __[3]
except:
    pass
try:
    with open('/sys/class/net/eth0/address', 'r') as f:
        __ = f.readline().strip()
        data['mc'] = hashlib.md5(__.encode()).hexdigest()
except:
    pass

#try:
#   body = urllib.parse.urlencode(data)
#   content = lib.www.Client().fetch_url("http://get.smarthomepy.de/version", method='POST', body=body, timeout=5)
#   if content:
#       rmajor, rminor, rchange = content.decode().split('.')
#       if int(rmajor) > lmajor or (int(rmajor) == lmajor and int(rminor) > lminor):
#           sh.env.core.upgrade(True)
#       elif int(rchange) > lchange:
#           sh.env.core.update(True)
#except:
#   pass
