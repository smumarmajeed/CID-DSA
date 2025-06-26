# sale.py

import csv
from collections import deque

class Sale:
    def __init__(self, car_id, dealer_id, owner_name, cnic, contact):
        self.car_id = car_id
        self.dealer_id = dealer_id
        self.owner_name = owner_name
        self.cnic = cnic
        self.contact = contact

class SalesQueue:
    def __init__(self):
        self.queue = deque()
        self.csv_file = 'sales.csv'
        self.load_from_csv()

    def enqueue_sale(self, sale):
        self.queue.append(sale)
        self.save_to_csv(sale)

    def save_to_csv(self, sale):
        file_exists = False
        try:
            with open(self.csv_file, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Car ID', 'Dealer ID', 'Owner Name', 'CNIC', 'Contact'])
            writer.writerow([sale.car_id, sale.dealer_id, sale.owner_name, sale.cnic, sale.contact])

    def load_from_csv(self):
        try:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    sale = Sale(row['Car ID'], row['Dealer ID'], row['Owner Name'], row['CNIC'], row['Contact'])
                    self.queue.append(sale)
        except FileNotFoundError:
            pass
    def get_all_sales(self):
     return list(self.queue)