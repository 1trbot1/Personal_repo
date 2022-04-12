#!/usr/bin/python3
from __main__ import sys, SshError, ssh_timeout
import paramiko
import socket
def ssh_exec(host, user, password = " ", p_key_file = " " ):
    ##########################################################################
    #SSH Connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password != " ":
        #Connect with password
        try:
            ssh.connect(hostname=host, username=user, password=password, timeout=ssh_timeout)
            tr = ssh.get_transport()
            tr.default_max_packet_size = 1000000000
            tr.default_window_size = 1000000000
            return ssh
        #Server unreachable error
        except socket.error:
            raise SshError("[ERROR]: Server unreachable.")
        #Authentication error
        except paramiko.ssh_exception.AuthenticationException:
            raise SshError("[ERROR]: Authentication faild.")
        except Exception as e:
            raise SshError(e)
    if p_key_file != " ":
        key = paramiko.RSAKey.from_private_key_file(p_key_file)
        #Connect with key
        try:
            ssh.connect(hostname=host, username=user, pkey=key, timeout=ssh_timeout)
            tr = ssh.get_transport()
            tr.default_max_packet_size = 1000000000
            tr.default_window_size = 1000000000
            return ssh
        #Server unreachable error
        except socket.error:
            raise SshError("[ERROR]: Server unreachable.")
        #Authentication error
        except paramiko.ssh_exception.AuthenticationException:
            raise SshError("[ERROR]: Authentication faild.")
        except Exception as e:
            raise SshError(e)
