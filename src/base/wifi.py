import network
import socket
import time
import re
import config
import machine
import rp2

def wait_wlan(wlan):
    max_wait = 15
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        print("Failed setting up wifi, status: " + str(wlan.status()) + ", will restart in 5 seconds")
        time.sleep(5)
        machine.reset()

def setup_ap():
    rp2.country(config.WIFI_COUNTRY)
    wlan = network.WLAN(network.AP_IF)
    wlan.active(False)
    wlan.disconnect()
    wlan.config(essid=config.WIFI_SSID, password=config.WIFI_PASSWORD) 
    wlan.config(pm = 0xa11140)
    wlan.active(True)
    wait_wlan(wlan)
    
    print('set up access point:', config.WIFI_SSID, 'with ip = ', wlan.ifconfig()[0])
    return wlan

def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.disconnect()
    
    wlan.active(True)
    wlan.config(pm = 0xa11140)

    try:
        if config.IP_ADDRESS != None and config.NETMASK != None and config.ROUTER_IP != None:
            wlan.ifconfig((config.IP_ADDRESS, config.NETMASK, config.ROUTER_IP, config.ROUTER_IP))

        if config.WIFI_CHANNEL != None:
            wlan.config(channel = config.WIFI_CHANNEL)
    except Exception as e:
        print("wifi.connect_wlan() exception: " + str(e))
        pass
        
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    
    wait_wlan(wlan)
    
    print('connected to wifi:', config.WIFI_SSID, 'with ip = ', wlan.ifconfig()[0])
    return wlan

def run():
    wlan = connect_wlan() if not config.WIFI_AP_MODE else setup_ap()
    return wlan

