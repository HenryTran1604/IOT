from dao import DAO
import urllib
class Service:
    def __init__(self) -> None:
        self.dao = DAO()

    def check_parking_by_license_plate_and_status(self, licensePlate, status):
        return self.dao.find_parking_by_license_plate_and_status(licensePlate, status)
    
    def check_car_by_license_plate(self, licensePlate):
        return self.dao.find_car_by_license_plate(licensePlate)
    
    def add_parking(self, licensePlate, timeIn):
        self.dao.add_parking(licensePlate, timeIn)
    
    def update_parking(self, licensePlate, timeOut):
        self.dao.update_parking(licensePlate, timeOut)
    
    def send_request(self, url):
        urllib.request.urlopen(url) # send request to ESP
