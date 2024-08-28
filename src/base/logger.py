import socket
import time
import ujson
import ntptime

try:
    from excprinter import get_callstack
except Exception as e:
    get_callstack = lambda e : []

class Logger:
    def __init__(self, ip, port, machine_id):
        try:
            self.machine_id = "[" + machine_id + "]"
            self.status = {}

            self.logging_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.logging_sock.connect(socket.getaddrinfo(ip, port)[0][-1])
        except Exception as e:
            self.set_status("Logger.__init__()", "failed setting up socket", e)

        try:
            ntptime.settime()
        except Exception as e:
            self.set_status("Logger.__init__()", "ntptime.settime()", e)

    def get_exception_info(self, e):
        return "exception: " + str(type(e)) + "(" + str(e) + "), callstack: " + str(get_callstack(e))

    def set_status(self, tag, status):
        self.status[str(tag)] = { self.get_time():status }

    def set_status(self, tag, status, e = None):
        if e == None:
            self.status[str(tag)] = self.get_time() + " " + status
        else:            
            self.status[str(tag)] = self.get_time() + " " + status + ", " + self.get_exception_info(e)

    def get_time(self):
        current_time = time.gmtime()
        return "{}/{:02d}/{:02d}_{:02d}:{:02d}:{:02d}".format(current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])
        
    def get_status(self):
        return self.status
    

    def send(self, message, e = None):
        try:
            if e == None:
                self.logging_sock.send(str(self.machine_id) + " " + self.get_time() + " " + message + "\n")
            else:
                self.logging_sock.send(str(self.machine_id) + " " + self.get_time() + " " + message + ", " + self.get_exception_info(e) + "\n")
        except Exception as e:
            self.set_status("Logger.send()", "network error", e)

    def send_status(self, tag, status, e = None):
        self.set_status(tag, status, e)
        self.send(tag + " " + status, e)
    