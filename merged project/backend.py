import busCompanyDB as db

bc = db.BusCompanyDB()

isLogged = False
currentUsersEmail = None

departure = None
arrival = None

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

def get_customer_accompanying_seqs():
    return make_fetchall_list(bc.get_customer_accompanying_seqs("City1", "City2", 1))

def make_fetchall_list(fetchall):
    list = []
    for i in fetchall:
        list.append(i[0])
    return list



if __name__ == "__main__":
    print(get_customer_accompanying_seqs())
