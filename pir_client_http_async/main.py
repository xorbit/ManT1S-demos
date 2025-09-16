from machine import Pin, I2C
import asyncio
import aiohttp
import time


# Detect debounce time in ms
DETECT_DEBOUNCE_TIME = 2000

# Light device address
light_device = 'mant1s-light'

# Qwiic connector I2C bus
i2c = I2C(0, scl=Pin(32), sda=Pin(33), freq=100000)

# Turn on light with async request
# Other task can run while this is ongoing
async def turn_light_on():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{light_device}/on') as response:
                pass
    except:
        print ("Sending light on command failed")

# PIR sensor monitor task
async def pir_monitor_task():
    time_detect = None
    while True:
        now = time.ticks_ms()
        try:
            detect = bool(i2c.readfrom_mem(18, 3, 1)[0] & 0x01)
        except:
            detect = False
        if detect:
            if time_detect is None or \
                    (time.ticks_diff(now, time_detect) > DETECT_DEBOUNCE_TIME):
                time_detect = now
                print ("Sending light on command")
                await turn_light_on()
        else:
            if time_detect is not None and \
                    (time.ticks_diff(now, time_detect) > DETECT_DEBOUNCE_TIME):
                time_detect = None
                print ("Sending one last light on command")
                await turn_light_on()
        await asyncio.sleep_ms(200)

# Run the PIR monitor task
asyncio.run(pir_monitor_task())

