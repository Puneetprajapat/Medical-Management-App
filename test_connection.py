import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sarthak"
    )
    print("MySQL connection successful!")
    print("MySQL Server version:", connection.get_server_info())
    connection.close()
except Exception as e:
    print("Error connecting to MySQL:", str(e))