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
        print(license_plates)
        return license_plates

    def find_license_plate_by_name_and_status(self, licensePlate, status):
        stm = f'SELECT * from parking where licensePlate = "{licensePlate}" and status = {status}'
        self.cursor.execute(stm)
        result = self.cursor.fetchall()
        return len(result) != 0
    
    def add_parking(self, licensePlate, timeIn):
        stm = f'INSERT INTO parking(status, timeIn, licensePlate) VALUES(0, {timeIn}, {licensePlate})'
        self.cursor.execute(stm)
        row = self.cursor.rowcount
        return row
    
    def update_parking(self, licensePlate, timeOut):
        stm = f'UPDATE parking SET status = 1, timeOut={timeOut} WHERE licensePlate = {licensePlate}'
        self.cursor.execute(stm)
        row = self.cursor.rowcount
        return row

dao = DAO()
print(dao.find_license_plate_by_name_and_status('36A-88888', 1))