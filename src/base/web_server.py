import config
import machine
import re
import time
import uos
import ujson

from logger import Logger
from machine import Pin
from socket_listener import SocketListener

# Generic server with various helpers:
# 
# 1. POST /sys/upload/{filename}
#    - Writes body as content to the specified filename.
#    - Requires restart call to take effect.
#
# 2. GET /sys/read/{filename}
#    - read the specified filename
#
# 3. GET /sys/status
#    - get system status
#
# 4. POST /sys/restart
#    - trigger a restart request
#
# Any other request gets sent to client logic handler if available.
# 
class WebServer:
    def __init__(self, wlan):
        ip_address = wlan.ifconfig()[0]
        self.logger = Logger(config.UDP_IP, config.UDP_PORT, ip_address)
        self.listener = SocketListener(self.logger, config.PORT)

        self.logging_time = config.LOGGING_INTERVAL
        self.deadline = time.ticks_add(time.ticks_ms(), self.logging_time)

        try: 
            import derived_logic
            self.logic = derived_logic.MainLoop(self.logger)
            self.logger.set_status("WebServer.__init__()", "OK")
            self.logger.send("WebServer.__init__() OK")

        except Exception as e:
            self.logic = None
            self.logger.set_status("WebServer.__init__()", "Failed importing/creating derived_logic, exception: " +  str(e))
            self.logger.send("WebServer.__init__() Failed importing/creating derived_logic, exception: " +  str(e))

    def update(self):
        if time.ticks_diff(self.deadline, time.ticks_ms()) < 0:
            self.deadline = time.ticks_add(time.ticks_ms(), self.logging_time)
            self.logger.send("Logger.Update() " + self.getStatusString())
            
        if self.logic != None:
            try:
                self.logic.update()
            except Exception as e:
                self.logger.set_status("MainLoop.update() last exception: ", str(e))

        cl = self.listener.accept()
        if not cl:
            time.sleep_ms(100)
            return

        try:
            self.handleClient(cl)
            cl.close()
        except Exception as e:
            self.logger.set_status("WebServer.update() last exception: ", str(e))

            self.logger.send("WebServer.update() Exception handling: " + str(e))
            try:
                cl.sendall('HTTP/1.0 500 Internal Server Error\r\nContent-type: text/html\r\n\r\n')
                cl.sendall("Exception: " + str(e))
                cl.close()
            except Exception as e:
                pass

    def handleClient(self, cl):
        data = cl.recv(1024)

        if self.handleUpload(cl, data):
            return

        if self.handleSys(cl, data):
            return

        if self.logic != None and self.logic.handleClient(cl, data.decode('utf-8')):
            return
            
    def handleUpload(self, cl, data):
        m = re.search("POST /sys/upload/([^ ]*) HTTP/1.1", data.decode('utf-8'))

        if m is None:
            return

        fileName = m.group(1)

        m = re.search("[Cc]ontent-[Ll]ength: ([0-9]*)", data.decode('utf-8'))
        if m is None:
            return
        
        length = int(m.group(1))
        self.logger.send("WebServer.handleUpload() Rewriting: " + str(fileName) + ", size: " + str(length))

        f = open(fileName, "wb")
                    
        i = 0
        while data[i] != 13 or data[i+1] != 10 or data[i+2] != 13 or data[i+3] != 10:
            i = i + 1
                    
        i = i + 4
        fragment = data[i:len(data)]
                        
        length = length - len(fragment)
        f.write(fragment)
                    
        while data != None and length>0:
            data = cl.recv(1024)
            length = length - len(data)
            f.write(data)
                        
        f.close()

        response="HTTP/1.0 200 OK\r\n\r\n"
        cl.sendall(response)
        cl.close()

    def getStatus(self):
        data = {}
        try:
            data["status"] = self.logger.get_status()
        except Exception as e:
            data["status"] = "Exception: " + str(e)
        
        if self.logic != None:
            try:
                data["logic_status"] = self.logic.getStatus()
            except Exception as e:
                data["logic_status"] = "Exception: " + str(e)
        else:
            data["logic_status"] = "None"

        return data

    def getStatusString(self):
        return ujson.dumps(self.getStatus())
    
    def handleSys(self, cl, data):
        m = re.search("(GET|POST) /sys/([^ ]*) HTTP/1.1", data.decode('utf-8'))

        if m is None:
            return

        if m.group(1) == "GET" and m.group(2) == "status":
            self.logger.send("WebServer.handleSys() status")

            response="HTTP/1.0 200 OK\r\n\r\n" + self.getStatusString()
            cl.sendall(response)
        elif m.group(1) == "POST" and m.group(2) == "restart":
            self.logger.send("WebServer.handleSys() restart")
            
            response="HTTP/1.0 200 OK\r\n\r\n"
            cl.sendall(response)
            cl.close()
            #machine.soft_reset()

            time.sleep(5)
            machine.reset()
            
        elif m.group(1) == "GET" and m.group(2).startswith("read/"):
            fileName=m.group(2)[5:]

            self.logger.send("WebServer.handleSys() read: " + fileName)

            response="HTTP/1.0 200 OK\r\nContent-Length: " + str(uos.stat(fileName)[6]) + "\r\n\r\n"
            cl.sendall(response)
            with open(fileName, 'r') as f:
                data = f.read(1400)
                while data != None and len(data) > 0:
                    cl.sendall(data)
                    data = f.read(1400)
