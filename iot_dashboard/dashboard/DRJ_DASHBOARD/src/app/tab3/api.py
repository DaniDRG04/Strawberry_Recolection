from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Allow all devices in the network to access
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection parameters
host = "10.25.15.228"
port = 3306
user = "strawberry"
password = "1234567890"
database = "strawberries"

def get_connection():
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

@app.route("/alldata", methods=["GET"])
def get_all_data():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get all sensor data
        cursor.execute("SELECT date_time, temp_air, hum_air, hum_soil, light FROM sensor_data ORDER BY date_time ASC")
        all_sensor = cursor.fetchall()
        print(f"Fetched {len(all_sensor)} sensor records.")

        # Get all images
        cursor.execute("SELECT date_time, image_base64 FROM plant_images ORDER BY date_time ASC")
        all_images = cursor.fetchall()
        print(f"Fetched {len(all_images)} image records.")

        cursor.execute("SELECT date_time, error FROM error_logs ORDER BY date_time ASC")
        all_errors = cursor.fetchall()
        print(f"Fetched {len(all_errors)} error records.")

        return jsonify({
            "sensorData": all_sensor,
            "images": all_images,
            "errors": all_errors
        })

    except Error as e:
        return jsonify({"error": str(e)})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Run on all network interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
