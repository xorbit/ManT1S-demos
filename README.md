# ManT1S-demos
Example software for the ManT1S

This repo contains the following:

## Default firmware configuration files

### micropython_config
Default [MicroPython](https://micropython.org/) config currently used for
factory firmware. 

## Stand-alone examples

### Arduino_ETH_ManT1S
Example [Arduino](https://www.arduino.cc/en/software/) code similar to that
provided for other ESP32 network PHYs such as LAN8720.

### file_server
MicroPython example that turns the ManT1S into a simple "file server", with
script to test upload and download speed through the ManT1S-Bridge.

## PIR triggered light examples

Simple server and client examples using MicroPython that demonstrate how to
to implement a
[Sparkfun Qwiic PIR sensor](https://www.sparkfun.com/sparkfun-qwiic-pir-170ua-ekmc4607112k.html)
activated light using two node types: a
light node and a PIR sensor node.  Simply extend to more sensors by adding
PIR nodes.

### light_server_socket_http
MicroPython example to turn a light on for a period of time, triggered from
either a socket command channel or over HTTP API.

### pir_client_http
PIR client to turn on the light on the light server when movement is detected.
This client uses the light's HTTP API with synchronous call using `requests`
library.

### pir_client_http_async
PIR client to turn on the light on the light server when movement is detected.
This client uses the light's HTTP API with asynchronous call using `aiohttp`
library.  Because it's asynchronous, it's easy to add other tasks that run
"simultaneously" (cooperative multitasking).

### pir_client_socket
PIR client to turn on the light on the light server when movement is detected.
This client uses a simple asynchronous socket command channel.  Because it's
asynchronous, it's easy to add other tasks that run "simultaneously"
(cooperative multitasking).

## Robot arm examples

[Robot arm](https://www.amazon.com/dp/B0DYK6GG9J) controller demonstrated in
the [Crowd Supply campaign](https://www.crowdsupply.com/silicognition/mant1s)
video. These
examples demonstrate some more complex use cases.  The robot arm uses two
ManT1S nodes, one for the "arm" and one for the "claw".  The code shows
 how multiple tasks can execute in "parallel" with cooperative
multitasking using `asyncio`.  It also shows how to solve issues with
accessing multiple nodes from a single web UI using
[CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS). 

### mant1s-robotarm
The "arm" node controls shoulder rotation and tilt, and elbow tilt using
servos driven with smooth acceleration control, controlled through an
HTTP API.  The arm node also implements an HTML control UI that can control
the complete arm (both the "arm" and "claw" nodes) from a unified UI.

### mant1s-claw
The "claw" node controls the wrist tilt and rotation, and claw closure.
In addition, the claw controller can read two claw
[pressure sensors](https://www.amazon.com/dp/B0BLGT1F5F) and an
[Arducam](https://www.amazon.com/dp/B0BW4L21KS) to show a view from the
claw perspective.
The servos use smooth acceleration control, and are controlled through an
HTTP API.  HTTP APIs are also used to read the claw pressure sensors and
the Arducam image.  CORS is used to allow access to these resources
from the arm UI webpage.

