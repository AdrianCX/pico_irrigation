import time
import irrigation
import config
import machine
import re
import ujson
from machine import Pin

class MainLoop:
    def __init__(self, logger):
        self.logger = logger

        self.message_limit = 4
        self.battery_level = machine.ADC(26)
        self.red_button = Pin(13, Pin.IN, Pin.PULL_UP)
        self.green_button = Pin(12, Pin.IN, Pin.PULL_UP)

        self.irrigation_on = False
        self.irrigation_shutoff = 0
        
        self.red_last=1
        self.red_count=0

        self.green_last=1
        self.green_count=0
        self.messages = []

        self.logger.send("MainLoop.__init__()")

    def getBatteryLevel(self):
        return self.battery_level.read_u16()
    
    def handleClient(self, cl, request):
        if self.handleStatus(cl, request):
            return
        
        if self.handleOpen(cl, request):
            return
        
        if self.handleClose(cl, request):
            return

    def getStatus(self):
        data = {}

        #unused currently
        #data["battery_level"] = self.getBatteryLevel()

        data["time"] = self.logger.get_time()
        
        if self.irrigation_on:
            data["irrigation"] = "on"
            data["time_left_ms"] = time.ticks_diff(self.irrigation_shutoff, time.ticks_ms())
        else:
            data["irrigation"] = "off"
            
        data["messages"] = self.messages
        return data

    def handleStatus(self, cl, request):
        m = re.search("GET /api/status", request)

        if m == None:
            return False

        self.logger.send("MainLoop.handleStatus()")
        
        response="HTTP/1.0 200 OK\r\n\r\n" + ujson.dumps(self.getStatus())
        cl.sendall(response)
            
        return True

    def addMessage(self, message):
        self.messages.append(self.logger.get_time() + " " + str(message))
        
        if len(self.messages) > self.message_limit:
            self.messages.pop(0)
    

    def handleClose(self, cl, request):
        m = re.search("GET /api/close", request)

        if m == None:
            return False

        self.logger.send("MainLoop.handleClose()")
        
        irrigation.close_all()
        cl.sendall("HTTP/1.0 200 OK\r\n\r\n")

        self.addMessage("irrigation off, web command")
        return True

    def handleOpen(self, cl, request):
        m = re.search("GET /api/open/([0-9]*)", request)

        if m == None:
            return False

        if m.group(1) == None:
            self.logger.send("MainLoop.handleOpen() failed to execute, operation requires duration")
            raise Exception("MainLoop.handleOpen() failed to execute, operation requires duration")

        duration=int(m.group(1))
        
        self.logger.send("MainLoop.handleOpen() Irrigation[on] web command, duration: " + str(m.group(1)))

        self.addMessage("irrigation on, web command, duration: " + str(duration))

        self.irrigation_shutoff = time.ticks_add(time.ticks_ms(), duration*1000)
        self.irrigation_on = True

        irrigation.open_all()
        cl.sendall("HTTP/1.0 200 OK\r\n\r\n")

        
        return True
            
    def update(self):
        if self.irrigation_on and time.ticks_diff(self.irrigation_shutoff, time.ticks_ms()) < 0:
            irrigation.close_all()
            self.irrigation_on = False

            self.addMessage("irrigation off, timer")
            self.logger.send("MainLoop.update() Irrigation[off] timer")
            
        # make sure at least 500ms press
        if self.red_button.value() == 0:
            self.red_count = self.red_count + 1
        else:
            self.red_count = 0
            self.red_last = 1

        if self.green_button.value() == 0:
            self.green_count = self.green_count + 1
        else:
            self.green_count = 0
            self.green_last = 1

        if self.red_count > 10 and self.red_last == 1:
            self.red_last = 0
            irrigation.close_all()
            self.addMessage("irrigation off, red button")
            self.logger.send("MainLoop.update() Irrigation[off] red button pressed")
            return

        if self.green_count > 10 and self.green_last == 1:
            self.green_last=0
            irrigation.open_all()
            self.addMessage("irrigation off, green button")
            self.logger.send("MainLoop.update() Irrigation[on] green button pressed")
            return
