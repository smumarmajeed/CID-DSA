class Car:
    def __init__(self, car_id, brand, model, year):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year

class CarInventory:
    def __init__(self):
        self.cars = []

    def add_car(self, car):
        self.cars.append(car)

    def get_all(self):
        return [vars(car) for car in self.cars]
