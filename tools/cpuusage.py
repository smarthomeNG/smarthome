import psutil, sys, time, os, json

def clear():
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")

def get_threads_cpu_percent(p, interval=0.1):
   total_percent = p.cpu_percent(interval)
   total_time = sum(p.cpu_times())
   return [[total_percent * ((t.system_time + t.user_time)/total_time), t.id, psutil.Process(t.id).name()] for t in p.threads()]


def get_basedir():
    cwd = os.getcwd()
    path_split = cwd.split('/')
    if path_split[-1] == 'tools' or path_split[-1] == 'priv_tools':
        del path_split[-1]
    return '/'.join(path_split)


def get_pid():
    with open(os.path.join(base_dir, 'var', 'run', 'smarthome.pid')) as f:
        pid = f.read()
    return pid

def get_threadinfo():
    global print_info
    print_info = False

    threadinfo = {}
    threadinfo_list = []
    try:
        with open(os.path.join(base_dir, 'var', 'run', 'threadinfo.json')) as f:
            threadinfo_list = json.load(f )
    except:
        print_info = True

    for ti in threadinfo_list:
        threadinfo[ti['native_id']] = ti
    return threadinfo

base_dir = get_basedir()
shng_pid = get_pid()
threadinfo = get_threadinfo()

print()
print("Checking cpu usage for SmartHomeNG:")
print("- stored in directory: {}".format(base_dir))
print("- running process id : {}".format(shng_pid))
print("- number of threads .: {}".format(len(threadinfo)))
print()
if print_info == True:
    print("ATTENTION: To get thread names listed,\n           enable 'threadinfo_export' in ../etc/smarthome.yaml")
    print()

proc = psutil.Process(int(shng_pid))

initial_loop = True
while True:
    threadinfo = get_threadinfo()
    try:
        threads = get_threads_cpu_percent(proc)
        threads.sort(reverse=True)
        if initial_loop or threads[0][0] > 0.0:
            clear()
            print("SmartHomeNG in directory '{}'".format(base_dir))
            print("- process id = {}   ({} threads)".format(shng_pid, len(threads)))
            print()
            print("   Percent   PID     Thread Id      Thread Name")
            for line in threads:
                l = line
                thread = threadinfo.get(int(l[1]), {'id': '?', 'name':l[2]})
                if thread is not None:
                    thread_name = thread['name']
                    thread_id = thread['id']
                elif int(l[1]) == int(shng_pid):
                    thread_name = 'SmartHomeNG'
                    thread_id = '   __Main__    '
                else:
                    thread_name = '?'
                    thread_id = '       ?       '
                percent = float(l[0])
                pid = int(l[1])
                if not (thread_name.startswith( ('CP Server','HTTPServer', 'ThreadPoolExecutor') ) and percent <= 0.08):
                    if percent >= 0.0:
                        print("{p:10.6f}%{pid:6} {id} - {t:15}".format(p=percent, pid=pid, id=thread_id, t=thread_name))
                if thread_name.lower().startswith('python'):
                    print_info = True

        initial_loop = False
        time.sleep(2)

    except KeyboardInterrupt:
        if print_info == True:
            print()
            print("ATTENTION: To get thread names listed,\n           enable 'threadinfo_export' in ../etc/smarthome.yaml")
        print()
        exit(0)
    except Exception as e:
        print(f"Instance of SmartHomeNG terminated: {e}")
        shng_pid = get_pid()
        proc = psutil.Process(int(shng_pid))
        time.sleep(2)
    #exit()

#
#

def get_procfs_path():
    return sys.modules['psutil'].PROCFS_PATH
