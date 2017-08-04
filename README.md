# ddns
Super-basic dynamic DNS system for a zone file hosted by NSD server. Server side is a Flask application served by gunicorn behind a nginx reverse proxy. Client side is a shell script run via cron.

Stole the idea from [iMil](https://imil.net/blog/2017/02/20/20-lines-dynamic-DNS-system/) .

## Server side
### Customize files
Update the following files with your information, such as domain name, authentication credentials, ...:
- client/dns-update
- server/ddns
- server/ddns.py

### Install software
```
sudo apt install python3 python3-flask python3-pip nginx
sudo pip3 install gunicorn # debian gunicorn package is python 2.7
```

### Set up the application
```
sudo useradd -r ddns
sudo chown root:ddns /etc/nsd/__your_domain__.zone
sudo chmod 0660 /etc/nsd/__your_domain__.zone
sudo mkdir -p /opt/ddns
sudo cp server/ddns.py /opt/ddns && sudo chmod 0755 /opt/ddns/ddns.py
```

### Set up gunicorn to run via systemd
```
sudo cp server/gunicorn.service /etc/systemd/system/
sudo cp server/gunicorn.socket /etc/systemd/system/
sudo cp server/gunicorn.conf /etc/tmpfiles.d/
sudo systemd-tmpfiles --create
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.socket
```

### Set up sudo
Allow ddns user to run two nsd-control commands without password:
```
sudo EDITOR=vim visudo -f /etc/sudoers.d/ddns

Add the following line:
ddns ALL= (root) NOPASSWD:NOEXEC: /usr/sbin/nsd-control reload, /usr/sbin/nsd-control transfer
```

### Nginx configuration
Add a vhost for the DDNS application, proxy incoming traffic to gunicorn:
```
sudo cp server/ddns /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/ddns /etc/nginx/sites-enabled/ddns 
sudo systemctl reload nginx
```

## Client side
Copy the shell script wherever is convenient and add a cronjob:
```
sudo cp client/dns-update /wherever/is/convenient
{ crontab -l; echo '*/5 * * * * /wherever/is/convenient/dns-update > /dev/null 2>&1'; } | crontab -
```
