# Author: Joaquin Cisneros & Rodrigo Manriquez
# Date: October 2025

import serial
import threading
import time

# === CONFIGURE YOUR PORT AND BAUD RATE ===
ARDUINO_PORT = "COM3"   # change this to your Arduino port
BAUD_RATE = 9600

# === GLOBAL VARIABLES ===
ser = None
is_listo = threading.Event()
is_fresa_si = threading.Event()


def read_from_arduino():
    """Continuously read from Arduino and detect 'Listo' messages."""
    global is_listo
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    print(f"[Arduino] {line}")
                    if "Listo" in line:
                        is_listo.set()  # notify that Arduino is ready
                    elif "FresaSi" in line:
                        is_fresa_si.set()  # notify that fresa is ready
        
        
        except serial.SerialException:
            print("Lost connection to Arduino.")
            break
        except Exception as e:
            print(f"Error reading: {e}")
            break

def connect_arduino(port=ARDUINO_PORT, baud=BAUD_RATE):
    """Open serial connection and start background thread."""
    global ser
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # wait for Arduino et
    print(f"Connected to {port} at {baud} baud.")

    thread = threading.Thread(target=read_from_arduino, daemon=True)
    thread.start()


def send_one():
    """Send '1' to open the valve."""
    if ser and ser.is_open:
        ser.write(b"1\n")
        print("[PC] Sent: 1 (abrir válvula)")


def send_zero():
    """Send '0' to close the valve."""
    if ser and ser.is_open:
        ser.write(b"0\n")
        print("[PC] Sent: 0 (cerrar válvula)")


def wait_for_ready(timeout=None):
    """
    Wait until Arduino sends 'Listo' twice.
    Waits 3 seconds before starting to listen.
    """
    print("Waiting 3 seconds before reading for 'Listo'...")
    time.sleep(3)

    print("Waiting for 2 'Listo' signals from Arduino...")
    listo_count = 0
    start_time = time.time()

    while True:
        remaining = None
        if timeout:
            remaining = timeout - (time.time() - start_time)
            if remaining <= 0:
                print("Timeout waiting for 'Listo'")
                return False

        if is_listo.wait(timeout=remaining):
            listo_count += 1
            print(f"Received 'Listo' #{listo_count}")
            is_listo.clear()  # reset event for next detection
            if listo_count >= 3:
                print("Arduino responded twice with 'Listo'")
                return True
        else:
            print("Timeout waiting for 'Listo'")
            return False

def wait_for_fresa_si(timeout=None):
    """
    Wait until Arduino sends 'FresaSi'.
    Waits 3 seconds before starting to listen.
    """
    print("Waiting 3 seconds before reading for 'FresaSi'...")
    time.sleep(3)

    print("Waiting for 'FresaSi' signal from Arduino...")

    start_time = time.time()

    while True:
        remaining = None
        if timeout:
            remaining = timeout - (time.time() - start_time)
            if remaining <= 0:
                print("Timeout waiting for 'FresaSi'")
                return False

        if is_fresa_si.wait(timeout=remaining):
            print("Received 'FresaSi'")
            is_fresa_si.clear()  # reset event for next detection
            return True
        else:
            print("Timeout waiting for 'FresaSi'")
            return False

def close_connection():
    """Close the serial connection."""
    global ser
    if ser and ser.is_open:
        ser.close()
        print("Serial connection closed.")