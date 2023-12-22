import backend as bk
from datetime import datetime
from flask import Flask, request, render_template


app = Flask(__name__)

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
    if request.method == 'POST':
        email = request.form.get('exampleInputEmail1')
        password = request.form.get('exampleInputPassword1')
        
        if bk.login_check(email, password):
            return set_index_page()
        else:
            error_message = "Login failed. Please check your information and try again."
            return render_template('giris.html', error_message=error_message)


@app.route('/findVoyage', methods=["GET", "POST"])
def findVoyage():
    if request.method == 'POST':
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')
        day = request.form.get('day')
        month = request.form.get('month')
        year = request.form.get('year')

        # Do something with the selected values, for example:
        print(f"From Location: {from_location}")
        print(f"To Location: {to_location}")
        print(f"Date: {day}-{month}-{year}")


def set_index_page():
    locations = bk.get_locations()
    # Simulated data for date options
    days = [str(i).zfill(2) for i in range(1, 32)]  # 01 to 31
    months = [str(i).zfill(2) for i in range(1, 13)]  # 01 to 12
    current_year = datetime.now().year

    years = [str(i) for i in range(current_year, current_year+2)]  # current year to current year + 1

    return render_template('index.html', locations=locations, days=days, months=months, years=years)





# render the html pages to add them to server
@app.route('/index.html', methods=["GET"])
def anasayfa():
    return render_template('index.html')

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
