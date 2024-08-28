Simple raspberry pi pico irrigation controlled via HTTP.

![Alt text](/images/0_main.jpg "")

# 1. General notes:

a. More fun projects: https://pico.otilia.dev/

b. This is controlled via telegram. (a listener to web buttons then makes HTTP requests, will share the repository later, ping and I can speed it up if you're curious)

# 2. How it looks

## 2.1. Videos in action

- https://youtube.com/shorts/xUNLjCEPuNw
- https://youtube.com/shorts/3z41MsT0E34

## 2.2. Cover open and all pieces visible:
![Alt text](/images/1_open.jpg "")

## 2.3. Wires without without fiberglass sheathe:
![Alt text](/images/2_before_sheathe.jpg "")

## 2.4. USB cable connector
![Alt text](/images/3_usb_connector.jpg "")

# 3. Components used:


1. Raspberry pi pico
- https://www.kiwi-electronics.com/nl/raspberry-pi-pico-w-10938?search=raspberry%20pi%20pico

2. DRV8833
- https://www.tinytronics.nl/en/mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/drv8833-bipolar-stepper-motor-and-dc-motor-motor-controller

3. Large green and red plastic buttons at the bottom.

4. Any electric waterproof junction box - drill holes for buttons on bottom to avoid water ingress, use glands for wires.

- https://www.amazon.nl/dp/B0C7KSQK9Q?ref=ppx_yo2ov_dt_b_fed_asin_title

5. Black cable is a 10 meter 2 wire electric cable.

6. Hook up to a generic USB power supply via 2 polyfuses to avoid any issues with shorts (power supply also detects shorts but did not want to risk that)

- https://www.tinytronics.nl/en/components/fuses/self-restoring-fuse-pptc-polyfuse-2000ma-through-hole

7. Insulating sleeve for wires

- https://www.distrelec.biz/en/insulating-sleeve-4mm-red-brown-glass-fibre-silicone-bourgeois-pf03-062-08-316/p/15505268?pos=5&origPos=6&origPageSize=50&track=true&sid=q7s4sH6bkP&itemList=category

8. Time module (unused so far can ignore)

9. Solenoid valve

- https://www.tinytronics.nl/en/mechanics-and-actuators/solenoids/solenoid-valves/solenoid-valve-latching-5v-brass-g1-2

10. Water hammer arrestor. (IMPORTANT - you don't want to destroy pipes when switching via solenoid)

- Any should do based on preferrence: https://www.amazon.com/water-hammer-arrestor/s?k=water+hammer+arrestor
- The actual piece: https://www.obadis.com/en/caleffi-antishock-wasserschlagdampfer-525150-uberwurfmutter-3-4-ig-x-3-4-ag-messing-gehause-verchromt.html

11. 2-way valve water distributor

- https://www.amazon.nl/dp/B07T41LBGH

12. Rubber rings to have water tight seals:

- https://www.amazon.nl/dp/B097Q151ZN?ref=ppx_yo2ov_dt_b_fed_asin_title

13. Connectors

- https://www.amazon.nl/dp/B09FKBYY5X?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1

# 4. Software

You should copy over all files in "src/base/" and "src/derived" on the pico in "/" directory.
To get callstack when exceptions are reported you need a custom compiled micropython. https://github.com/AdrianCX/custom_micropython
It will work with official micropython, you just won't have full callstack.:

Logic is as follows:
1. src/base - common server components that can be reused for other projects
- board initialization - config, wifi, http listener.
- logger - send any logs from system over UDP to a remote host.
- upload/download APIs - so we can change files remotely if we want to add functionality or fix bugs
- status API - quick glance over system and any problematic exceptions

2. src/derived - irrigation system logic
- safety.py        - needed by "base" - item imported on boot - initialize environment (stop water flow for example)
- derived_logic.py - main logic for HTTP handling
- irrigation.py    - GPIO and utilities for handling solenoids

# 5. Debugging

Change config.ini UDP_IP/UDP_PORT to point to a machine where you can run netcat on and start up netcat:

```
root@kube:~# netcat -ukl 51001

227933 Logger.Update() Status: OK
235968 MainLoop.update() green button pressed
238100 MainLoop.update() red button pressed
238205 Logger.Update() Status: OK
247058 MainLoop.update() buttons 1 1, battery: 45259
248280 Logger.Update() Status: OK
250271 MainLoop.handleOpen() duration: 30
258313 Logger.Update() Status: OK
268392 Logger.Update() Status: OK
278471 Logger.Update() Status: OK
280505 MainLoop.update() Irrigation shut off due to timer
```

# 6. APIs available:

See "scripts/" folder for wrappers over each API.

a. GET /api/open/{timeSeconds}

Open up all pipes and keep them open for "timeSeconds"

b. GET /api/close

Close all pipes.

c. POST /sys/upload/{filename}

Write body to the given filename

d. GET /sys/read/{filename}

Read data from given filename

e. POST /sys/restart

Soft restart - useful after uploading files.

f. GET /sys/status

General system status


