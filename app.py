from flask import Flask, flash, render_template, request, redirect, url_for
from inventory import CarInventory, Car
from dealer import DealerLinkedList, DealerNode
from sale import SalesQueue, Sale
import matplotlib.pyplot as plt
from flask import send_file
import base64
from collections import defaultdict
import numpy as np
import io
import os
from werkzeug.utils import secure_filename
from flask import jsonify





sales_queue = SalesQueue()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key')

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


dealer_list = DealerLinkedList()
inventory = CarInventory()
inventory.load_from_csv()

@app.route('/')
def home():
    return render_template("home.html", show_video=True)

@app.route('/car', methods=['GET', 'POST'])
def manage_car():
    inventory.load_from_csv()  # Ensure latest data

    if request.method == 'POST':
        form_action = request.form.get('action')

        # Shared fields
        car_id = request.form['car_id']
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        price = request.form.get('price')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        if form_action == 'add':
            new_car = Car(car_id, brand, model, year, price, latitude, longitude, image_filename)
            inventory.add_car(new_car)
            return jsonify({'status': 'success', 'message': '✅ Car added successfully!'})

        elif form_action == 'update':
            inventory.update_car(car_id, brand, model, year, price, latitude, longitude, image_filename)
            return jsonify({'status': 'success', 'message': '✏️ Car updated successfully!'})

        elif form_action == 'delete':
            inventory.delete_car_by_id(car_id)
            return jsonify({'status': 'success', 'message': '🗑️ Car deleted successfully!'})

        return jsonify({'status': 'error', 'message': '❌ Unknown action'})

    # GET request
    cars = inventory.get_all_cars()
    # Prepare data for both the table and the map
    map_data = []
    for car in cars:
        try:
            if car.latitude and car.longitude:
                map_data.append({
                    'title': f"{car.brand or 'Unknown'} {car.model or 'Car'} ({car.year or 'N/A'}) - ${car.price or '0'}",
                    'latitude': float(car.latitude),
                    'longitude': float(car.longitude)
                })
        except (ValueError, TypeError):
            print(f"Skipping car {car.car_id} due to invalid coordinates")
            continue

    # Debug output
    print(f"Prepared {len(map_data)} valid car locations for map")
    
    return render_template('car.html', 
                         cars=cars, 
                         car_data=[c.__dict__ for c in cars],  # More reliable data passing
                         map_data=map_data)
 


from flask import flash  # Add this at the top

@app.route('/dealer', methods=['GET', 'POST'])
def manage_dealer():
    # Always reload from CSV to get latest data
    dealer_list.load_from_csv()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            dealer_id = request.form.get('dealer_id')
            name = request.form.get('name')
            location = request.form.get('location')
            
            # Validate inputs
            if not all([dealer_id, name, location]):
                flash('All fields are required!', 'error')
                return redirect(url_for('manage_dealer'))
            
            # Check if dealer exists
            current = dealer_list.head
            while current:
                if current.dealer_id == dealer_id:
                    flash(f'Dealer ID {dealer_id} already exists!', 'error')
                    return redirect(url_for('manage_dealer'))
                current = current.next
                
            dealer_list.add_dealer(dealer_id, name, location)
            flash('Dealer added successfully!', 'success')
            
        elif action == 'update':
            dealer_id = request.form.get('dealer_id')
            name = request.form.get('name')
            location = request.form.get('location')
            
            if not all([dealer_id, name, location]):
                flash('All fields are required!', 'error')
                return redirect(url_for('manage_dealer'))
            
            if dealer_list.update_dealer(dealer_id, name, location):
                flash('Dealer updated successfully!', 'success')
            else:
                flash(f'Dealer ID {dealer_id} not found!', 'error')
            
        elif action == 'delete':
            dealer_id = request.form.get('dealer_id')
            
            if dealer_list.delete_dealer(dealer_id):
                flash('Dealer deleted successfully!', 'success')
            else:
                flash(f'Dealer ID {dealer_id} not found!', 'error')
        
        return redirect(url_for('manage_dealer'))
    
    # GET request
    dealers = dealer_list.get_all_dealers()
    return render_template('dealer.html', dealers=dealers, dealer_data=dealers)
@app.route('/sell', methods=['GET', 'POST'])
def sell_car():
    if request.method == 'POST':
        car_id = request.form['car_id']
        dealer_id = request.form['dealer_id']
        owner_name = request.form['owner_name']
        cnic = request.form['cnic']
        contact = request.form['contact']

        # Create and record the sale
        sale = Sale(car_id, dealer_id, owner_name, cnic, contact)
        sales_queue.enqueue_sale(sale)

        # Remove the car from inventory
        inventory.delete_car_by_id(car_id)
        
        flash('Car sold successfully!', 'success')
        return redirect(url_for('sell_car'))

    # Get available cars (not sold yet)
    all_cars = inventory.get_all_cars()
    sold_car_ids = {sale.car_id for sale in sales_queue.get_all_sales()}
    available_cars = [car for car in all_cars if car.car_id not in sold_car_ids]
    
    dealers = dealer_list.get_all_dealers()
    return render_template('sell_car.html', cars=available_cars, dealers=dealers)
@app.route('/analytics')
def analytics():
    sales = sales_queue.get_all_sales()

    # Collect all prices
    prices = []
    for sale in sales:
        car = inventory.get_car_by_id(sale.car_id)
        if car and hasattr(car, 'price'):
            prices.append(int(car.price))

    # Bin prices into 5 equal-width intervals
    if not prices:
        return render_template('analytics.html', chart_data={})

    min_price = min(prices)
    max_price = max(prices)
    bin_width = (max_price - min_price) // 5 or 1

    bins = [min_price + i * bin_width for i in range(6)]
    bin_labels = [f"{bins[i]} - {bins[i+1]-1}" for i in range(5)]
    bin_counts = [0] * 5

    for price in prices:
        for i in range(5):
            if bins[i] <= price < bins[i+1]:
                bin_counts[i] += 1
                break
        else:
            if price == bins[-1]:
                bin_counts[-1] += 1

    chart_data = {
        "labels": bin_labels,
        "counts": bin_counts
    }

    return render_template('analytics.html', chart_data=chart_data)


@app.route('/analytics_dealer_owner')
def analytics_dealer_owner():
    dealer_owner_sales = defaultdict(lambda: defaultdict(int))  # Dealer → Owner → Count

    for sale in sales_queue.get_all_sales():
        dealer_owner_sales[sale.dealer_id][sale.owner_name] += 1

    owners = sorted(list(set(owner for dealer in dealer_owner_sales for owner in dealer_owner_sales[dealer])))
    dealers = sorted(list(dealer_owner_sales.keys()))

    chart_data = {
        "owners": owners,
        "datasets": []
    }

    for dealer in dealers:
        sales_counts = [dealer_owner_sales[dealer].get(owner, 0) for owner in owners]
        chart_data["datasets"].append({
            "label": dealer,
            "data": sales_counts
        })

    return render_template('analytics_dealer_owner.html', chart_data=chart_data)

@app.route('/location')
def location():
    inventory.load_from_csv()
    cars = inventory.get_all_cars()
    map_data = []
    
    for car in cars:
        try:
            if car.latitude and car.longitude:
                map_data.append({
                    'title': f"{car.brand} {car.model} ({car.year})",
                    'latitude': float(car.latitude),
                    'longitude': float(car.longitude)
                })
        except Exception as e:
            print(f"Error processing car: {e}")
            continue

    print("Final map data to be sent to template:")
    print(map_data)  # This will show in your Flask console
    
    return render_template('location.html', map_data=map_data)
@app.route('/car_view', methods=['GET', 'POST'])
def car_view():
    inventory.load_from_csv()  # Ensure latest data
    cars = inventory.get_all_cars()

    print("\n=== Image Path Debug ===")
    for car in cars:
        print(f"Car ID: {car.car_id}, Image: {getattr(car, 'image_filename', 'N/A')}")
        # Ensure image_filename exists
        if not hasattr(car, 'image_filename'):
            car.image_filename = None
    print("======================\n")
    
    
    # Clean price data and convert to integers
    for car in cars:
        try:
            # Remove commas and convert to integer
            if hasattr(car, 'price') and car.price:
                car.price = int(str(car.price).replace(',', ''))
        except (ValueError, AttributeError):
            car.price = 0  # Default value if price is invalid
    
    # Search functionality
    search_results = []
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').lower()
        search_type = request.form.get('search_type', 'linear')
        
        if search_query:
            if search_type == 'binary':
                # Binary search requires sorted data
                sorted_cars = sorted(cars, key=lambda x: x.model.lower())
                search_results = binary_search_cars(sorted_cars, search_query)
            else:
                # Default to linear search
                search_results = linear_search_cars(cars, search_query)
        else:
            search_results = cars
    else:
        search_results = cars
    
    return render_template('car_view.html', cars=search_results)

# DSA Search Algorithms
def linear_search_cars(cars, query):
    results = []
    for car in cars:
        if (query in car.brand.lower() or 
            query in car.model.lower() or 
            query in str(car.year).lower() or 
            query in str(car.price).lower()):
            results.append(car)
    return results

def binary_search_cars(sorted_cars, query):
    results = []
    low = 0
    high = len(sorted_cars) - 1
    
    while low <= high:
        mid = (low + high) // 2
        car_model = sorted_cars[mid].model.lower()
        
        if query in car_model:
            # Found a match, now check neighboring elements
            results.append(sorted_cars[mid])
            
            # Check left side
            left = mid - 1
            while left >= 0 and query in sorted_cars[left].model.lower():
                results.append(sorted_cars[left])
                left -= 1
                
            # Check right side
            right = mid + 1
            while right < len(sorted_cars) and query in sorted_cars[right].model.lower():
                results.append(sorted_cars[right])
                right += 1
                
            return results
        elif query < car_model:
            high = mid - 1
        else:
            low = mid + 1
    
    return results

if __name__ == '__main__':
    app.run(debug=True)