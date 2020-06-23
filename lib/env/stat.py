# System logic 'stat' of SmartHomeNG
#
# schedule is defined in lib.env.logic.yaml
#
import os
import sys
import shutil
import ephem
import psutil

if sh.env.system.libs.ephem_version is not None:
    sh.env.system.libs.ephem_version(ephem.__version__, logic.lname)


# lib/env/statistic.py

# Garbage
gc.collect()
if gc.garbage != []:
    sh.env.core.garbage(len(gc.garbage), logic.lname)
    logger.warning("Garbage: {} objects".format(len(gc.garbage)))
    logger.info("Garbage: {}".format(gc.garbage))
    del gc.garbage[:]

# Threads
sh.env.core.threads(threading.activeCount(), logic.lname)

# Scheduler: Worker threads
sh.env.core.scheduler.worker_threads(sh.scheduler.get_worker_count(), logic.lname)
sh.env.core.scheduler.idle_threads(sh.scheduler.get_idle_worker_count(), logic.lname)
sh.env.core.scheduler.worker_names(sh.scheduler.get_worker_names(), logic.lname)

# Memory
p = psutil.Process(os.getpid())
mem_info = p.memory_info()
mem = mem_info.rss
sh.env.core.memory(mem, logic.lname)

# System Memory
swap_info = psutil.swap_memory()
sh.env.system.swap(swap_info.used, logic.lname)
sysmem_info = psutil.virtual_memory()
sh.env.system.memory.used(sysmem_info.used, logic.lname)
sh.env.system.memory.percent(sysmem_info.percent, logic.lname)

# Load
l1, l5, l15 = os.getloadavg()
sh.env.system.load(round(l5, 2), logic.lname)

# Diskusage
if sys.version_info > (3, 3):
    #pathname = os.path.dirname(sys.argv[0])
    absolute_pathname = sh.get_basedir()
    #du = shutil.disk_usage(os.path.abspath(pathname))
    try:
        du = shutil.disk_usage(absolute_pathname)
        sh.env.system.diskfree(du.free, logic.lname)
        sh.env.system.disksize(du.total, logic.lname)
        sh.env.system.diskusage(du.used, logic.lname)
        sh.env.system.diskusagepercent(round(du.used / du.total * 100.0, 2), logic.lname)
    except:
        logger.error("Statistics could not be read using base directory {}".format(absolute_pathname))

if sh.moon:
    sh.env.location.moonlight(sh.moon.light(), logic.lname)


