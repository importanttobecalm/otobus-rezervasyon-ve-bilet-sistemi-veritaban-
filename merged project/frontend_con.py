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
            return open_admin_panel()
            return render_template('giris.html', error_message=error_message, user_is_authenticated=user_is_authenticated, user_name=user_name)


def open_admin_panel():
    customers = bk.get_customer_tableSP()
    buses = bk.bc.cur.execute("SELECT * FROM bus WHERE voyageID IS NULL").fetchall()
    voyages = bk.bc.cur.execute("SELECT * FROM voyage").fetchall()
    routes = bk.bc.cur.execute("SELECT * FROM route").fetchall()
    voyage_routes = bk.bc.cur.execute("SELECT * FROM voyage_route").fetchall()
    tickets = bk.get_ticket_tableSP()
    return render_template('admin.html', customers = customers, buses = buses, voyages = voyages, routes = routes, voyage_routes = voyage_routes, tickets=tickets)

@app.route('/get_table_name', methods=['POST'])
def get_table_name():
    table_name = request.form.get('table_name')
    bk.get_tables_pdf(table_name)
    return open_admin_panel()

@app.route('/add_customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        tc = request.form['tc']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        phone = request.form['phone']
        role_id = request.form['role_id']
        bk.insert_customer(tc, name, surname, email, phone, role_id)
        # Add the new customer to the database (replace with your database logic)
        # Example: db.add_customer(tc, name, surname, email, phone, role_id)

        # Redirect to the page with the updated customer list
        return open_admin_panel()

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    if request.method == 'POST':
        customer_tc = request.form['customer_tc']
        bus_id = request.form['bus_id']
        price_id = request.form['price_id']
        seat = request.form['seat']
        ticket_date = request.form['ticket_date']
        bk.create_ticket_admin(customer_tc, bus_id, price_id, seat, ticket_date)
        # Add the new ticket to the database (replace with your database logic)
        # Example: db.add_ticket(customer_tc, bus_id, price_id, gender, seat, ticket_date)

        # Redirect to the page with the updated ticket list
        return open_admin_panel()

@app.route('/delete_customer/<tc>', methods=['POST'])
def delete_customer(tc):
    bk.delete_customer_with_tc(tc)
    return open_admin_panel()

@app.route('/delete_ticket/<ticketID>', methods=['POST'])
def delete_ticket(ticketID):
    bk.delete_ticket_with_ticketID(ticketID)
    return open_admin_panel()

@app.route('/assign_bus_to_voyage', methods=['POST'])
def assign_bus_to_voyage():
    bus_id = request.form.get('bus_id')
    voyage_id = request.form.get('voyage_id')
    bk.assign_bus_to_voyage(bus_id, voyage_id)
    return open_admin_panel()

@app.route('/add_bus', methods=['POST'])
def add_bus():
    bus_id = request.form.get('plate')
    bk.add_buss(bus_id)
    return open_admin_panel()

@app.route('/add_voyage_route', methods=['POST'])
def add_voyage_route():
    # Extract data from the form
    voyage_id = request.form.get('voyage_id')
    route_id = request.form.get('route_id')

    bk.create_voyage_route(voyage_id, route_id)

    return open_admin_panel()


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
            estTimeSTR = bk.get_estimated_time(from_location, to_location, suitable_buses[i-1])
            seferler_data.append({"fromLoc": from_location, "toLoc": to_location, 
         "time": estTimeSTR, "price": str(bk.get_price_info()), 
         "features": ["WiFi", "Ücretsiz Yemek", "Televizyon"], 
         "bus_type": "1+1 10 Koltuklu Lüks Otobüs", "bus_id": str(suitable_buses[i-1])})
    
    return render_template('seferler.html', seferler_data=seferler_data, user_name=user_name)

@app.route('/busChoice', methods=["GET", "POST"])
def busChoice():
    global reservedSeats
    if request.method == 'POST':
        bus_id = request.form['purchase_button']
        bk.set_selected_bus(bus_id)
        """ fix here """
        reservedSeats = bk.get_reserved_seats()
        return render_template('koltukSec.html', reservedSeats=reservedSeats, user_name=user_name)


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
            
    return render_template('satinAl.html', user_name=user_name)


@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if request.method == 'POST':
        bk.create_ticket()

        bus_tickets = bk.customer_tickets_info()
        
        return render_template('biletlerim.html', bus_tickets=bus_tickets, user_name=user_name)

@app.route('/cancel_ticket', methods=['POST'])
def cancel_ticket():
    if request.method == 'POST':
        pnr_no = request.form.get('pnr_no')  # Get PNR number from the form data
        bk.delete_ticket_with_ticket_id(pnr_no)
        # Add your logic here to cancel the ticket (e.g., update the database)
                
        return set_index_page()










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
    return set_index_page()

app.route('/admin.html', methods=["GET"])
def admin():
    return render_template('admin.html')

@app.route('/biletlerim.html', methods=["GET"])
def biletlerim():
    bus_tickets = bk.customer_tickets_info()
    return render_template('biletlerim.html', bus_tickets=bus_tickets, user_name=user_name)

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

@app.route('/loading.html', methods=["GET"])
def loading():
    return render_template('loading.html')


if __name__ == '__main__':
    app.run(debug=True)
