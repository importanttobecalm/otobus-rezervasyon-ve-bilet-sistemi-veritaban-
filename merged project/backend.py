import busCompanyDB as db

bc = db.BusCompanyDB()
isLogged = False
currentUsersEmail = None
def register_check(tc, name, surname, email, password, phone):
    if bc.check_register(tc, email, phone):
        return False
    else:
        bc.insert_customer(tc, name, surname, email, password, phone)
        return True

def login_check(email, password):
    if bc.check_login(email, password):
        isLogged = True
        currentUsersEmail = email
        return True
        
    else:
        return False

def get_locations():
    return make_fetchall_list(bc.get_cities())

def make_fetchall_list(fetchall):
    list = []
    for i in fetchall:
        list.append(i[0])
    return list

if __name__ == "__main__":
    print(get_locations)
