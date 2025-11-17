# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import time


# Code for serial port

SERIAL_PORT = 'COM3'  # Change to your Arduino port (COM3, COM4, etc. on Windows)
BAUD_RATE = 115200
def setup_serial():
    """Initialize serial connection to Arduino"""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        time.sleep(2)  # Wait for Arduino to reset after connection
        print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def send_command(ser, command):
    """Send a command to Arduino"""
    if ser and ser.is_open:
        ser.write(f"{command}\n".encode())
        ser.flush()
        return True
    return False

def read_response(ser):
    """Read response from Arduino"""
    if ser and ser.is_open and ser.in_waiting > 0:
        return ser.readline().decode().strip()
    
arduino = setup_serial()



# Backend code

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
CORS(app)

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route('/segmentdisplay', methods=['POST'])
def post_number():
    # Accept JSON {"value": <int>} or form field "value"
    data = request.get_json(silent=True) or {}
    value = data.get("value")
    if value is None:
        if "value" in request.form:
            try:
                value = int(request.form.get("value"))
            except (TypeError, ValueError):
                value = None
    # Validate
    if not isinstance(value, int):
        return jsonify(error="value must be an integer"), 400
    if not (0 <= value <= 99):
        return jsonify(error="value must be between 0 and 99"), 400
    
    # Execute
    print(f"Received number: {value}")
    send_command(arduino, str(value))
    
    return jsonify(ok=True, value=value), 200

@app.route('/led', methods=['POST'])
def post_led():
    # Accept JSON {"value": "RRRGGGBBB"} - 9-digit string
    data = request.get_json(silent=True) or {}
    value = data.get("value")
    
    # Validate
    if not isinstance(value, str):
        return jsonify(error="value must be a string"), 400
    if len(value) != 9 or not value.isdigit():
        return jsonify(error="value must be a 9-digit string (RRRGGGBBB)"), 400
    
    # Execute
    print(f"Received LED color: {value}")
    send_command(arduino, value)
    
    return jsonify(ok=True, value=value), 200

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()