from flask import Flask, render_template, jsonify
import serial
import threading
import json
import time

app = Flask(__name__, static_folder="static", template_folder="templates")

# === Configuration ===
SERIAL_PORT = 'COM15'  # Change as needed (e.g., COM3, /dev/ttyUSB0)
BAUD_RATE = 9600
sensor_data = {}

# === Open Serial Port ===
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give time for Arduino to reset
    print(f"[INFO] Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Could not open serial port: {e}")
    ser = None

# === Background Serial Reader ===
def read_serial():
    global sensor_data
    if not ser:
        return
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                sensor_data = data
                print("Received:", data)
        except json.JSONDecodeError:
            print("⚠️  JSON decode error:", line)
        except Exception as e:
            print("⚠️  Serial read error:", e)

# Start serial reading thread
threading.Thread(target=read_serial, daemon=True).start()

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')  # Make sure templates/index.html exists

@app.route('/data')
def data():
    return jsonify(sensor_data)

# === Run Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
