import sys, os, signal, __main__, strings, platform, subprocess
from log import log

def get_pid(bin):
    """Get PID of an executable if running"""
    if platform.system() == "Darwin":
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()      
        for line in out.splitlines():       
            if bin in line:     
                return int(line.split(None, 1)[0])      
        return None        
    else:
        cmd = subprocess.Popen('pidof %s' % bin, shell=True, stdout=subprocess.PIPE).stdout.read()
        processes = cmd.strip().split()
        if not len(processes):
            return None
        return int(processes[0])

def kill_process(pid):
    log.info("--> attempting to kill process %s" % pid)
    try:
        pid = int(pid)
        os.kill(pid, signal.SIGKILL)
        killed_pid, stat = os.waitpid(pid, os.WNOHANG)
        if killedpid == 0:
            log.error("--> could not kill process %s" % pid)
            return False
    except (ValueError, OSError) as e:
        if e.args[0] == 3:
            log.info("--> no process was running with pid %s" % pid)
        else:
            log.error(log.exc(e))
        return True
    else:
        log.info("--> killed process %s" % pid)
        return True            

def secure_pid(run_folder):
    name = strings.prefix('.', os.path.basename(__main__.__file__))
    if name == "__main__":
        name = strings.suffix('/', os.path.dirname(__main__.__file__))
    log.info("Attempting to launch daemon %s..." % name)
    pid = str(os.getpid())
    if not os.path.isdir(run_folder):
        os.makedirs(run_folder)
    pidfile = os.path.join(run_folder, "%s.pid" % name)
    if os.path.isfile(pidfile):
        old_pid = open(pidfile).read()
        log.info("--> pidfile already exists for %s" % old_pid)
        kill_process(old_pid)
    open(pidfile, 'w').write(pid)    
    log.info("--> launched with pid %s" % pid)        

