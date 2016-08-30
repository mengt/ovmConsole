#!/usr/bin/env python
#-*-coding:utf-8-*-
import os
txt_str = '#! /bin/bash\n# chkconfig: 2345 10 5\n# description: Starts the docke registry server\n#\n# Source function library.\n\n. /etc/init.d/functions\nPATH=/sbin:/bin:/usr/sbin:/usr/bin:$PATH\nRETVAL=0\nDREG=docker-registry\n\nstart(){\n\tif [ -f /var/lock/subsys/$DREG ]; then\n\t\techo "docker-registry is running"\n\telse\n\t\techo "docker-registry is starting"\n\t\tnohup gunicorn --access-logfile /var/log/docker-registry/access.log --error-logfile /var/log/docker-registry/server.log -k gevent --max-requests 100 --graceful-timeout 3600 -t 3600 -b 0.0.0.0:5000 -w 1 docker_registry.wsgi:application -p /var/run/docker-registry.pid 2>/dev/null &\n\t\ttouch /var/lock/subsys/docker-registry\n\t\tsleep 1\n\t\techo "docker-registry start OK."\n\tfi\n\t}\nstop(){\n\tif [ -f /var/lock/subsys/$DREG ];then\n\t\techo "Stopping docker-registry"\n  \t\tcat /var/run/docker-registry.pid | while read line;do kill -9 $line; done\n\t\trm -f /var/lock/subsys/docker-registry\n\t\trm -f /var/run/docker-registry.pid\n\t\tsleep 1\n\t\techo "docker-registry stop OK."\n\telse\n\t\techo "docker-registry is not running"\n\tfi\n\t}\nrestart(){\n\tstop\n\tstart\n\t}\ncase "$1" in\n\tstart)\n\t\tstart;;\n\tstop)\n\t\tstop;;\n\trestart)\n\t\trestart;;\n\t*)\n\techo $"Usage: ${DREG} {start|stop|restart}"\n\texit 1 ;;\nesac\nexit $RETVAL\n\n'
open_write = open('/etc/rc.d/init.d/docker-registry','w')
open_write.write(txt_str)
open_write.close()
os.system('chmod +x /etc/rc.d/init.d/docker-registry')



