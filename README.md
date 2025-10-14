# Protoflap

Controls the welcome room Vestaboard directly, bypassing their cloud.




## Setup

SSH into the Vestaboard using the root key, ie:

```
$ ssh -i ~/.ssh/vestaboard root@10.139.85.133
```

### Script

Clone the script:

```
# git clone https://github.com/Protospace/protoflap.git
```

Test it:

```
# cd protoflap/
# python protoflap.py
```

### Supervisor

To run the script automatically, install supervisor:

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
# supervisorctl status
```

