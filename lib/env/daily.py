#!/usr/bin/env python3
#

_logicname_prefix = 'logics.'     # prefix for scheduler names

if trigger['value'] == 'init':
    h = random.randrange(2, 5)
    m = random.randrange(0, 59)
    sh.scheduler.change(_logicname_prefix+logic.name, cron=f"{m} {h} * *")
    exit()

