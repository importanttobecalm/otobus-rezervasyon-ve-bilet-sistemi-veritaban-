import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta


connStr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=lucimark0;DATABASE=BUSCOMPANYDBbk;Trusted_Connection=yes'
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
      customerRoleID tinyint FOREIGN KEY REFERENCES customer_role(customerRoleID) ON DELETE SET NULL
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
       departure tinyint FOREIGN KEY REFERENCES city(cityID) ON DELETE Cascade,
       departurePlatform tinyint,
       arrival tinyint FOREIGN KEY REFERENCES city(cityID) ON DELETE NO ACTION,
       arrivalPlatform tinyint,
       estTime smallint
   )
END
"""
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
    voyageID tinyint FOREIGN KEY REFERENCES voyage(voyageID) ON DELETE Cascade,
    routeID tinyint FOREIGN KEY REFERENCES route(routeID) ON DELETE SET NULL,
    sequenceOrder smallint NOT NULL
)END
"""

createBusTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'bus')
BEGIN
   CREATE TABLE bus (
       busID smallint PRIMARY KEY IDENTITY,
       voyageID tinyint FOREIGN KEY REFERENCES voyage(voyageID) ON DELETE NO ACTION,
       plate VARCHAR(10),
       seat VARCHAR(10) DEFAULT REPLICATE('0', 10),
       platformno tinyint DEFAULT 0,
       currentvoyageRoute smallint FOREIGN KEY REFERENCES voyage_route(voyageRouteID) ON DELETE SET NULL
   )
END"""

createBusSeatTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'bus_seat')
BEGIN
   CREATE TABLE bus_seat (
       busSeatID smallint PRIMARY KEY IDENTITY,
       busID smallint FOREIGN KEY REFERENCES bus(busID) ON DELETE Cascade,
       seat VARCHAR(10) DEFAULT REPLICATE('0', 10),
       reservedvoyageRoute smallint
   )
END"""

createPriceTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'price')
BEGIN
    CREATE TABLE price (
        priceID smallint PRIMARY KEY IDENTITY,
        firstCity tinyint FOREIGN KEY REFERENCES city(cityID) ON DELETE Cascade,
        secondCity tinyint FOREIGN KEY REFERENCES city(cityID) ON DELETE NO ACTION,
        price DECIMAL(10, 2)
    )
END"""

createTicketTableSTR = """
-- Check if the ticket table exists
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ticket')
BEGIN
    -- Create the ticket table
    CREATE TABLE ticket (
        ticketID smallint PRIMARY KEY IDENTITY,
        tc VARCHAR(11) FOREIGN KEY REFERENCES customer(tc) ON DELETE Cascade,
        busID smallint FOREIGN KEY REFERENCES bus(busID) ON DELETE SET NULL,
        priceID smallint FOREIGN KEY REFERENCES price(priceID) ON DELETE SET NULL,
        gender VARCHAR(1),
        seat VARCHAR(38),
        ticketDate DATETIME DEFAULT GETDATE()
    );
END
ELSE
BEGIN
    -- Check if the foreign key constraint exists and does not have ON DELETE SET NULL
    IF EXISTS (
        SELECT * 
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
        WHERE CONSTRAINT_NAME = 'FK__ticket__tc__5535A963' AND DELETE_RULE <> 'SET NULL'
    )
    BEGIN
        -- Drop the existing foreign key constraint on the tc column
        ALTER TABLE ticket
        DROP CONSTRAINT FK__ticket__tc__5535A963;

        -- Add a new foreign key constraint on the tc column with ON DELETE SET NULL
        ALTER TABLE ticket
        ADD CONSTRAINT FK__ticket__tc__5535A963
        FOREIGN KEY (tc) REFERENCES customer(tc) ON DELETE SET NULL;
    END;
END;
"""


createDeletedCustomerTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DeletedCustomerLog')

BEGIN
CREATE TABLE DeletedCustomerLog (
    deletionID INT PRIMARY KEY IDENTITY(1,1),
    tc VARCHAR(11),
    name VARCHAR(50),
    surname VARCHAR(50),
    email VARCHAR(50),
    password VARCHAR(50),
    phone VARCHAR(11),
    customerRoleID TINYINT,
    deletionDate DATETIME DEFAULT GETDATE()
)
END"""

createDeletedTicketLogTableSTR = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DeletedTicketLog')
BEGIN
    CREATE TABLE DeletedTicketLog (
        deletionID INT PRIMARY KEY IDENTITY(1,1),
        ticketID smallint,
        tc VARCHAR(11),
        busID smallint,
        priceID smallint,
        gender VARCHAR(1),
        seat VARCHAR(38),
        ticketDate DATETIME
    )
END;
"""

#------------------------#
createVoyageRouteTriggerSTR = """
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


createCustomerAddTriggerSTR = """
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'customer_add_database')
BEGIN
    EXEC('
        CREATE TRIGGER customer_add_database
        ON customer
        INSTEAD OF INSERT
        AS 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM customer c INNER JOIN inserted i ON c.tc = i.tc)
                AND NOT EXISTS (SELECT 1 FROM customer c INNER JOIN inserted i ON c.email = i.email)
            BEGIN
                INSERT INTO customer (tc, name, surname, email, password, phone, customerRoleID)
                SELECT tc, name, surname, email, password, phone, customerRoleID
                FROM inserted;

                PRINT ''Registration is successful'';
            END
            ELSE
            BEGIN
                IF EXISTS (SELECT 1 FROM customer c INNER JOIN inserted i ON c.tc = i.tc)
                    PRINT ''This TC is already registered. Registration failed.'';
                ELSE
                    PRINT ''This email is already registered. Registration failed'';
            END
        END;
    ');
END;
"""

createLogDeletedCustomerTriggerSTR = """
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'log_deleted_customer')
BEGIN
    EXEC('
        CREATE TRIGGER log_deleted_customer
        ON customer
        AFTER DELETE
        AS
        BEGIN
            SET NOCOUNT ON;

            INSERT INTO DeletedCustomerLog (tc, name, surname, email, password, phone, customerRoleID)
            SELECT tc, name, surname, email, password, phone, customerRoleID
            FROM deleted;
        END;
    ');
END;

"""

createDeleteTicketsOnNullTCTriggerSTR = """
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_delete_tickets_on_null_tc')
BEGIN
    EXEC('
        CREATE TRIGGER tr_delete_tickets_on_null_tc
        ON ticket
        AFTER UPDATE
        AS
        BEGIN
            SET NOCOUNT ON;

            -- Check if the tc column is updated to NULL
            IF UPDATE(tc) AND NOT EXISTS (SELECT 1 FROM inserted WHERE tc IS NOT NULL)
            BEGIN
                -- Delete the ticket with NULL tc
                DELETE FROM ticket
                WHERE tc IS NULL;
            END;
        END;
    ');
END;
"""


createLogDeletedTicketTriggerSTR = """
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'log_deleted_ticket')
BEGIN
    EXEC('
        CREATE TRIGGER log_deleted_ticket
        ON ticket
        AFTER DELETE
        AS
        BEGIN
            SET NOCOUNT ON;

            INSERT INTO DeletedTicketLog (ticketID, tc, busID, priceID, gender, seat, ticketDate)
            SELECT ticketID, tc, busID, priceID, gender, seat, ticketDate
            FROM deleted;
        END;
    ');
END;
"""

#------------------------#
createSPAssignVoyageToBusAndCreateSeatsSTR = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'AssignVoyageToBusAndCreateSeats')
BEGIN
    EXEC('
    CREATE PROCEDURE AssignVoyageToBusAndCreateSeats
    @busID smallint,
    @voyageID tinyint
AS
BEGIN
    DECLARE @firstVoyageRouteID smallint;
    DECLARE @firstDeparturePlatform tinyint;

    -- Get the first voyage route''s ID and departure platform
    SELECT TOP 1 @firstVoyageRouteID = voyageRouteID, @firstDeparturePlatform = r.departurePlatform
    FROM voyage_route vr
    JOIN route r ON vr.routeID = r.routeID
    WHERE vr.voyageID = @voyageID
    ORDER BY vr.sequenceOrder;

    -- Update bus with voyageID, first voyage route ID, and departure platform
    UPDATE bus
    SET voyageID = @voyageID, currentvoyageRoute = @firstVoyageRouteID, platformno = @firstDeparturePlatform
    WHERE busID = @busID;

    -- Get the voyageRouteIDs associated with the voyage
    DECLARE @voyageRouteIDs TABLE (voyageRouteID smallint);

    INSERT INTO @voyageRouteIDs (voyageRouteID)
    SELECT voyageRouteID
    FROM voyage_route
    WHERE voyageID = @voyageID;

    -- Create seats for each voyageRoute
    INSERT INTO bus_seat (busID, seat, reservedvoyageRoute)
    SELECT @busID, REPLICATE(''0'', 10), voyageRouteID
    FROM @voyageRouteIDs;
END
    ');
END;
"""

SP_GetCustomerTickets = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetCustomerTickets')
BEGIN
    EXEC('
    CREATE PROCEDURE SP_GetCustomerTickets
        @tc VARCHAR(11)
    AS
    BEGIN
        SELECT *
        FROM ticket
        WHERE tc = @tc;
    END
    ');
END
"""

SP_GetAllCustomersWithRolesSTR = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetAllCustomersWithRoles')
BEGIN
    EXEC('
    CREATE PROCEDURE SP_GetAllCustomersWithRoles
    AS
    BEGIN
        SELECT c.tc, c.name, c.surname, c.email, c.phone, cr.customerRole
        FROM customer c
        JOIN customer_role cr ON c.customerRoleID = cr.customerRoleID
    END
    ');
END
"""


SP_GetAllRoutesWithCityNamesSTR = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetAllRoutesWithCityNames')
BEGIN
    EXEC('
    CREATE PROCEDURE SP_GetAllRoutesWithCityNames
    AS
    BEGIN
        SELECT r.routeID, c1.cityName, r.departurePlatform, c2.cityName, r.arrivalPlatform, r.estTime
        FROM route r
        JOIN city c1 ON r.departure = c1.cityID
        JOIN city c2 ON r.arrival = c2.cityID
    END
    ');
END
"""

SP_GetAllVoyageRoutesWithSequenceOrdersSTR = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetAllVoyageRoutesWithSequenceOrders')
BEGIN
    EXEC('
    CREATE PROCEDURE SP_GetAllVoyageRoutesWithSequenceOrders
    AS
    BEGIN
        SELECT vr.voyageRouteID, v.voyageDate, v.startTime, v.voyageName,
               dep.cityName AS departureCity, arr.cityName AS arrivalCity, 
               vr.sequenceOrder
        FROM voyage_route vr
        JOIN voyage v ON vr.voyageID = v.voyageID
        JOIN route r ON vr.routeID = r.routeID
        JOIN city dep ON r.departure = dep.cityID
        JOIN city arr ON r.arrival = arr.cityID
    END
    ');
END
"""

SP_GetAllTicketsWithCustomerAndBusInfoSTR = """
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetAllTicketsWithCustomerAndBusInfo')
BEGIN
    EXEC('
    CREATE PROCEDURE SP_GetAllTicketsWithCustomerAndBusInfo
    AS
    BEGIN
        SELECT t.ticketID, c.name, c.surname, b.plate, t.seat, t.seat, t.ticketDate 
        FROM ticket t
        JOIN customer c ON t.tc = c.tc
        JOIN bus b ON t.busID = b.busID
    END
    ');
END
"""
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
INSERT INTO bus (voyageID, plate, platformno, currentvoyageRoute)
SELECT ?, ?, ?, ?
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

checkRegister = """SELECT * FROM customer WHERE tc = ? OR email = ? OR phone = ?
"""

checkLogin = """SELECT * FROM customer WHERE email = ? AND password = ?"""

#------------------------#


table_dict = {
        "customer_role": ["customerRole"],
        "customer": ["tc", "name", "surname", "email", "password", "phone", "customerRoleID"],
        "city": ["cityName"],
        "route": ["departure", "departurePlatform", "arrival", "arrivalPlatform", "estTime"],
        "voyage": ["voyageDate", "startTime", "voyageName"],
        "voyage_route": ["voyageID", "routeID", "sequenceOrder"],
        "bus": ["voyageID", "plate", "seat", "platformno", "currentvoyageRoute"],
        "bus_seat": ["busID", "seat", "reservedvoyageRoute"],
        "price": ["firstCity", "secondCity", "price"],
        "ticket": ["tc", "busID", "priceID", "gender", "seat", "ticketDate"],
        "DeletedCustomerLog": ["tc", "name", "surname", "email", "password", "phone", "customerRoleID", "deletionDate"],
        "DeletedTicketLog": ["ticketID", "tc", "busID", "priceID", "gender", "seat", "ticketDate"]
        }
    
    

deleteOrder = ["ticket", "bus_seat", "bus", "voyage_route", "voyage", "route", "price", "city", "customer", "customer_role"]


class BusCompanyDB:
    def __init__(self) -> None:
        self.con = pyodbc.connect(connStr, autocommit=True)
        self.cur = self.con.cursor()
        self.create_tables()
        self.create_triggers()
        self.create_stored_procedures()

    def create_tables(self):
        self.cur.execute(createCustomerRoleTableSTR)
        self.cur.execute(createCustomerTableSTR)
        self.cur.execute(createCityTableSTR)
        self.cur.execute(createRouteTableSTR)
        self.cur.execute(createVoyageTableSTR)
        self.cur.execute(createVoyageRouteTableSTR)
        self.cur.execute(createBusTableSTR)
        self.cur.execute(createBusSeatTableSTR)
        self.cur.execute(createPriceTableSTR)
        self.cur.execute(createTicketTableSTR)

        self.cur.execute(createDeletedCustomerTableSTR)
        self.cur.execute(createDeletedTicketLogTableSTR)

    def create_triggers(self):
        self.cur.execute(createVoyageRouteTriggerSTR)
        self.cur.execute(createCustomerAddTriggerSTR)

        self.cur.execute(createLogDeletedCustomerTriggerSTR)
        self.cur.execute(createLogDeletedTicketTriggerSTR)

        self.cur.execute(createDeleteTicketsOnNullTCTriggerSTR)


        
    
    def create_stored_procedures(self):
        self.cur.execute(createSPAssignVoyageToBusAndCreateSeatsSTR)
        self.cur.execute(SP_GetCustomerTickets)

        self.cur.execute(SP_GetAllCustomersWithRolesSTR)
        self.cur.execute(SP_GetAllTicketsWithCustomerAndBusInfoSTR)
        self.cur.execute(SP_GetAllRoutesWithCityNamesSTR)
        self.cur.execute(SP_GetAllVoyageRoutesWithSequenceOrdersSTR)
    #------------------------#
    def export_all_tables_to_csv(self, table_dict):
        for table_name, columns in table_dict.items():
            self.export_table_to_csv(table_name, columns)

    def export_table_to_csv(self, table_name, columns):
        export_folder = 'ExportedData'
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        column_names = ", ".join(columns)
        query = f"SELECT {column_names} FROM {table_name}"

        # Execute the query using the cursor
        self.cur.execute(query)

        # Fetch all rows from the query result
        rows = self.cur.fetchall()

        # Get the column names from the cursor description
        columns = [column[0] for column in self.cur.description]

        # Create a DataFrame from the fetched data
        df = pd.DataFrame.from_records(rows, columns=columns)

        # Specify the CSV file path within the ExportedData folder
        csv_path = os.path.join(export_folder, f"{table_name}_table.csv")

        # Export the DataFrame to a CSV file
        df.to_csv(csv_path, index=False)

    def clean_tables(self, table_name):
        for name in table_name:
            clear_query = f"DROP TABLE {name}"
            self.cur.execute(clear_query)
            self.cur.commit()

        self.create_tables()
        table_name = table_name[::-1]

        for name in table_name:
            self.insert_csv_data_into_table(name)

    def insert_csv_data_into_table(self, table_name):
        # Read CSV file into DataFrame
        csv_path = os.path.join('ExportedData', f"{table_name}_table.csv")
        df = pd.read_csv(csv_path)
        # Insert data into the table
        for _, row in df.iterrows():
            # Replace empty strings with None
            row = row.apply(lambda x: None if pd.isna(x) or (isinstance(x, str) and x.strip() == '') else x)

            columns = ', '.join(row.index)
            values = ', '.join([self.format_value(value, df.dtypes[column]) for column, value in row.items()])
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.cur.execute(insert_query)
            self.cur.commit()

    def format_value(self, value, column_type):
        if pd.isna(value):
            return 'NULL'
        elif column_type == 'int64':
            return str(int(value))
        elif column_type == 'float64':
            return str(float(value))
        elif column_type == 'datetime64[ns]':
            return f"'{value}'"
        elif column_type == 'object':
            return f"N'{str(value)}'"  # Use N for Unicode strings
        else:
            return str(value)
    #------------------------#
        
    def take_backup(self):
        self.export_all_tables_to_csv(table_dict)
    
    def return_from_backup(self):
        self.clean_tables(deleteOrder)

    #------------------------#    
    def insert_customer_role(self, customer_role):
        self.cur.execute(insertCustomerRole, (customer_role))
        bc.cur.commit()

    def insert_customer(self, tc, name, surname, email, password, phone, customerRoleID = 1):
        self.cur.execute(insertCustomer, (tc, name, surname, email, password, phone, customerRoleID))
        bc.cur.commit()

    def insert_city(self, city_name):
        self.cur.execute(insertCity, (city_name))
        bc.cur.commit()

    def insert_route(self, departure, departurePlatform, arrival, arrivalPlatform, estTime):
        self.cur.execute(insertRoute, (departure, departurePlatform, arrival, arrivalPlatform, estTime))
        bc.cur.commit()

    def insert_voyage(self, voyageDate, startTime):
        self.cur.execute(insertVoyage, (voyageDate, startTime, voyageDate))
        bc.cur.commit()

    def insert_voyage_route(self, voyageID, routeID, seq):
        self.cur.execute(insertVoyageRoute, (voyageID, routeID, seq))
        bc.cur.commit()

    def insert_bus(self, voyageID, plate, platformno, currentvoyageRoute):
        self.cur.execute(insertBus, (voyageID, plate, platformno, currentvoyageRoute))
        bc.cur.commit()

    def insert_price(self, firstCity, secondCity, price):
        self.cur.execute(insertPrice, (firstCity, secondCity, price))
        bc.cur.commit()

    #------------------------#
        
    def create_ticket(self, tc, busID, priceID, seat, ticketDate ):
        ticketDate = datetime.strptime(ticketDate, '%Y-%m-%d').date()
        self.cur.execute(createTicket, (tc ,busID, priceID,'M', seat, ticketDate))
        self.cur.commit()


    def create_voyage_route(self, voyage_id, route_id):
        sequence_order = self.cur.execute("SELECT MAX(sequenceOrder) FROM voyage_route WHERE voyageID = ?", (voyage_id,)).fetchone()[0]
        seq = sequence_order if sequence_order != None else 0
        self.cur.execute(insertVoyageRoute, (voyage_id, route_id, seq))
        self.cur.commit()

    #------------------------#
        
    def add_bus(self, plate):
        self.cur.execute(insertBus, (None, plate, None, None))
        self.cur.commit()

    #------------------------#
        

    def sp_assign_voyage_to_bus_and_create_seats(self, bus_id, voyage_id):
        self.cur.execute("EXEC AssignVoyageToBusAndCreateSeats ?, ?", (bus_id, voyage_id))
        self.cur.commit()

    #------------------------#

    def check_register(self, tc, email, phone):
        return self.cur.execute(checkRegister, (tc, email, phone)).fetchone()

    def check_login(self, email, password):
        return self.cur.execute(checkLogin, (email, password)).fetchone()

    #------------------------#

    def get_customer_tableSP(self):
        return self.cur.execute("EXEC SP_GetAllCustomersWithRoles").fetchall()
    
    def get_ticket_tableSP(self):
        return self.cur.execute("EXEC SP_GetAllTicketsWithCustomerAndBusInfo").fetchall()
    
    def get_route_tableSP(self):
        return self.cur.execute("EXEC SP_GetAllRoutesWithCityNames").fetchall()
    
    def get_voyageRouteandVoyage_tableSP(self):
        return self.cur.execute("EXEC SP_GetAllVoyageRoutesWithSequenceOrders").fetchall()
    #------------------------#

    def get_tc_with_email(self, email):
        return self.cur.execute("SELECT tc FROM customer WHERE email = ?", (email,)).fetchone()[0]

    def get_cities(self):
        return self.cur.execute("SELECT cityName FROM city").fetchall()
    
    def get_customer_tickets(self, tc):
        return bc.cur.execute("EXEC SP_GetCustomerTickets @tc=?", (tc,)).fetchall()
    
    def get_customer_name(self, tc):
        return self.cur.execute("SELECT name FROM customer WHERE tc = ?", (tc,)).fetchone()[0]

    def get_city_names_with_priceid(self, priceID):
        return [self.cur.execute("SELECT cityName FROM city WHERE cityID = (SELECT firstCity FROM price WHERE priceID = ?)", (priceID,)).fetchone()[0], self.cur.execute("SELECT cityName FROM city WHERE cityID = (SELECT secondCity FROM price WHERE priceID = ?)", (priceID,)).fetchone()[0]]
    
    def get_voyage_start_time(self, bus_id):
        return self.cur.execute("SELECT startTime FROM voyage WHERE voyageID = (SELECT voyageID FROM bus WHERE busID = ?)", (bus_id,)).fetchone()[0]
    
    def get_route_esttime(self, seq):
        return self.cur.execute("SELECT estTime FROM route WHERE routeID = (SELECT routeID FROM voyage_route WHERE voyageRouteID = ?)", (seq,)).fetchone()[0]
    
    def get_suitable_buses(self, from_location, to_location, date):
        # Convert the date string to a datetime object
        date = datetime.strptime(date, '%Y-%m-%d').date()

        # Select buses that have a voyage on the specified date
        query = """
            SELECT b.busID
            FROM bus b
            JOIN voyage v ON b.voyageID = v.voyageID
            JOIN voyage_route vr_from ON v.voyageID = vr_from.voyageID
            JOIN voyage_route vr_to ON v.voyageID = vr_to.voyageID
            JOIN route r_from ON vr_from.routeID = r_from.routeID
            JOIN route r_to ON vr_to.routeID = r_to.routeID
            WHERE r_from.departure = (SELECT cityID FROM city WHERE cityName = ?)
                AND r_to.arrival = (SELECT cityID FROM city WHERE cityName = ?)
                AND v.voyageDate = ?
            ORDER BY vr_from.sequenceOrder;
        """
        # Execute the query with parameters
        result = self.cur.execute(query, (from_location, to_location, date)).fetchall()
        return result

    def get_price_info_with_locs(self, from_location, to_location):
        # Select price information based on the given locations (both directions)
        query = """
            SELECT price
            FROM price
            WHERE (firstCity = (SELECT cityID FROM city WHERE cityName = ?) AND secondCity = (SELECT cityID FROM city WHERE cityName = ?))
               OR (firstCity = (SELECT cityID FROM city WHERE cityName = ?) AND secondCity = (SELECT cityID FROM city WHERE cityName = ?));
        """

        # Execute the query with parameters
        result = self.cur.execute(query, (from_location, to_location, to_location, from_location)).fetchone()

        # Process the result or return it as needed
        return result
    
    def get_price_info_with_priceid(self, priceID):
        # Select price information based on the given locations (both directions)
        query = """
            SELECT price
            FROM price
            WHERE priceID = ?
        """

        # Execute the query with parameters
        result = self.cur.execute(query, (priceID)).fetchone()

        # Process the result or return it as needed
        return result

    def get_price_id(self, from_location, to_location):
        # Select price information based on the given locations (both directions)
        query = """
            SELECT priceID
            FROM price
            WHERE (firstCity = (SELECT cityID FROM city WHERE cityName = ?) AND secondCity = (SELECT cityID FROM city WHERE cityName = ?))
               OR (firstCity = (SELECT cityID FROM city WHERE cityName = ?) AND secondCity = (SELECT cityID FROM city WHERE cityName = ?));
        """

        # Execute the query with parameters
        result = self.cur.execute(query, (from_location, to_location, to_location, from_location)).fetchone()

        # Process the result or return it as needed
        return result

    def get_customer_accompanying_seqs(self, from_location, to_location, bus_id):
        sequences = []
        # Find the voyage_id for the specified bus
        query_voyage = """
            SELECT v.voyageID
            FROM bus b
            JOIN voyage v ON b.voyageID = v.voyageID
            WHERE b.busID = ?
        """

        # Execute the query with parameters
        voyage_id_result = self.cur.execute(query_voyage, (bus_id,)).fetchone()

        if not voyage_id_result:
            print("Bus information not found.")
            return None

        voyage_id = voyage_id_result[0]

        # Get the sequence orders for the specified route
        query_sequence_orders = """
            SELECT vr.sequenceOrder
        FROM voyage_route vr
        JOIN route r_from ON vr.routeID = r_from.routeID
        JOIN city c_from ON r_from.departure = c_from.cityID
        WHERE vr.voyageID = ?
            AND c_from.cityName = ?
        ORDER BY vr.sequenceOrder;


        """

        # Execute the query with parameters
        sequence_orders = self.cur.execute(query_sequence_orders, (voyage_id, from_location)).fetchone()
        sequences.append(sequence_orders)

        query_sequence_orders = """
            SELECT vr.sequenceOrder
            FROM voyage_route vr
            JOIN route r_to ON vr.routeID = r_to.routeID
            JOIN city c_to ON r_to.arrival = c_to.cityID
            WHERE vr.voyageID = (SELECT b.voyageID
                                FROM bus b
                                JOIN voyage v ON b.voyageID = v.voyageID
                                WHERE b.busID = ?)
                AND c_to.cityName = ?
            ORDER BY vr.sequenceOrder;



        """

        # Execute the query with parameters
        sequence_orders = self.cur.execute(query_sequence_orders, (voyage_id, to_location)).fetchone()
        sequences.append(sequence_orders)

        if not sequence_orders:
            print("Route information not found.")
            return None

        return sequences
    
    def set_reserved_seat(self, reservedSequence, reservedSeat, bus_id):
        getOldSeatLayout = """
            SELECT seat
            FROM bus_seat
            WHERE busID = ? AND reservedvoyageRoute = ?
        """

        oldLayout = bc.cur.execute(getOldSeatLayout, (bus_id, reservedSequence)).fetchone()[0]
        newLayout = ""
        for i in range(0, len(oldLayout)):
            if i == int(reservedSeat):
                newLayout += "1"
            else:
                newLayout += oldLayout[i]
        
        updateSeatLayout = """
            UPDATE bus_seat
            SET seat = ?
            WHERE busID = ? AND reservedvoyageRoute = ?
        """
        bc.cur.execute(updateSeatLayout, (newLayout, bus_id, reservedSequence))

        bc.cur.commit()
    
    def get_reserved_seats(self, bus_id, sequences):

        seats = []
        getReservedSeats = """
            SELECT seat
            FROM bus_seat
            WHERE busID = ? AND reservedvoyageRoute = ?
        """
        for seq in sequences:
            seats.append(bc.cur.execute(getReservedSeats, (bus_id, seq)).fetchone()[0])

        reservedSeats = []
        for seat in seats:
            for i in range(0, len(seat)):
                if seat[i] == "1" and i not in reservedSeats:
                    reservedSeats.append(i)

        return reservedSeats
    
    #------------------------#

    def delete_ticket_with_ticket_id(self, ticket_id):
        self.cur.execute("DELETE FROM ticket WHERE ticketID = ?", (ticket_id,))
        self.cur.commit()
    
    def delete_customer_with_tc(self, tc):
        self.cur.execute("DELETE FROM customer WHERE tc = ?", (tc,))
        self.cur.commit()

    def delete_ticket_with_ticketID(self, ticket_id):
        self.cur.execute("DELETE FROM ticket WHERE ticketID = ?", (ticket_id,))
        self.cur.commit()


bc = BusCompanyDB()
bc.cur.commit()
def get_customer_role():
    customer_role = 'normal'
    bc.insert_customer_role(customer_role)
    customer_role = 'admin'
    bc.insert_customer_role(customer_role)


def get_customer():
    tc = 1
    name = 1
    surname = 1
    email = 1
    password = 1
    phone = 1
    customerRoleID = 1
    bc.insert_customer(tc, name, surname, email, password, phone, customerRoleID)

def get_route():
    for i in range(1,5):
        departure = i
        departurePlatform = i
        arrival = i+1
        arrivalPlatform = i+1
        estTime = i+1
        bc.insert_route(departure, departurePlatform, arrival, arrivalPlatform, estTime)

def get_voyage():
    voyageDate = datetime.strptime(input("date seperated with - : "), '%d-%m-%Y').date()
    startTime = input("Enter start time: ")
    bc.insert_voyage(voyageDate, startTime)

def get_voyage_route():
    voyageID = input("Enter voyage ID: ")
    routeID = input("Enter route ID: ")
    bc.insert_voyage_route(voyageID, routeID)

def get_bus():
    voyageRouteID = None
    plate = '123'
    platformno = '1'
    currentCity = '1'
    bc.insert_bus(voyageRouteID, plate, platformno, currentCity)

def get_price():
    firstCity = 1
    secondCity = 2
    price = 200
    bc.insert_price(firstCity, secondCity, price)

def get_ticket():
    busID = input("Enter bus ID: ")
    priceID = input("Enter price ID: ")
    seat = input("Enter seat: ")
    ticketDate = input("Enter ticket date: ")
    bc.create_ticket(busID, priceID, seat, ticketDate)


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


if __name__ == "__main__":
    # get_customer_role()
    # get_customer()
    # city_names_to_insert = ["City1", "City2", "City3", "City4", "City5"]
    # get_city(city_names_to_insert)
    # get_route()
    # get_price()

    # create_voyage()
    # create_voyage_route()

    # bc.add_bus('1')
    # bc.sp_assign_voyage_to_bus_and_create_seats(1, 1)



    


    # return backup delete all tables
    # bc.cur.execute('delete from ticket')
    # bc.cur.execute('delete from bus_seat')
    # bc.cur.execute('delete from bus')
    # bc.cur.execute('delete from customer')
    # bc.cur.execute('delete from customer_role')
    # bc.cur.execute('delete from voyage_route')
    # bc.cur.execute('delete from voyage')
    # bc.cur.execute('delete from price')
    # bc.cur.execute('delete from route')
    # bc.cur.execute('delete from city')

    #
    # print(deleteOrder.reverse())
   
     # Create a folder for storing CSV files
   
    #csv_filename = os.path.join(export_folder, f'{table_name}.csv')
    print(bc.cur.execute("SELECT * FROM bus").fetchall())
    
    # print(table_dict.keys())
    
    # print(bc.cur.execute("SELECT * FROM voyage").fetchall())
    # print(bc.cur.execute("SELECT * FROM customer").fetchall())
    pass

