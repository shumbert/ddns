from flask import Flask

import datetime
import os
import re

app = Flask(__name__)
domain = '__domain__'
zone_file = '/etc/nsd/' + domain + '.zone'

def update_record(line, ip):
    m = re.match('(.+?)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
    prefix = m.group(1)
    return prefix + ip

def update_serial(line):
    m = re.match('( +)(\d{8})(\d{2})', line)
    prefix = m.group(1)
    date   = m.group(2)
    seq    = m.group(3)

    today = datetime.date.today().strftime('%Y%m%d')

    if date == today:
        seq = '%02d' % (int(seq) + 1)
        return prefix + today + seq
    else:
        return prefix + today + '01'

@app.route('/query/<host>')
def query(host):
    result = 'notfound'

    # Read the zone file
    with open(zone_file, 'r') as file:
        content = file.read()

    # Parse file content
    for line in content.splitlines():
        if re.match(host, line):
            m = re.match('.+?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            result = m.group(1)

    return result

@app.route('/update/<host>/<ip>', methods=['POST'])
def update(host, ip):
    # Read the zone file
    with open(zone_file, 'r') as file:
        old_content = file.read()
    
    # Parse and update file content
    new_content = ''
    for line in old_content.splitlines():
    
        if re.match(' +\d{10}', line):
            new_content += update_serial(line)
    
        elif re.match(host, line):
            new_content += update_record(line, ip)
    
        else:
            new_content += line
    
        new_content += '\n'
    
    # Write the updated zone file
    with open(zone_file, 'w') as file:
        file.write(new_content)

    # Reload NSD
    os.system('/usr/bin/sudo /usr/sbin/nsd-control reload &> /dev/null')
    os.system('/usr/bin/sudo /usr/sbin/nsd-control notify &> /dev/null')

    return 'OK'

if __name__ == "__main__":
    app.run()
