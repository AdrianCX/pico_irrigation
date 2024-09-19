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

Items below are listed for completeness and were used mostly because I already had them, there are simpler alternatives if starting from scratch.

## 3.1. Main black box:

Box: https://www.amazon.nl/-/en/Distributor-Waterproof-Surface-Mounted-Junction-Diameter/dp/B0BQBP43H2/

Logic:
- Raspberry pi pico w: https://www.digikey.nl/nl/products/detail/raspberry-pi/SC0918/16608263
- DRV8833: https://www.digikey.nl/nl/products/detail/adafruit-industries-llc/1311/6198255

goodies:
- 2x Separate headers (break off as needed): https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/male/40-pins-header-male-long
- perf board: https://www.digikey.nl/nl/products/detail/adafruit-industries-llc/1609/5353655
- 20x screw terminals: https://www.tinytronics.nl/en/cables-and-connectors/connectors/screw-terminals/2-pin-screw-terminal-block-connector-2.54mm-distance
- solid core wires: https://www.digikey.nl/nl/products/detail/adafruit-industries-llc/1311/6198255
- Green button: https://www.digikey.nl/nl/products/detail/adafruit-industries-llc/3487/7364334
- Red button: https://www.digikey.nl/nl/products/detail/adafruit-industries-llc/3489/7349495


## 3.2. Power supply/cable:

- Long cable to run 5V on, can use home electric cable, alternative: https://www.amazon.nl/-/en/CARLITS-2x0-8mm²-Extension-Electric-Lighting/dp/B08F7TS37H/
- 2 polyfuses to avoid shorts causing problems: https://www.tinytronics.nl/en/components/fuses/self-restoring-fuse-pptc-polyfuse-2000ma-through-hole
- A general purpose proto board: https://www.digikey.nl/nl/products/detail/digikey/DKS-SOLDERBREAD-02/15970925
- 2x screw terminals (already part of 1)
- USB power supply (should have at home)
- USB cable - cut one end and connect the 2 wires to the proto board screw terminal.

## 3.3. Solenoid valves and hookup:

- Solenoid valve: https://www.tinytronics.nl/en/mechanics-and-actuators/solenoids/solenoid-valves/solenoid-valve-latching-5v-brass-g1-2
- Shrink tubes to insude wire hookup: https://www.amazon.nl/-/en/Preciva-Electric-Assortment-Electrical-Insulation/dp/B0778D22WM/
- Insulating sleeve for wires: https://www.distrelec.biz/en/insulating-sleeve-6mm-red-brown-glass-fibre-silicone-bourgeois-pf03-062-08-321/p/15505284?pos=5&origPos=8&origPageSize=50&track=true&sid=Lso9yn9zyr&itemList=category
- Water hammer arrestor: https://www.obadis.com/en/caleffi-antishock-wasserschlagdampfer-525150-uberwurfmutter-3-4-ig-x-3-4-ag-messing-gehause-verchromt.html
- 2-way valve water distributor: https://www.amazon.nl/-/en/Manifold-Divider-Splitter-Connector-Separate/dp/B08XBPBCYF
- Rubber rings to have water tight seals (1/2"): https://www.amazon.nl/-/en/Prasacco-Shower-Sealing-Washers-Connection/dp/B0B9NGWQYR/
- Rubber rings to have water tight seals (3/4"): https://www.amazon.nl/-/en/Lvcky-Garden-Shower-Rings-Rubber/dp/B07GX8Z72J/
- Connectors (3/4" to 1/2"): https://www.amazon.nl/dp/B09FKBYY5X?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1
- Garden cable connectors on solenoid: https://www.amazon.nl/-/en/GARDENA-Premium-tap-connection-21mm/dp/B076WVH17N/
- (optional) Other side hooked up to pipes: https://www.amazon.nl/-/en/18215-20/dp/B00PNUC9K6/

Notes: 
- should use the solid core wires from 1 to extend wires from solenoids.
- Use the rubber rings on all connections to avoid water leaking
- Water hammer arrestor is IMPORTANT - you don't want to destroy pipes when switching via solenoid.


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


