import socket
import time
import ujson

class Logger:
    def __init__(self, ip, port, machine_id):
        try:
            self.machine_id = machine_id
            self.status = {}

            self.logging_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.logging_sock.connect(socket.getaddrinfo(ip, port)[0][-1])
        except Exception as e:
            self.set_status("Logger.__init__()", "Exception: " + str(e))

    def set_status(self, tag, status):
        self.status[str(tag)] = status

    def get_status(self):
        return self.status
    
    def send(self, message):
        try:
            self.logging_sock.send(str(self.machine_id) + " " + str(time.ticks_ms()) + " " + message + "\n")
        except Exception as e:
            self.set_status("Logger.send()", "Exception: " + str(e))
