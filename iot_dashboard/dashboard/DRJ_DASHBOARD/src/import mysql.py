import mysql.connector
from mysql.connector import Error

# Database connection parameters
host = "10.25.15.228"   # Replace with your remote IP
port = 3306              # Default MySQL port
user = "strawberry"   # Replace with your MySQL username
password = "1234567890"  # Replace with your MySQL password
database = "strawberries"  # Replace with your database name

try:
    # Connect to the database
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

    if connection.is_connected():
        print("Connected to the database")

        cursor = connection.cursor(dictionary=True)  # dictionary=True gives column names
        cursor.execute("SELECT * FROM plant_images")  # Replace with your table

        rows = cursor.fetchall()
        print(f"Total rows fetched: {len(rows)}")

        # Print each row
        for row in rows:
            print(row)

except Error as e:
    print(f"Error connecting to MySQL: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed")
