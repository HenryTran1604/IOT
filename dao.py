import mysql.connector

class DAO:
    def __init__(self) -> None:
        self.db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database="car_parking"
        )
        self.cursor = self.db.cursor()
    def find_all_license_plates(self):
        stm = 'SELECT licensePlate FROM car'
        self.cursor.execute(stm)
        license_plates = [x[0] for x in self.cursor.fetchall()]
        return license_plates
    
    def find_car_by_license_plate(self, licensePlate):
        stm = 'SELECT * FROM car WHERE licensePlate = %s'
        self.cursor.execute(stm, (licensePlate, ))
        result = self.cursor.fetchall()
        return len(result) != 0

    def find_parking_by_license_plate_and_status(self, licensePlate, status):
        stm = 'SELECT * from parking where licensePlate = (%s) and status = (%s)'
        self.cursor.execute(stm, (licensePlate, status))
        result = self.cursor.fetchall()
        return len(result) != 0
    
    def add_parking(self, licensePlate, timeIn):
        stm = 'INSERT INTO parking(status, timeIn, licensePlate) VALUES(0, %s, %s)'
        self.cursor.execute(stm, (timeIn, licensePlate))
        self.db.commit()
        row = self.cursor.rowcount
        print(row)
        return row
    
    def update_parking(self, licensePlate, timeOut):
        print(timeOut)
        stm = f'UPDATE parking SET status = 1, timeOut="{timeOut}" WHERE licensePlate = "{licensePlate}" AND status = 0'
        self.cursor.execute(stm)
        self.db.commit()
        row = self.cursor.rowcount
        return row

dao = DAO()
print(dao.find_parking_by_license_plate_and_status('36A-88888', 1))