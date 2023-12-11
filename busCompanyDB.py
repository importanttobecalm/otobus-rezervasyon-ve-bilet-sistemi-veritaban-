import pyodbc
from datetime import datetime


connStr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=lucimark0;DATABASE=BUSCOMPANYDB;Trusted_Connection=yes'
# Yukarıdaki satırı kendi veritabanı bilgilerinizle doldurmalısınız.

createCustomerRoleTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'customer_role')
BEGIN
   CREATE TABLE customer_role (
       customerRoleID tinyint PRIMARY KEY identity,
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
       cityID tinyint PRIMARY KEY identity,
       cityName VARCHAR(50)
   )
END"""

createRouteTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'route')
BEGIN
   CREATE TABLE route (
       routeID tinyint PRIMARY KEY identity,
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
        voyageID tinyint PRIMARY KEY identity,
        voyageDate date,
        startTime varchar(5)
    )
END"""

createVoyageRouteTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'voyage_route')
BEGIN
    CREATE TABLE voyage_route (
        voyageRouteID smallint PRIMARY KEY identity,
        voyageID tinyint FOREIGN KEY REFERENCES voyage(voyageID),
        routeID tinyint FOREIGN KEY REFERENCES route(routeID),
        sequenceOrder smallint
    )
END"""

createBusTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'bus')
BEGIN
   CREATE TABLE bus (
       busID smallint PRIMARY KEY identity,
       voyageRouteID smallint FOREIGN KEY REFERENCES voyage_route(voyageRouteID),
       plate VARCHAR(10),
       seat VARCHAR(38) DEFAULT REPLICATE('0', 38),
       platformno tinyint default 0,
       currentCity tinyint FOREIGN KEY REFERENCES city(cityID)
   )
END"""

createPriceTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'price')
BEGIN
    CREATE TABLE price (
        priceID smallint PRIMARY KEY identity,
        firstCity tinyint FOREIGN KEY REFERENCES city(cityID),
        secondCity tinyint FOREIGN KEY REFERENCES city(cityID),
        price DECIMAL(10, 2)
    )
END"""

createTicketTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ticket')
BEGIN
    CREATE TABLE ticket (
        ticketID smallint PRIMARY KEY identity,
        tc VARCHAR(11) foreign key REFERENCES customer(tc),
        busID smallint FOREIGN KEY REFERENCES bus(busID),
        priceID smallint FOREIGN KEY REFERENCES price(priceID),
        gender VARCHAR(1),
        seat VARCHAR(38),
        ticketDate DATETIME default GETDATE(),
        FOREIGN KEY (tc) REFERENCES customer(tc)
    )
END"""

#------------------------#

insertCustomerRole = """
INSERT INTO customer_role (customerRole)
SELECT ?
WHERE NOT EXISTS(SELECT 1
              FROM customer_role c
              WHERE c.customerRole = ?)
"""

insertCustomer = """
INSERT INTO customer (tc, name, surname, email, password, phone, customerRoleID)
SELECT ?, ?, ?, ?, ?, ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM customer c
              WHERE c.tc = ?)
"""

insertCity = """
INSERT INTO city (cityName)
SELECT ?
WHERE NOT EXISTS(SELECT 1
              FROM city c
              WHERE c.cityName = ?)
"""

insertRoute = """
INSERT INTO route (departure, departurePlatform, arrival, arrivalPlatform, estTime)
SELECT ?, ?, ?, ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM route r
              WHERE r.departure = ? AND r.departurePlatform = ? AND r.arrival = ? AND r.arrivalPlatform = ? AND r.estTime = ?)
"""

insertVoyage = """
INSERT INTO voyage (voyageDate, startTime)
SELECT ?,?
WHERE NOT EXISTS(SELECT 1
              FROM voyage v
              WHERE v.voyageDate = ?)
"""

insertVoyageRoute = """
INSERT INTO voyage_route (voyageID, routeID, sequenceOrder)
SELECT ?, ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM voyage_route vr
              WHERE vr.voyageID = ? AND vr.routeID = ? AND vr.sequenceOrder = ?)
"""

insertBus = """
INSERT INTO bus (voyageRouteID, plate, seat, platformno, currentCity)
SELECT ?, ?, REPLICATE('0', 38), ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM bus b
              WHERE b.voyageRouteID = ? AND b.plate = ? AND b.platformno = ? AND b.currentCity = ?)
"""

insertPrice = """
INSERT INTO price (firstCity, secondCity, price)
SELECT ?, ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM price p
              WHERE p.firstCity = ? AND p.secondCity = ? AND p.price = ?)
"""

createTicket = """
INSERT INTO ticket (tc, busID, priceID, gender, seat, ticketDate)
SELECT ?, ?, ?, ?, ?, ?
WHERE NOT EXISTS(SELECT 1
              FROM ticket t
              WHERE t.tc = ? AND t.busID = ? AND t.priceID = ? AND t.gender = ? AND t.seat = ? AND t.ticketDate = ?)
"""

# further brain needed
select_voyage_based_date = """SELECT * FROM voyage 
JOIN voyage_route ON voyage.voyageID = voyage_route.voyageID
WHERE voyage.voyageDate = ? """

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
        self.cur.execute(createBusTableSTR)
        self.cur.execute(createPriceTableSTR)
        self.cur.execute(createTicketTableSTR)
    
    def insert_customer_role(self, customer_role):
        self.cur.execute(insertCustomerRole, (customer_role,customer_role))
        
    def insert_customer(self, tc, name, surname, email, password, phone, customerRoleID):
        self.cur.execute(insertCustomer, (tc, name, surname, email, password, phone, customerRoleID, tc))

    def insert_city(self, city_name):
        self.cur.execute(insertCity, (city_name, city_name))
    
    def insert_route(self, departure, departurePlatform, arrival, arrivalPlatform, estTime):
        self.cur.execute(insertRoute, (departure, departurePlatform, arrival, arrivalPlatform, estTime, departure, departurePlatform, arrival, arrivalPlatform, estTime))
    
    def insert_voyage(self, voyageDate, startTime):
        self.cur.execute(insertVoyage, (voyageDate, startTime, voyageDate))
    
    def insert_voyage_route(self, voyageID, routeID, sequenceOrder):
        self.cur.execute(insertVoyageRoute, (voyageID, routeID, sequenceOrder, voyageID, routeID, sequenceOrder))
    
    def insert_bus(self, voyageRouteID, plate, platformno, currentCity):
        self.cur.execute(insertBus, (voyageRouteID, plate, platformno, currentCity, voyageRouteID, plate, platformno, currentCity))
    
    def insert_price(self, firstCity, secondCity, price):
        self.cur.execute(insertPrice, (firstCity, secondCity, price, firstCity, secondCity, price))
    
    def create_ticket(self, busID, priceID, gender, seat, ticketDate):
        self.cur.execute(createTicket, (busID, priceID, gender, seat, ticketDate, busID, priceID, gender, seat, ticketDate))
    
    def select_voyage_based_date(self, date):
        date = datetime.strptime(date, '%d-%m-%Y').date()
        print(self.cur.execute(select_voyage_based_date, (date,)).fetchall())

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

def get_city():
    city_name = input("Enter city name: ")
    bc.insert_city(city_name)
    bc.cur.commit()

def get_route():
    departure = input("Enter departure: ")
    departurePlatform = input("Enter departure platform: ")
    arrival = input("Enter arrival: ")
    arrivalPlatform = input("Enter arrival platform: ")
    estTime = input("Enter estimated time: ")
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
    sequenceOrder = input("Enter sequence order: ")
    bc.insert_voyage_route(voyageID, routeID, sequenceOrder)
    bc.cur.commit()

def get_bus():
    voyageRouteID = input("Enter voyageRouteID: ")
    plate = input("Enter plate: ")
    platformno = input("Enter platform number: ")
    currentCity = input("Enter current city: ")
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


# get_customer_role()
# get_customer()
# print("city")
# get_city()
# get_city()
# get_city()
# get_city()
# print("route")
# get_route()
# get_route()
# get_route()
# print("voyage")
# get_voyage()
# print("voyage route")
# get_voyage_route()
# get_voyage_route()
# get_voyage_route()
# print("bus")
# get_bus()
# get_price()

bc.select_voyage_based_date("12-11-2023")