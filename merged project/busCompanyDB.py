import pyodbc
from datetime import datetime, timedelta


connStr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=lucimark0;DATABASE=BUSCOMPANYDB;Trusted_Connection=yes'
# Yukarıdaki satırı kendi veritabanı bilgilerinizle doldurmalısınız.

createCustomerRoleTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'customer_role')
BEGIN
   CREATE TABLE customer_role (
       customerRoleID tinyint PRIMARY KEY IDENTITY,
       customerRole VARCHAR(50)
   )
END"""

createCustomerTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'customer')
BEGIN
  CREATE TABLE customer (
      tc VARCHAR(11) PRIMARY KEY,
      name VARCHAR(50),
      surname VARCHAR(50),
      email VARCHAR(50),
      password VARCHAR(50),
      phone VARCHAR(11),
      customerRoleID tinyint FOREIGN KEY REFERENCES customer_role(customerRoleID)
  )
END"""

createCityTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'city')
BEGIN
   CREATE TABLE city (
       cityID tinyint PRIMARY KEY IDENTITY,
       cityName VARCHAR(50)
   )
END"""

createRouteTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'route')
BEGIN
   CREATE TABLE route (
       routeID tinyint PRIMARY KEY IDENTITY,
       departure tinyint FOREIGN KEY REFERENCES city(cityID),
       departurePlatform tinyint,
       arrival tinyint FOREIGN KEY REFERENCES city(cityID),
       arrivalPlatform tinyint,
       estTime smallint
   )
END"""

createVoyageTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'voyage')
BEGIN
    CREATE TABLE voyage (
        voyageID tinyint PRIMARY KEY IDENTITY,
        voyageDate DATE,
        startTime VARCHAR(5),
        voyageName VARCHAR(50),
    )END
"""

createVoyageRouteTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'voyage_route')
BEGIN
    CREATE TABLE voyage_route (
    voyageRouteID smallint PRIMARY KEY IDENTITY,
    voyageID tinyint FOREIGN KEY REFERENCES voyage(voyageID),
    routeID tinyint FOREIGN KEY REFERENCES route(routeID),
    sequenceOrder smallint NOT NULL
)END
"""

create_voyage_route_trigger = """
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_voyage_route_insert')
BEGIN
    EXEC('
    CREATE TRIGGER tr_voyage_route_insert
    ON voyage_route
    AFTER INSERT
    AS
    BEGIN
        UPDATE vr
        SET sequenceOrder = vr.sequenceOrder + 1
        FROM voyage_route vr
        INNER JOIN inserted i ON vr.voyageRouteID = i.voyageRouteID;
    END
    ');
END;
"""

createBusTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'bus')
BEGIN
   CREATE TABLE bus (
       busID smallint PRIMARY KEY IDENTITY,
       voyageRouteID smallint FOREIGN KEY REFERENCES voyage_route(voyageRouteID),
       plate VARCHAR(10),
       seat VARCHAR(38) DEFAULT REPLICATE('0', 38),
       platformno tinyint DEFAULT 0,
       currentCity tinyint FOREIGN KEY REFERENCES city(cityID)
   )
END"""

createPriceTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'price')
BEGIN
    CREATE TABLE price (
        priceID smallint PRIMARY KEY IDENTITY,
        firstCity tinyint FOREIGN KEY REFERENCES city(cityID),
        secondCity tinyint FOREIGN KEY REFERENCES city(cityID),
        price DECIMAL(10, 2)
    )
END"""

createTicketTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ticket')
BEGIN
    CREATE TABLE ticket (
        ticketID smallint PRIMARY KEY IDENTITY,
        tc VARCHAR(11) FOREIGN KEY REFERENCES customer(tc),
        busID smallint FOREIGN KEY REFERENCES bus(busID),
        priceID smallint FOREIGN KEY REFERENCES price(priceID),
        gender VARCHAR(1),
        seat VARCHAR(38),
        ticketDate DATETIME DEFAULT GETDATE()
    )
END"""

#------------------------#

insertCustomerRole = """
INSERT INTO customer_role (customerRole)
SELECT ?
"""

insertCustomer = """
INSERT INTO customer (tc, name, surname, email, password, phone, customerRoleID)
SELECT ?, ?, ?, ?, ?, ?, ?
"""

insertCity = """
INSERT INTO city (cityName)
SELECT ?
"""

insertRoute = """
INSERT INTO route (departure, departurePlatform, arrival, arrivalPlatform, estTime)
SELECT ?, ?, ?, ?, ?
"""

insertVoyage = """
INSERT INTO voyage (voyageDate, startTime)
SELECT ?,?
"""

insertVoyageRoute = """
INSERT INTO voyage_route (voyageID, routeID, sequenceOrder)
SELECT ?, ?, ?
"""

insertBus = """
INSERT INTO bus (voyageRouteID, plate, seat, platformno, currentCity)
SELECT ?, ?, REPLICATE('0', 38), ?, ?
"""

insertPrice = """
INSERT INTO price (firstCity, secondCity, price)
SELECT ?, ?, ?
"""

createTicket = """
INSERT INTO ticket (tc, busID, priceID, gender, seat, ticketDate)
SELECT ?, ?, ?, ?, ?, ?
"""

#------------------------#

# further brain needed
select_voyage_based_date = """SELECT * FROM voyage
JOIN voyage_route ON voyage.voyageID = voyage_route.voyageID
WHERE voyage.voyageDate = ? """

#------------------------#

checkRegister = """SELECT * FROM customer WHERE tc = ? OR email = ? OR phone = ?
"""

checkLogin = """SELECT * FROM customer WHERE email = ? AND password = ?"""

class BusCompanyDB:
    def __init__(self) -> None:
        self.con = pyodbc.connect(connStr)
        self.cur = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute(createCustomerRoleTableSTR)
        self.cur.execute(createCustomerTableSTR)
        self.cur.execute(createCityTableSTR)
        self.cur.execute(createRouteTableSTR)
        self.cur.execute(createVoyageTableSTR)
        self.cur.execute(createVoyageRouteTableSTR)
        self.cur.execute(create_voyage_route_trigger)
        self.cur.execute(createBusTableSTR)
        self.cur.execute(createPriceTableSTR)
        self.cur.execute(createTicketTableSTR)

    #------------------------#

    def insert_customer_role(self, customer_role):
        self.cur.execute(insertCustomerRole, (customer_role))

    def insert_customer(self, tc, name, surname, email, password, phone, customerRoleID = 1):
        self.cur.execute(insertCustomer, (tc, name, surname, email, password, phone, customerRoleID))

    def insert_city(self, city_name):
        self.cur.execute(insertCity, (city_name))

    def insert_route(self, departure, departurePlatform, arrival, arrivalPlatform, estTime):
        self.cur.execute(insertRoute, (departure, departurePlatform, arrival, arrivalPlatform, estTime))

    def insert_voyage(self, voyageDate, startTime):
        self.cur.execute(insertVoyage, (voyageDate, startTime, voyageDate))

    def insert_voyage_route(self, voyageID, routeID, seq):
        self.cur.execute(insertVoyageRoute, (voyageID, routeID. seq))

    def insert_bus(self, voyageRouteID, plate, platformno, currentCity):
        self.cur.execute(insertBus, (voyageRouteID, plate, platformno, currentCity))

    def insert_price(self, firstCity, secondCity, price):
        self.cur.execute(insertPrice, (firstCity, secondCity, price))

    def create_ticket(self, busID, priceID, gender, seat, ticketDate):
        self.cur.execute(createTicket, (busID, priceID, gender, seat, ticketDate))

    #------------------------#

    def select_voyage_based_date(self, date):
        date = datetime.strptime(date, '%d-%m-%Y').date()
        #print(self.cur.execute(select_voyage_based_date, (date,)).fetchall())

    #------------------------#

    def check_register(self, tc, email, phone):
        return self.cur.execute(checkRegister, (tc, email, phone)).fetchone()

    def check_login(self, email, password):
        return self.cur.execute(checkLogin, (email, password)).fetchone()

    #------------------------#

    def get_cities(self):
        return self.cur.execute("SELECT cityName FROM city").fetchall()


bc = BusCompanyDB()
bc.cur.commit()
def get_customer_role():
    customer_role = input("Enter customer role: ")
    bc.insert_customer_role(customer_role)
    bc.cur.commit()

def get_customer():
    tc = input("Enter TC: ")
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    phone = input("Enter phone: ")
    customerRoleID = input("Enter customer role ID: ")
    bc.insert_customer(tc, name, surname, email, password, phone, customerRoleID)
    bc.cur.commit()

def get_route():
    for i in range(1,5):
        departure = i
        departurePlatform = i
        arrival = i+1
        arrivalPlatform = i+1
        estTime = i+1
        bc.insert_route(departure, departurePlatform, arrival, arrivalPlatform, estTime)
    bc.cur.commit()

def get_voyage():
    voyageDate = datetime.strptime(input("date seperated with - : "), '%d-%m-%Y').date()
    startTime = input("Enter start time: ")
    bc.insert_voyage(voyageDate, startTime)
    bc.cur.commit()

def get_voyage_route():
    voyageID = input("Enter voyage ID: ")
    routeID = input("Enter route ID: ")
    bc.insert_voyage_route(voyageID, routeID)
    bc.cur.commit()

def get_bus():
    voyageRouteID = 1
    plate = '123'
    platformno = '1'
    currentCity = '1'
    bc.insert_bus(voyageRouteID, plate, platformno, currentCity)
    bc.cur.commit()

def get_price():
    firstCity = input("Enter first city: ")
    secondCity = input("Enter second city: ")
    price = input("Enter price: ")
    bc.insert_price(firstCity, secondCity, price)
    bc.cur.commit()

def get_ticket():
    busID = input("Enter bus ID: ")
    priceID = input("Enter price ID: ")
    gender = input("Enter gender: ")
    seat = input("Enter seat: ")
    ticketDate = input("Enter ticket date: ")
    bc.create_ticket(busID, priceID, gender, seat, ticketDate)
    bc.cur.commit()


def create_voyage():
    voyage_date_str = datetime.now().strftime("%Y-%m-%d").split(" ")[0]
    start_time = '08:00'
    voyage_name = input("Enter Voyage Name: ")
    generate_option = 'None'

    # Convert string to datetime
    try:
        voyage_date = datetime.strptime(voyage_date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Insert the voyage into the table
    insert_voyage_sql = f"""
    INSERT INTO voyage (voyageDate, startTime, voyageName)
    VALUES ('{voyage_date}', '{start_time}', '{voyage_name}')
    """
    print(f"Inserted Voyage:\n{insert_voyage_sql}")

    # Generate long voyages based on the selected option
    if generate_option != "None":
        duration = {"1Week": 7, "2Weeks": 14, "1Month": 30}.get(generate_option)
        if duration:
            print(f"\nGenerated Long Voyages:")
            for i in range(duration):
                current_date = voyage_date + timedelta(days=i)
                insert_long_voyage_sql = f"""
                INSERT INTO voyage (voyageDate, startTime, voyageName)
                VALUES ('{current_date}', '{start_time}', '{voyage_name}')
                """
                print(f"{i+1}. {insert_long_voyage_sql}")
    bc.cur.execute(insert_voyage_sql)
    bc.cur.commit()

def create_voyage_route():
    for i in range(1,5):
        voyage_id = 1
        route_id = i
        sequence_order = bc.cur.execute("SELECT MAX(sequenceOrder) FROM voyage_route WHERE voyageID = ?", (voyage_id,)).fetchone()[0]
        seq = sequence_order if sequence_order != None else 0
        bc.cur.execute(insertVoyageRoute, (voyage_id, route_id, seq))
        bc.cur.commit()


def get_city(city_names):
    for city_name in city_names:
        bc.insert_city(city_name)
        bc.cur.commit()



if __name__ == "__main__":
    city_names_to_insert = ["City1", "City2", "City3", "City4", "City5"]
    get_city(city_names_to_insert)
    get_route()
    create_voyage()
    create_voyage_route()
    get_bus()
    pass