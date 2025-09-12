from microdot import Microdot, send_file
import asyncio
import time
from robotarm import shoulder_rotate_servo, shoulder_tilt_servo, \
                elbow_servo, reset


# Create Microdot web server object
app = Microdot()


# Web control interface
@app.get('/')
async def index(req):
    return send_file('/static/index.html')

# Other static files for web control interface
@app.get('/static/<path:path>')
async def static(req, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('/static/' + path)

# Get servo state endpoint
@app.get('/servo')
async def get_servo_handler(req):
    return {
        'shoulder_rotate': shoulder_rotate_servo.position,
        'shoulder_tilt': shoulder_tilt_servo.position,
        'elbow': elbow_servo.position
    }

# Post servo state endpoint
@app.post('/servo')
async def post_servo_handler(req):
    if req.json is not None:
        try:
            shoulder_rotate_servo.position = float(req.json['shoulder_rotate'])
        except:
            pass
        try:
            shoulder_tilt_servo.position = float(req.json['shoulder_tilt'])
        except:
            pass
        try:
            elbow_servo.position = float(req.json['elbow'])
        except:
            pass
    return {
        'shoulder_rotate': shoulder_rotate_servo.position,
        'shoulder_tilt': shoulder_tilt_servo.position,
        'elbow': elbow_servo.position
    }

@app.post('/reset')
async def reset_handler(req):
    reset()
    return "Reset..."

# Main code entry point async function
async def main():
    print ("Robot arm web interface listening...")
    # Run all asyncio tasks
    await asyncio.gather(
        app.start_server(port=80),
        shoulder_rotate_servo.run_task(0.025),
        shoulder_tilt_servo.run_task(0.025),
        elbow_servo.run_task(0.025)
    )

# Guard to allow import as module
if __name__ == "__main__":
    asyncio.run(main())

