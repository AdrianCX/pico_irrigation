import time
from machine import Pin

right_forward = Pin(18, Pin.OUT)
right_back = Pin(19, Pin.OUT)

left_forward = Pin(17, Pin.OUT)
left_back = Pin(16, Pin.OUT)

sleeppin = Pin(15, Pin.OUT)
sleeppin.value(0)

def left_close():
    left_forward.value(0)
    left_back.value(1)

def left_open():
    left_back.value(0)
    left_forward.value(1)

def right_close():
    right_forward.value(0)
    right_back.value(1)

def right_open():
    right_back.value(0)
    right_forward.value(1)

def execute():
    sleeppin.value(1)
    time.sleep_ms(200)
    sleeppin.value(0)

def open_all():
    right_open()
    left_open()
    execute()
    
def close_all():
    right_close()
    left_close()
    execute()
