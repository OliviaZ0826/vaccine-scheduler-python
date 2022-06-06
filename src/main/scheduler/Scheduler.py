from doctest import Example
from setuptools import find_namespace_packages
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1].lower()
    password = tokens[2]
    
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    # check3: check strong password
    if not check_password(password):
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1].lower()
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check3: check strong password
    if not check_password(password):
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1].lower()
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient



def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1].lower()
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    # check the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check if logged in
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    date = tokens[1].lower()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    get_username = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(get_username, d)
        for row in cursor:
            print(row[0])
    except pymssql.Error as e:
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please try again!")
        return
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()

    conn = cm.create_connection()
    cursor = conn.cursor()

    get_vaccine = "SELECT Name, Doses FROM Vaccines"
    try:
        cursor.execute(get_vaccine)
        print('%-15s' %  "Vaccine", '%-15s' % "Doses")
        for row in cursor:
            print('%-15s' % row[0], '%-15s' % row[1])
    except pymssql.Error as e:
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()


def reserve(tokens):
    """
    TODO: Part 2
    """
    # check if logged in
    global current_caregiver
    global current_patient
    if current_patient is None:
        print("Please login first!")
        return
    elif current_caregiver is not None:
        print("Please login as a patient!")
        return 
    
    # check: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1].lower()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    get_caregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY Username ASC"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(get_caregiver, d)
        if cursor.rowcount == 0:
            print("No Caregiver is avaible!")
            return
        for row in cursor:
            caregiver = row[0]
    except ValueError:
        print("Please try again!")
        return
    except pymssql.Error as e:
        print("TOP 1")
        print("Db-Error:", e)
        quit()
    except Exception:
        print("Please try again!")
        return
    finally:
        cm.close_connection()

    vaccine_name = tokens[2].lower()
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, 0).get()
    except pymssql.Error as e:
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    
    if vaccine is None:
        print("No such vaccine exist!")
        return
    if vaccine.get_available_doses() == 0:
        print("Not enough available doses!")
        return

    conn = cm.create_connection()
    cursor = conn.cursor()
    remove_row = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    try:
        cursor.execute(remove_row, (d, caregiver))
        conn.commit()
    except pymssql.Error as e:
        print("DELETE")
        print("Eb-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()

    id = random.randint(10000, 99999)
    check_duplicate_id = "SELECT * FROM Appointment WHERE Appt_ID = %d"
    count = 0
    while count == 0:
        conn = cm.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(check_duplicate_id, id)
            if cursor.rowcount == 0:
                count = 1
            else:
                id = random.randint(10000, 99999)
        except pymssql.Error as e:
            print("ID")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error:", e)
            print("Please try again!")
            return
        finally:
            cm.close_connection()

    conn = cm.create_connection()
    cursor = conn.cursor()

    add_row = "INSERT INTO Appointment VALUES (%d, %s, %s, %s, %s)"
    try:
        cursor.execute(add_row, (id, current_patient.get_username(), d, caregiver, vaccine.get_vaccine_name()))
        conn.commit()
    except pymssql.Error as e:
        print("INSERT")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()

    vaccine.decrease_available_doses(1)
    
    print("Appointment ID:", id, "Caregiver username:", caregiver)


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1].lower()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1].lower()
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    # check if logged in
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    if current_caregiver is not None:
        show_appointment = "SELECT Appt_ID, Vaccine, Time, Patient FROM Appointment WHERE Caregiver = %s ORDER BY Appt_ID"
        title = ("Appintment ID", "Vaccine", "Time", "Patient")
        user = current_caregiver
    else:
        show_appointment = "SELECT Appt_ID, Vaccine, Time, Caregiver FROM Appointment WHERE Patient = %s ORDER BY Appt_ID"
        title = ("Appintment ID", "Vaccine", "Time", "Caregiver")
        user = current_patient

    try:
        cursor.execute(show_appointment, user.get_username())
        print('%-15s' % title[0], '%-15s' % title[1], '%-15s' % title[2], '%-15s' % title[3])
        for row in cursor:
            print('%-15s' % row[0], '%-15s' % row[1], '%-15s' % row[2], '%-15s' % row[3])
    except pymssql.Error as e:
        print("De-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    try:
        if current_caregiver is not None:
            current_caregiver = None
        else:
            current_patient = None
        print("Successfully logged out!")
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return


def check_password(password):
    if len(password) < 8:
        print("Password at least 8 characters!")
        return False

    num_upper = 0
    num_lower = 0
    num_number = 0
    num_special = 0
    for c in password:
        if c.islower():
            num_lower+=1
        if c.isupper():
            num_upper+=1
        if c.isdigit():
            num_number+=1
        if c in '!@?#':
            num_special+=1
        
    if num_upper == 0 or num_lower == 0:
        print("Password should contain both upper and lower case!")
        return False
    if num_number == 0:
        print("Password should contain both numbers and letters")
        return False
    if num_special == 0:
        print("Password should contain at least one from !, @, #, ?")
        return False

    return True
    

def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
