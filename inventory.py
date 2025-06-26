import csv
import os

from sale import SalesQueue

CSV_FILE = 'cars.csv'

class Car:
    def __init__(self, car_id, brand, model, year, price, longitude="", latitude="", image_path=""):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price
        self.longitude = longitude
        self.latitude = latitude
        self.image_path = image_path


class CarInventory:
    def __init__(self):
        self.cars = []

    def load_from_csv(self):
     self.cars.clear()  # Clear existing cars only once
     if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                car = Car(
                    row['Car ID'],
                    row['Brand'],
                    row['Model'],
                    row['Year'],
                    row['Price'],
                    row.get('Longitude', ""),  # Default to empty string if not found
                    row.get('Latitude', ""),   # Default to empty string if not found
                    row.get('Image Path', "")  # Default to empty string if not found
                )
                setattr(car, 'image_filename', row.get('Image Path', '').strip())
                self.cars.append(car)

            

    def save_all_to_csv(self):
     with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Car ID', 'Brand', 'Model', 'Year', 'Price', 'Longitude', 'Latitude', 'Image Path'])
        for car in self.cars:
            writer.writerow([
                car.car_id,
                car.brand,
                car.model,
                car.year,
                car.price,
                car.longitude,
                car.latitude,
                car.image_path
            ])


    def add_car(self, car):
        self.cars.append(car)
        self.save_all_to_csv()
    def update_car(self, car_id, brand, model, year, price, latitude, longitude, image_filename=None):
      for car in self.cars:
         if car.car_id == car_id:
            car.brand = brand
            car.model = model
            car.year = year
            car.price = price
            car.latitude = latitude
            car.longitude = longitude
            if image_filename:
                car.image_filename = image_filename
            self.save_all_to_csv()
            return True
      return False



    def get_all_cars(self):
        return self.cars

    def get_car_by_id(self, car_id):
        for car in self.cars:
            if car.car_id == car_id:
                return car
        return None

    def delete_car_by_id(self, car_id):
        self.cars = [car for car in self.cars if car.car_id != car_id]
        self.save_all_to_csv()

    def get_available_cars(self):
        """Return only cars that haven't been sold"""
        # Get all sold car IDs from sales records
        sold_car_ids = {sale.car_id for sale in self.sales_queue.get_all_sales()}
        
        # Return cars not in the sold list
        return [car for car in self.cars if car.car_id not in sold_car_ids]

    def remove_car(self, car_id):
        """Remove a car from inventory (when sold)"""
        self.cars = [car for car in self.cars if car.car_id != car_id]
        self.save_all_to_csv()