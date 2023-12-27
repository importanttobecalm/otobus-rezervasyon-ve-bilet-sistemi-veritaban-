from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
import busCompanyDB as db

bc = db.BusCompanyDB()

isLogged = False
currentUsersEmail = None

departure = None
arrival = None

selectedDate = None
selectedBus = None
reservedSeats = []

def register_check(tc, name, surname, email, password, phone):
    if bc.check_register(tc, email, phone):
        return False
    else:
        bc.insert_customer(tc, name, surname, email, password, phone)
        bc.cur.commit()
        return True

def login_check(email, password):
    if bc.check_login(email, password):
        global isLogged
        global currentUsersEmail

        isLogged = True
        currentUsersEmail = email
        return True

    else:
        return False

def get_locations():
    return make_fetchall_list(bc.get_cities())

def get_suitable_buses(from_location, to_location, date):
    global departure
    global arrival
    global selectedDate

    selectedDate = date
    departure = from_location
    arrival = to_location
    return make_fetchall_list(bc.get_suitable_buses(from_location, to_location, date))

def get_price_info():
    return bc.get_price_info_with_locs(departure, arrival)[0]

def get_estimated_time(from_location, to_location, bus_id):
    startTimeSTR = bc.get_voyage_start_time(bus_id)
    startTime = datetime.strptime(startTimeSTR, '%H:%M')
    sequences = get_customer_accompanying_seqs(from_location, to_location, bus_id)
    endTime = startTime
    
    for seq in range(1,sequences[0]+1):
        endTime += timedelta(minutes=bc.get_route_esttime(seq))
    endTimeSTR = endTime.strftime('%H:%M')

    if len(sequences) != 1:
        startTimeSTR = endTimeSTR
        for seq in range(sequences[0]+1,sequences[1]+1):
            endTime += timedelta(minutes=bc.get_route_esttime(seq))
        endTimeSTR = endTime.strftime('%H:%M')

    return f"{startTimeSTR} -> {endTimeSTR}"


def get_customer_tableSP():
    return bc.get_customer_tableSP()

def get_ticket_tableSP():
    return bc.get_ticket_tableSP()

def get_route_tableSP():
    return bc.get_route_tableSP()

def get_voyageRouteandVoyage_tableSP():
    return bc.get_voyageRouteandVoyage_tableSP()

def set_selected_bus(bus_id):
    global selectedBus
    selectedBus = bus_id

def set_reserved_seat(seatNo):
    global reservedSeats
    reservedSeats = seatNo.split(',')
    reservedSequences = get_customer_accompanying_seqs(departure, arrival, selectedBus)

    for seq in reservedSequences:
        for seat in reservedSeats:
            bc.set_reserved_seat(seq, seat, selectedBus)


def assign_bus_to_voyage(bus_id, voyage_id):
    bc.sp_assign_voyage_to_bus_and_create_seats(bus_id, voyage_id)

def get_customer_accompanying_seqs(from_location, to_location, bus_id):
    sequences = bc.get_customer_accompanying_seqs(from_location, to_location, bus_id)
    reservedSequences = []
    for i in range(sequences[0][0], sequences[1][0]+1):
        reservedSequences.append(i)

    return reservedSequences

def create_ticket():
    for seat in reservedSeats:
            bc.create_ticket(bc.get_tc_with_email(currentUsersEmail), selectedBus, bc.get_price_id(departure, arrival)[0], seat, ticketDate=selectedDate)

def create_voyage_route(voyageID, routeID):
    bc.create_voyage_route(voyageID, routeID)

def add_bus(plate):
    bc.add_bus(plate)

def get_reserved_seats():
    return bc.get_reserved_seats(selectedBus ,get_customer_accompanying_seqs(departure, arrival, selectedBus))

def customer_tickets_info():
    tickets = []
    
    for ticket in get_customer_tickets():
        name = bc.get_customer_name(ticket[1])
        journal = bc.get_city_names_with_priceid(ticket[3])
        tickets.append({
                        "pnr_no": ticket[0],
                        "seat_no": ticket[5],
                        "passenger_name": name,
                        "departure_time": get_estimated_time(journal[0], journal[1], ticket[2]),
                        "date": ticket[4],
                        'route': f"{journal[0]}->{journal[1]}",
                        'price': bc.get_price_info_with_priceid(ticket[3])[0],
                        'amenities': ['WiFi', 'Ücretsiz Yemek', 'Televizyon'],
                        'bus_info': '1+1 10 seated ultra Luxury Bus'
                        
                        })

    return tickets


def get_customer_tickets():
    tc = bc.get_tc_with_email(currentUsersEmail)
    return bc.get_customer_tickets(tc)


def get_customer_name(email):
    return bc.get_customer_name(bc.get_tc_with_email(email))[0]



def make_fetchall_list(fetchall):
    list = []
    for i in fetchall:
        list.append(i[0])
    return list


def delete_ticket_with_ticket_id(ticket_id):
    bc.delete_ticket_with_ticket_id(ticket_id)


def insert_customer(tc, name, surname, email, password, phone):
    bc.insert_customer(tc, name, surname, email, password, phone)

def create_ticket_admin(tc, bus_id, price_id, seat_no, ticketDate):
    bc.create_ticket(tc, bus_id, price_id, seat_no, ticketDate)

def delete_customer_with_tc(tc):
    bc.delete_customer_with_tc(tc)

def delete_ticket_with_ticketID(ticketID):
    bc.delete_ticket_with_ticketID(ticketID)


def get_tables_pdf(table_name):
    query = f'SELECT * FROM {table_name}'
    cursor = bc.cur
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()

    # Create PDF
    pdf = canvas.Canvas(table_name + '.pdf')
    pdf.drawString(100, 800, "Your PDF Report Title")

    # Add column names
    for i, column in enumerate(columns):
        pdf.drawString(100 + i * 100, 780, column)

    # Add data
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            pdf.drawString(100 + j * 100, 760 - i * 20, str(value))

    pdf.save()




query = 'SELECT * FROM customer'

# Function to generate a PDF report
def generate_pdf_report(query, output_filename):
    cursor = bc.cur
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()

    # Create PDF
    pdf = canvas.Canvas(output_filename)
    pdf.drawString(100, 800, "Your PDF Report Title")

    # Add column names
    for i, column in enumerate(columns):
        pdf.drawString(100 + i * 100, 780, column)

    # Add data
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            pdf.drawString(100 + j * 100, 760 - i * 20, str(value))

    pdf.save()

# Generate PDF report
generate_pdf_report(query, 'output_report.pdf')


















if __name__ == "__main__":
    sequences = bc.get_customer_accompanying_seqs('City2', 'City3', 1)
    reservedSequences = []
    for i in range(sequences[0][0], sequences[1][0]+1):
        reservedSequences.append(i)

    print(reservedSequences)

    print(bc.get_voyage_start_time(1))
