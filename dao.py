import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database="car_parking"
)
cursor = mydb.cursor()
cursor.execute('SELECT licensePlate FROM car')
license_plates = [x[0] for x in cursor.fetchall()]
print(license_plates)