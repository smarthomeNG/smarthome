#!/usr/bin/env python3
#

if trigger['value'] == 'init':
    h = random.randrange(2, 5)
    m = random.randrange(0, 59)
    sh.scheduler.change(logic.name, cron="{} {} * *".format(m, h))
    exit()