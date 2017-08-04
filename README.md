# ddns
Super-basic dynamic DNS system for a zone file hosted by NSD server. Server side is a Flask application served by gunicorn behind a nginx reverse proxy. Client side is a shell script run via cron.

## Server side
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
sudo cp ddns.py /opt/ddns && sudo chmod 0755 /opt/ddns/ddns.py
```

### Set up gunicorn to run via systemd
```
sudo cp gunicorn.service /etc/systemd/system/
sudo cp gunicorn.socket /etc/systemd/system/
sudo cp gunicorn.conf /etc/tmpfiles.d/
sudo systemd-tmpfiles --create
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.socket
```

### Set up sudo
Allow ddns user to run two nsd-control commands without password:
```
sudo EDITOR=vim visudo -f /etc/sudoers.d/ddns
ddns ALL= (root) NOPASSWD:NOEXEC: /usr/sbin/nsd-control reload, /usr/sbin/nsd-control transfer
```

## Client side
