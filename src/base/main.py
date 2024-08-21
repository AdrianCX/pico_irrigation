# System initialization for GPIO and other items. (example: make sure water is stopped)
import safety

# Other imports
import wifi
from web_server import WebServer

# Set up wifi
wlan = wifi.run()

# Run our server loop
server = WebServer(wlan)

while True:
    try:
        server.update()
    except Exception as e:
        pass