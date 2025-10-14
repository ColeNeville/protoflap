# Protoflap

Controls the welcome room Vestaboard directly, bypassing their cloud.




## Setup


### Supervisor

Install supervisor:

```
# apt install supervisor
# touch /etc/supervisor/conf.d/protoflap.conf
# vim /etc/supervisor/conf.d/protoflap.conf
```

Set config to:

```
[program:protoflap]
user=root
directory=/root/protoflap
command=/usr/bin/python /root/protoflap/protoflap.py
stopsignal=INT
stopasgroup=true
killasgroup=true
autostart=true
autorestart=true
stderr_logfile=/var/log/protoflap.log
stderr_logfile_maxbytes=10MB
stdout_logfile=/var/log/protoflap.log
stdout_logfile_maxbytes=10MB
```

Load changes:

```
# supervisorctl reread; supervisorctl update
```

