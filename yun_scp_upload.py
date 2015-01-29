# -*- coding: utf-8 -*-
import scp
import sys
import paramiko
from scp import SCPClient
from paramiko import SSHClient
import time

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

server = 'IP OF YOUR YUN'
port = 22
user = 'USERNAME'
password = 'PASSWORD'
i = 1

hexFile = sys.argv[1] # Path to your HEX file

print(hexFile)
while True:
    print("Trying to connect to {0} ({1}/30)\n".format(server, i))

    try:
        ssh = createSSHClient(server, port, user, password)
        print("Connected to {0}\n".format(server))
        break
    except paramiko.AuthenticationException:
        print("Authentication failed when connecting to {0}\n".format(server))
        sys.exit(1)
    except:
        print("Could not SSH to {0}, waiting for it to start\n".format(server))
        i += 1
        time.sleep(2)

    # If we could not connect within time limit
    if i == 30:
        print("Could not connect to {0}. Giving up\n".format(server))
        sys.exit(1)


try:
    scp = SCPClient(ssh.get_transport())
    scp.put(hexFile, '/etc/arduino/temp.hex')
    print("File {0} uploaded\n".format(hexFile))
except:
    print("File could not be uploaded\n")

try:
    stdin, stdout, stderr = ssh.exec_command('cd /usr/bin; ./merge-sketch-with-bootloader.lua /etc/arduino/temp.hex')
    stdin, stdout, stderr = ssh.exec_command('run-avrdude /etc/arduino/temp.hex')
    # Wait for the command to terminate
    while not stdout.channel.exit_status_ready():
        for line in stdout.readlines():
            print (line)
        for line in stderr.readlines():
            print (line)

except:
    print("Could not run commands")

# Disconnect from the host
print("Command done, closing SSH connection")
ssh.close()
