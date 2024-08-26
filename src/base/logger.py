import socket
import time
import ujson
import ntptime

class Logger:
    def __init__(self, ip, port, machine_id):
        try:
            self.machine_id = "[" + machine_id + "]"
            self.status = {}

            self.logging_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.logging_sock.connect(socket.getaddrinfo(ip, port)[0][-1])
        except Exception as e:
            self.set_status("Logger.__init__()", "Exception: " + str(e))

        try:
            ntptime.settime()
        except Exception as e:
            self.set_status("Logger.__init__() ntptime.settime() ", "Exception: " + str(e))

    def set_status(self, tag, status):
        self.status[str(tag)] = { self.get_time():status }

    def get_time(self):
        current_time = time.gmtime()
        return "{}/{:02d}/{:02d}_{:02d}:{:02d}:{:02d}".format(current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])
        
    def get_status(self):
        return self.status
    
    def send(self, message):
        try:
            self.logging_sock.send(str(self.machine_id) + " " + self.get_time() + " " + message + "\n")
        except Exception as e:
            self.set_status("Logger.send()", "Exception: " + str(e))
