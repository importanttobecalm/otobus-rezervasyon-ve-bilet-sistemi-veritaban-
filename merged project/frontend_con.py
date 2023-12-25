import backend as bk
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)

user_is_authenticated = False
user_name = None

@app.route('/', methods=["GET"])
def index():
    return render_template('giris.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        tc = request.form.get('tcno')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        # Do something with the username and password
        if bk.register_check(tc, name, surname, email, password, phone):
            return render_template('giris.html')
        else: 
            error_message = "Registration failed. Please check your information and try again."
            return render_template('kayitOl.html', error_message=error_message)

@app.route('/login', methods=["GET", "POST"])
def login():
    global user_is_authenticated
    global user_name
    
    if request.method == 'POST':
        email = request.form.get('exampleInputEmail1')
        password = request.form.get('exampleInputPassword1')
        
        user_is_authenticated = bk.login_check(email, password)
        if user_is_authenticated:
            user_name = bk.get_customer_name(email)
            return set_index_page()
        else:
            error_message = "Login failed. Please check your information and try again."
            customers = bk.bc.cur.execute("SELECT * FROM customer").fetchall()
            buses = bk.bc.cur.execute("SELECT * FROM bus").fetchall()
            voyages = bk.bc.cur.execute("SELECT * FROM voyage").fetchall()
            routes = bk.bc.cur.execute("SELECT * FROM route").fetchall()
            voyage_routes = bk.bc.cur.execute("SELECT * FROM voyage_route").fetchall()
            tickets = bk.bc.cur.execute("SELECT * FROM ticket").fetchall()
            return render_template('admin.html', customers = customers, buses = buses, voyages = voyages, routes = routes, voyage_routes = voyage_routes, tickets=tickets)
            return render_template('giris.html', error_message=error_message, user_is_authenticated=user_is_authenticated, user_name=user_name)

@app.route('/delete_customer/<tc>', methods=['POST'])
def delete_customer(tc):
    # Perform the customer deletion logic here
    # You should modify this based on your actual deletion process
    pass
    return redirect(url_for('admin_panel'))

@app.route('/delete_ticket/<ticketID>', methods=['POST'])
def delete_ticket(ticketID):
    # Perform the ticket deletion logic here
    # You should modify this based on your actual deletion process
    pass
    return redirect(url_for('admin_panel'))

@app.route('/assign_bus_to_voyage', methods=['POST'])
def assign_bus_to_voyage():
    # Extract data from the form
    # bus_id = request.form.get('bus_id')
    # voyage_id = request.form.get('voyage_id')

    # # Perform the assignment logic (modify based on your actual logic)
    # # For example, you might want to update the bus table with the voyage ID
    # # or create a new record in a table that represents the assignment.
    # # This is just a placeholder, update it based on your database structure and logic.
    # bk.bc.cur.execute("UPDATE bus SET voyageID = ? WHERE busID = ?", (voyage_id, bus_id))
    # bk.bc.cur.commit()
    pass
    # # Redirect back to the input page
    # return redirect(url_for('input_page'))

@app.route('/add_voyage_route', methods=['POST'])
def add_voyage_route():
    # Extract data from the form
    # voyage_id = request.form.get('voyage_id')
    # route_id = request.form.get('route_id')

    # # Perform the addition logic (modify based on your actual logic)
    # # For example, you might want to insert a new record in the voyage_route table.
    # # This is just a placeholder, update it based on your database structure and logic.
    # bc.cur.execute("INSERT INTO voyage_route (voyageID, routeID, sequenceOrder) VALUES (?, ?, 1)", (voyage_id, route_id))
    # bc.cur.commit()
    pass
    # # Redirect back to Panel 3
    # return redirect(url_for('panel3'))


@app.route('/logout')
def logout():
    global user_is_authenticated
    user_is_authenticated = False
    # Clear the user session
    # Redirect to the home page or any other page after logout
    return redirect(url_for('index'))

@app.route('/findVoyage', methods=["GET", "POST"])
def findVoyage():
    seferler_data = []
    if request.method == 'POST':

        if not user_is_authenticated:
            error_message = "Please login to continue."
            return render_template('giris.html', error_message=error_message, user_is_authenticated=user_is_authenticated, user_name=user_name)

        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')
        day = request.form.get('day')
        month = request.form.get('month')
        year = request.form.get('year')

        suitable_buses = bk.get_suitable_buses(from_location, to_location, f"{year}-{month}-{day}")
        for i in range(1,len(suitable_buses)+1):
            seferler_data.append({"fromLoc": from_location, "toLoc": to_location, 
         "time": "00:00 -> 03:00", "price": str(bk.get_price_info()), 
         "features": ["WiFi", "Ücretsiz Yemek", "Televizyon"], 
         "bus_type": "1+1 10 Koltuklu Lüks Otobüs", "bus_id": str(i)})
    
    return render_template('seferler.html', seferler_data=seferler_data)

@app.route('/busChoice', methods=["GET", "POST"])
def busChoice():
    global reservedSeats
    if request.method == 'POST':
        bus_id = request.form['purchase_button']
        bk.set_selected_bus(bus_id)
        """ fix here """
        reservedSeats = bk.get_reserved_seats()
        return render_template('koltukSec.html', reservedSeats=reservedSeats)


@app.route('/seatChoice', methods=["GET", "POST"])
def seatChoice():
    if request.method == 'POST':
        chosen_seats = request.form.get('chosen_seats', '')
        # Convert the comma-separated string to a list of integers
        # chosen_seats_list = list(map(int, chosen_seats.split(',')))

        # Now 'chosen_seats_list' contains the list of selected seats
        if chosen_seats == '':
            error_message = "please select seat before purchase"
            return render_template('koltukSec.html', error_message=error_message, reservedSeats=reservedSeats)
        else:
            bk.set_reserved_seat(chosen_seats)
            
    return render_template('satinAl.html')


@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if request.method == 'POST':
        bk.create_ticket()

        bus_tickets = bk.customer_tickets_info()
        
        return render_template('biletlerim.html', bus_tickets=bus_tickets)














def set_index_page():
    locations = bk.get_locations()
    # Simulated data for date options
    days = [str(i).zfill(2) for i in range(1, 32)]  # 01 to 31
    months = [str(i).zfill(2) for i in range(1, 13)]  # 01 to 12
    current_year = datetime.now().year

    years = [str(i) for i in range(current_year, current_year+2)]  # current year to current year + 1

    return render_template('index.html', locations=locations, days=days, months=months, years=years, user_is_authenticated=user_is_authenticated, user_name=user_name)


# render the html pages to add them to server
@app.route('/index.html', methods=["GET"])
def anasayfa():
    return render_template('index.html')

app.route('/admin.html', methods=["GET"])
def admin():
    return render_template('admin.html')

@app.route('/biletlerim.html', methods=["GET"])
def biletlerim():
    return render_template('biletlerim.html')

@app.route('/giris.html', methods=["GET"])
def giris():
    return render_template('giris.html')

@app.route('/kayitOl.html', methods=["GET"])
def kayitOl():
    return render_template('kayitOl.html')

@app.route('/seferler.html', methods=["GET"])
def seferler():
    return render_template('seferler.html')

@app.route('/koltukSec.html', methods=["GET"])
def koltukSec():
    return render_template('koltukSec.html')

@app.route('/satinAl.html', methods=["GET"])
def satinAl():
    return render_template('satinAl.html')

if __name__ == '__main__':
    app.run(debug=True)
