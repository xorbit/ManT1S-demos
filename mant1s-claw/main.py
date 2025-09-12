from microdot import Microdot, redirect
from microdot.cors import CORS
import asyncio
import time
from claw import cam, wrist_tilt_servo, wrist_rotate_servo, \
                claw_servo, claw_pressure_adc, reset


# Robot arm controller URL
ROBOT_ARM_URL = 'http://mant1s-robotarm'

# Create Microdot web server object
app = Microdot()
# Allow access from the robot arm web UI
CORS(app, allowed_origins=[ROBOT_ARM_URL])


# Redirect to robot arm where the web UI is implemented
@app.get('/')
async def index(req):
    return redirect(ROBOT_ARM_URL)

# Get servo state endpoint
@app.get('/servo')
async def get_servo_handler(req):
    return {
        'wrist_tilt': wrist_tilt_servo.position,
        'wrist_rotate': wrist_rotate_servo.position,
        'claw': claw_servo.position
    }

# Post servo state endpoint
@app.post('/servo')
async def post_servo_handler(req):
    if req.json is not None:
        try:
            wrist_tilt_servo.position = float(req.json['wrist_tilt'])
        except:
            pass
        try:
            wrist_rotate_servo.position = float(req.json['wrist_rotate'])
        except:
            pass
        try:
            claw_servo.position = float(req.json['claw'])
        except:
            pass
    return {
        'wrist_tilt': wrist_tilt_servo.position,
        'wrist_rotate': wrist_rotate_servo.position,
        'claw': claw_servo.position
    }

@app.get('/camera')
async def get_camera_image(req):
    cam.capture_jpg()
    return cam.get_JPG(), 200, {'Content-Type': 'image/jpeg'}

@app.post('/reset')
async def reset_handler(req):
    reset()
    return "Reset..."

# Main code entry point async function
async def main():
    print ("Claw web interface listening...")
    # Run all asyncio tasks
    await asyncio.gather(
        app.start_server(port=80),
        wrist_tilt_servo.run_task(0.025),
        wrist_rotate_servo.run_task(0.025),
        claw_servo.run_task(0.025)
    )

# Guard to allow import as module
if __name__ == "__main__":
    asyncio.run(main())

