import sys, os
import shutil
import ephem 

if sh.env.system.libs.ephem_version is not None:
    sh.env.system.libs.ephem_version( ephem.__version__ )


# lib/env/statistic.py

# Garbage
gc.collect()
if gc.garbage != []:
    sh.env.core.garbage(len(gc.garbage))
    logger.warning("Garbage: {} objects".format(len(gc.garbage)))
    logger.info("Garbage: {}".format(gc.garbage))
    del gc.garbage[:]

# Threads
sh.env.core.threads(threading.activeCount())

# Memory
statusfile = "/proc/{0}/status".format(os.getpid())
units = {'kB': 1024, 'mB': 1048576}
with open(statusfile, 'r') as f:
    data = f.read()
status = {}
for line in data.splitlines():
    key, sep, value = line.partition(':')
    status[key] = value.strip()
size, unit = status['VmRSS'].split(' ')
mem = round(int(size) * units[unit])
sh.env.core.memory(mem)

# Load
l1, l5, l15 = os.getloadavg()
sh.env.system.load(round(l5, 2))

# Diskusage
if sys.version_info > (3,3):
    pathname = os.path.dirname(sys.argv[0])        
    du = shutil.disk_usage( os.path.abspath(pathname))
    sh.env.system.diskfree( du.free ) 
    sh.env.system.disksize( du.total )
    sh.env.system.diskusage( du.used )
    sh.env.system.diskusagepercent( round(du.used / du.total * 100.0,2) )

if sh.moon:
    sh.env.location.moonlight(sh.moon.light())


