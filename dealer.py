# dealer.py

import csv
import os

class DealerNode:
    def __init__(self, dealer_id, name, location):
        self.dealer_id = dealer_id
        self.name = name
        self.location = location
        self.next = None

class DealerLinkedList:
    def __init__(self):
        self.head = None
        self.csv_file = 'dealers.csv'
        self.load_from_csv()

    def add_dealer(self, dealer_id, name, location):
        new_dealer = DealerNode(dealer_id, name, location)
        if not self.head:
            self.head = new_dealer
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_dealer
        self.save_to_csv(new_dealer)

    def save_to_csv(self, dealer_node):
        file_exists = os.path.isfile(self.csv_file)
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Dealer ID', 'Name', 'Location'])  # Header
            writer.writerow([dealer_node.dealer_id, dealer_node.name, dealer_node.location])

    def load_from_csv(self):
    # Clear existing list first
     self.head = None
    
     if not os.path.exists(self.csv_file):
        return
        
     try:
         with open(self.csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Only add if all required fields exist
                if all(key in row for key in ['Dealer ID', 'Name', 'Location']):
                    self.add_dealer_no_save(row['Dealer ID'], row['Name'], row['Location'])
     except Exception as e:
        print(f"Error loading dealers from CSV: {e}")

    def add_dealer_no_save(self, dealer_id, name, location):
        new_dealer = DealerNode(dealer_id, name, location)
        if not self.head:
            self.head = new_dealer
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_dealer

    def get_all_dealers(self):
        dealers = []
        current = self.head
        while current:
            dealers.append({
                "dealer_id": current.dealer_id,
                "name": current.name,
                "location": current.location
            })
            current = current.next
        return dealers

# Add this to dealer.py

    def update_dealer(self, dealer_id, new_name, new_location):
        current = self.head
        updated = False
        while current:
            if current.dealer_id == dealer_id:
                current.name = new_name
                current.location = new_location
                updated = True
                break
            current = current.next
        if updated:
            self._rewrite_csv()
        return updated

    def _rewrite_csv(self):
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Dealer ID', 'Name', 'Location'])  # Header
            current = self.head
            while current:
                writer.writerow([current.dealer_id, current.name, current.location])
                current = current.next

# Add to dealer.py

    def delete_dealer(self, dealer_id):
        current = self.head
        prev = None
        deleted = False

        while current:
            if current.dealer_id == dealer_id:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                deleted = True
                break
            prev = current
            current = current.next

        if deleted:
            self._rewrite_csv()
        return deleted
