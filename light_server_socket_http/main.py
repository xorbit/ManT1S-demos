from socket_cc import CommChannel
from machine import Pin, reset
from microdot import Microdot
import asyncio
import time


# Light on time in ms
LIGHT_ON_TIME = 20000

# Globals to trigger light on and force it off
trigger_light = False
trigger_force_light_off = True

# Light control pin, default off
light_pin = Pin(20, Pin.OUT, value=0)

# Create comm channel
cc = CommChannel()

# Add comm channel handler for off command
@cc.add_handler('off')
async def off_handler(data):
    global trigger_force_light_off
    print ("Light off requested")
    trigger_force_light_off = True

# Add comm channel handler for on command
@cc.add_handler('on')
async def on_handler(data):
    global trigger_light
    print ("Light on requested")
    trigger_light = True

# Create Microdot web server object
app = Microdot()

# HTTP light status endpoint
@app.route('/')
async def root_handler(req):
    return f"Light is { ['off', 'on'][light_pin.value()] }"

# HTTP light off endpoint
@app.route('/off')
async def off_handler(req):
    global trigger_force_light_off
    print ("Light off requested over HTTP")
    trigger_force_light_off = True
    return "Light off requested"

# HTTP light on endpoint
@app.route('/on')
async def on_handler(req):
    global trigger_light
    print ("Light on requested over HTTP")
    trigger_light = True
    return "Light on requested"

# Light control task
# We have this task to manage keeping the light on for a minimum amount
# of time every time it is requested to be on (debounce) and then turn
# it off.
async def light_control_task():
    global trigger_light
    global trigger_force_light_off
    time_on = None
    while True:
        now = time.ticks_ms()
        if trigger_light:
            if time_on is None:
                print ("Light turned on")
                light_pin.value(1)
            time_on = now
            trigger_light = False
        elif trigger_force_light_off or (time_on is not None
                and time.ticks_diff(now, time_on) > LIGHT_ON_TIME):
            print ("Light turned off")
            light_pin.value(0)
            time_on = None
            trigger_force_light_off = False
        await asyncio.sleep_ms(100)

# Main code entry point async function
async def main():
    print ("Light controller listening on HTTP and socket control channel.")
    # Run all asyncio tasks
    await asyncio.gather(
        app.start_server(port=80),
        cc.listen(),
        light_control_task()
    )

# Guard to allow import as module
if __name__ == "__main__":
    asyncio.run(main())

