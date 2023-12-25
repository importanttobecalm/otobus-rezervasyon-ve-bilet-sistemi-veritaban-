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
    return bc.get_price_info(departure, arrival)[0]

def set_selected_bus(bus_id):
    global selectedBus
    selectedBus = bus_id

def set_reserved_seat(seatNo):
    global reservedSeats
    reservedSeats = seatNo.split(',')
    reservedSequences = get_customer_accompanying_seqs()

    for seq in reservedSequences:
        for seat in reservedSeats:
            bc.set_reserved_seat(seq, seat, selectedBus)

def get_customer_accompanying_seqs():
    sequences = bc.get_customer_accompanying_seqs("City1", "City2", 1)
    reservedSequences = []
    for i in range(sequences[0][0], sequences[1][0]+1):
        reservedSequences.append(i)

    return reservedSequences

def create_ticket():
    for seat in reservedSeats:
            bc.create_ticket(bc.get_tc_with_email(currentUsersEmail), selectedBus, bc.get_price_id(departure, arrival)[0], seat, ticketDate=selectedDate)

def get_reserved_seats():
    return bc.get_reserved_seats(selectedBus ,get_customer_accompanying_seqs())

def customer_tickets_info():
    tickets = []

    for ticket in get_customer_tickets():
        name = bc.get_customer_name(ticket[1])
        tickets.append({
                        "pnr_no": ticket[0],
                        "seat_no": ticket[5],
                        "passenger_name": name,
                        "departure_time": '00:00 -> 03:00',
                        "date": ticket[4],
                        'route': f"{departure}->{arrival}",
                        'price': get_price_info(),
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



if __name__ == "__main__":
    print(bc.cur.execute("SELECT * FROM ticket").fetchall())
