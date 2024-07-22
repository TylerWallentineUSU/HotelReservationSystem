import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

import db_base as db
import csv
import time
import datetime
from SQL_Classes import HotelReservations, HotelRooms, HotelUsers, HotelEmployees


'''
    WELCOME FUNCTION
'''

def WelcomeMessage(sleepTime = 0):
    print("Welcome to the Bonneville Inn!")
    time.sleep(sleepTime)
    print("Renown for our exemplary service, we house guests from all across the world.")
    time.sleep(sleepTime*3)
    print("We would invite you to see our excellence for yourself!")
    time.sleep(sleepTime*5)
    print("We would invite you, first, to create an account or log in.")

'''
    LOGIN FUNCTIONs
'''

def LoginDetails(LoginFile="HotelUsers.sqlite", override=False):
    Directory = os.listdir()
    HotelUserBase = HotelUsers(LoginFile)
    if LoginFile not in Directory or override == True:
        print("Login file not found. Creating file.")
        HotelUserBase.reset_or_create_db()
        print("Loading Default Users.")
        HotelUserBase.read_default_users("DefaultUsers.csv")
        HotelUserBase.save_to_database()
        print("Users are saved to database!")
    return HotelUserBase

def LoginSystem(HotelUserBase):
    AccountCheck = input("Do you have an account? (Y/N): ")
    Username = input("Enter your username: ")
    
    # Account Access
    
    if 'y' in AccountCheck.lower():
        Answer = HotelUserBase.fetch(Username = Username)
        if Answer:
            Password = input("Enter your password: ")
            if Password == Answer[2]:
                print("Welcome,", Username, f"({Answer[3]})")
                return True, Username, Answer[2], Answer[3]
            else:
                for i in range(2):
                    Password = input(f"Passwords do not match. Please try again ({2 - i} tries remaining): ")
                    if Password == Answer[2]:
                        print("Welcome,", Username, f"({Answer[3]})")
                        return True, Username, Answer[2], Answer[3]
                    elif i == 1:
                        print("Maximum number of attempts exceeded. Please contact an administrator for assistance.")
                        return False, Username, "N/A", "N/A"
        else:
            AccountCheck2 = input("User does not exist. Would you like to create an account?")
    
    # Account Creation
    
    if 'n' in AccountCheck.lower() or 'y' in AccountCheck2.lower():
        if HotelUserBase.fetch(Username = Username):
            print(f"User {Username} already exists. Please log in using proper credentials.")
            return False, Username, "N/A", "N/A"
        Email = input("Enter your email: ")
        while "@" not in Email or "." not in Email:
            Email = input("Not a valid email. Please re-enter: ")
        Password = input("Enter your password: ")
        Password2 = input("Confirm your password: ")
        while Password != Password2:
            Password = input("Enter your password: ")
            Password2 = input("Confirm your password: ")
        HotelUserBase.add(Username, Password, Email)
        Answer = HotelUserBase.fetch(Username = Username)
        return True, Username, Answer[2], Answer[3]

def displayDictionaryChoices(dictionary, message="", AdminBlock=[]):
    if len(message) > 0:
        print(message)
    actionOptions = list(dictionary.values())
    actionKeys = list(dictionary.keys())
    for i, action in enumerate(actionOptions):
        print(actionKeys[i], ":", actionOptions[i])
    Choice = input("(Enter one of the above numbers)\n")
    Choice = int(Choice) if Choice.isdigit() else None
    return Choice

def ModifyAccountStatuses(HotelUserBase, RoomTable, ReservationTable, EmployeeTable):
    
    
    roleOptions = {
        1 : "Administrator",
        2 : "User",
        3 : "Employee"
        }
    columnOptions = {
        1 : "ID",
        2 : "Username",
        3 : "Password",
        4 : "Type",
        5 : "Email"
        }
    searchOptions = {
        1 : "Username",
        2 : "Email",
        3 : "Role",
        4 : "ID"
        }
    
    # Search / Filtering
    
    Choice = displayDictionaryChoices(searchOptions, message="Search by...")
    KeyColumn = searchOptions[Choice]
    if Choice == 1:
        KeyValue = input("Enter a username: ")
        Result = HotelUserBase.fetch(Username=KeyValue)
    elif Choice == 2:
        KeyValue = input("Enter an email: ")
        Result = HotelUserBase.fetch(Email=KeyValue)
    elif Choice == 3:
        KeyValue = roleOptions[displayDictionaryChoices(roleOptions)]
        Result = HotelUserBase.fetch(Role=KeyValue)
        ResultDict = {}
        for i, value in enumerate(Result):
            print(f"[{i}] - {value[1]}")
            ResultDict[i] = value[1]
        UserSelected = displayDictionaryChoices(ResultDict, message="Pick a user: ")
        UserSelected = Result[int(UserSelected)][1]
        Result = HotelUserBase.fetch(Username=UserSelected)
        KeyColumn = "Username"
        KeyValue = UserSelected
    elif Choice == 4:
        key = input("Enter an ID: ")
        KeyValue = int(key) if key.isdigit() else key
        Result = HotelUserBase.fetch(ID=int(KeyValue))
    
    AccountDeletion= input("Are you deleting this account? (Y/N): ")
    if 'n' in AccountDeletion.lower():
    
        # Selecting a column to update for selected user
            
        ChangeColumn = displayDictionaryChoices(columnOptions, message="Which metric would you like to update?")
        if ChangeColumn != 4:
            ChangeValue = input(f"Enter a new {columnOptions[ChangeColumn]}: ")
        elif ChangeColumn == 4:
            ChangeValue = roleOptions[displayDictionaryChoices(roleOptions)]
            if ChangeValue == "Employee":
                print("\n--Employee Creation Menu--")
                Username = Result[1]
                Salary = input("Enter a desired salary (float): ")
                Floor_Served = input("Enter a floor served: ")
                Position = input("Enter a position title: ")
                Address = input("Enter an address: ")
                DOB = input("Enter a DOB: ")
                Status = "Active"
                EmployeeTable.add(Username, Salary, Floor_Served, Position, Address, DOB, Status)
            if Result[3] == "Employee" and ChangeValue != "Employee":
                print(f"We are removing {Result[1]} from the employment list.")
                if 'y' in input("Confirm? (Y/N)").lower():
                    EmployeeTable.delete("Username", Result[1])
                
    
        if Result:
            print("KeyColumn =", KeyColumn,"KeyValue =", KeyValue, "ChangeColumn =", columnOptions[ChangeColumn], "ChangeValue =", ChangeValue)
            HotelUserBase.update(KeyColumn = KeyColumn,
                                 KeyValue = KeyValue,
                                 ChangeColumn = columnOptions[ChangeColumn],
                                 ChangeValue = ChangeValue)
    elif 'y' in AccountDeletion.lower():
        Confirm = input(f"Are you sure you want to delete this account ({Result[1]}) ? (Y/N): ")
        if 'y' in Confirm.lower():
            HotelUserBase.delete(Result[1])
            ReservationTable.delete("ResOwner", Result[1])
            EmployeeTable.delete("Username", Result[1])
            
def performSystemReset(HotelUserBase, RoomTable, ReservationTable, EmployeeTable):
    systemResetOptions = {
        1 : "Reset User Base",
        2 : "Clear All Reservations",
        3 : "Reset User Base and Clear All Reservations"
        }
    Choice = displayDictionaryChoices(systemResetOptions)
    Proceed = input("WARNING: Proceeding with this decision will clear all data from the selected datafields, resetting the system element to factory settings! Respond 'CONTINUE' to proceed:\n")
    if Proceed == "CONTINUE":
        if Choice == 1 or Choice == 3:
            HotelUserBase.reset_or_create_db(defaults=True)
        if Choice == 2 or Choice == 3:
            ReservationTable.reset_or_create_db(defaults=True)
            RoomTable.reset_or_create_db(defaults=True)
            EmployeeTable.reset_or_create_db(defaults=True)
    else:
        print("Process aborted.")

def DeleteMyAccount(Username, HotelUserBase, RoomTable, ReservationTable):
    Confirm = input("Are you sure you want to delete your account? (Enter 'CONTINUE' if YES): ")
    if Confirm == "CONTINUE":
        HotelUserBase.delete(Username)
        ReservationTable.update(KeyColumn="ResOwner", KeyValue=Username, ChangeValue="CANCELLED")

def ChangeMyPassword(Username, Password, HotelUserBase, RoomTable, ReservationTable):
    print("Let's change your password!")
    try:
        Password = HotelUserBase.fetch(Username=Username)[2]
    except:
        print(f"The username '{Username}' was unable to be located in the system...")
        return 0
    print(Password)
    PasswordConfirm = input("Please enter your password: ")
    if PasswordConfirm == Password:
        NewPassword = input("Enter your new password: ")
        NewPasswordConfirm = input("Enter your new password again: ")
        if NewPassword == NewPasswordConfirm:

            HotelUserBase.update(KeyValue=Username, ChangeValue=NewPassword)
        else:
            print("Passwords do not match. Exiting.")
    else:
        print("Wrong password. Exiting.")

ReservationCriteria = {
    1 : "View All Available Rooms",
    2 : "Filter By Price",
    3 : "Filter by Tier (Quality)",
    4 : "Filter by Number of Guests",
    5 : "Filter by Floor",
    6 : "Filter by Room Name"
    }


def generate_date_range(start_date, end_date):

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    delta = (end_date - start_date).days

    date_list = [start_date + datetime.timedelta(days=i) for i in range(delta + 1)]

    return date_list

def printRooms(Rooms):
    Dict = {}
    for i, room in enumerate(Rooms):
        Dict[room[0]] = f"{room[2]} \n\tNUMBER: {room[3]} \n\tCOST PER NIGHT: {room[5]} \n\tMAXIMUM GUESTS: {room[6]}"
    return Dict

def read_reservations(file_path):
    lines = []
    reserved_dates = []
    reserved_room = []
    reserve_number = []
    reserved_owner = []
    reserved_statuses = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            lines.append(row)
            reserved_room.append(row[0])
            reserve_number.append(row[1])
            reserved_owner.append(row[2])
            reserved_dates.append(row[4])
            reserved_statuses.append(row[5])

    return reserved_room, reserve_number, reserved_owner, reserved_dates, reserved_statuses

def write_reservations(file_path, row):
    try:
        with open(file_path, mode='a', newline='\n') as file:
            writer = csv.writer(file)
            writer.writerows([row])
    except Exception as e:
        print(f"An error occurred while saving reservation: {e}")

def getUnavailable(date_list, Rooms, Number, Owner, Dates, Statuses, RoomTable, prints=False):
    Unavailable = []
    for i, room in enumerate(Rooms):

        Date = datetime.datetime.strptime(Dates[i], "%m/%d/%Y")
        if Date in date_list and room not in Unavailable and Statuses[i] == "ACTIVE":
            Unavailable.append(room)
    if prints and len(Unavailable) > 0:
        print("The following rooms are unavailable during this time:")
        for i, room in enumerate(Unavailable):
            print(i, "\t", room)
    AvailableRooms = RoomTable.fetchall(Status="AVAILABLE")
    for i, room in enumerate(AvailableRooms):
        Unavailable.append(room[0])
        print(room[0], "is unavailable")
    return Unavailable

def getRoomDataByIndex(Rooms, Number, Index):
    for i, room in enumerate(Rooms):
        if room[0] == Number:
            return room[Index]

def ReservationConfirmation(ID, date_list, Name, Number, DailyCost, Cost, Username, Guests, Butler):
    print("\n-------------------------\nReservation Confirmation:")
    print("ID: \t\t\t{:07d}".format(ID))
    print(f"Room Name: \t\t{Name}")
    print(f"Account: \t\t{Username}")
    print(f"Guests: \t\t{Guests}")
    print(f"Butler: \t\t{Butler}")
    print(f"Check in: \t\t{date_list[0]}")
    print(f"Check out: \t\t{date_list[-1]} ({len(date_list)}-day stay)")
    print(f"Cost Per Day: \t{DailyCost}")
    print(f"Base Total: \t{Cost}")

def GetAvailableButlers(ButlerList, EmployeeTable):
    
    def is_tuple(variable):
        return isinstance(variable, (tuple))
    if is_tuple(ButlerList):
        ButlerList = [ButlerList]
    Available = []
    for Butler in ButlerList:
        if Butler[7] == "Active":
            Available.append(Butler)
    # If butlers for a floor aren't available, escalate to all butlers
    if len(Available) == 0:
        ButlerList = EmployeeTable.fetch(Position="Butler", FetchAll=True)
        for Butler in ButlerList:
            if Butler[7] == "Active":
                Available.append(Butler)
    # If no butlers are available, escalate to management
    if len(Available) == 0:
        ButlerList = EmployeeTable.fetch(Position="Manager", FetchAll=True)
        for Butler in ButlerList:
            if Butler[7] == "Active":
                Available.append(Butler)
    return Available

        

def MakeReservation(Username, Password, HotelUserBase, RoomTable, ReservationTable, EmployeeTable):
    import random
    print("Let's make a reservation.")
    print("What dates are you interested in staying?")

    # Prompt user for desired date(s) of stay
    check_in_date = datetime.datetime.strptime(input("Enter a check-in date (MM/DD/YYYY): "), "%m/%d/%Y")
    check_out_date = datetime.datetime.strptime(input("Enter a check-out date (MM/DD/YYYY): "), "%m/%d/%Y")
    #check_in_date = datetime.datetime.strptime("7/21/2024", "%m/%d/%Y")
    #check_out_date = datetime.datetime.strptime("7/21/2024", "%m/%d/%Y")
    date_list = generate_date_range(check_in_date, check_out_date)

    # Check AllReservations.csv to first see which rooms are unavailable during the selected range

    TakenRooms, TakenNumber, TakenOwner, TakenDates, TakenStatuses, TakenGuests = ReservationTable.taken()

    ReservationNumber = int(max(TakenNumber)) + 1
    UnavailableRooms = getUnavailable(date_list, TakenRooms, TakenNumber, TakenOwner, TakenDates, TakenStatuses, RoomTable)

    # Prompt the user on how to search for rooms (they will select a filter or choose to view all for the time range selected)

    Choice = displayDictionaryChoices(ReservationCriteria)
    print(ReservationCriteria[Choice])
    Rooms = None

    # Based off of the user's choice, filter using SQL from the existing rooms database
    RangeChoices = [2, 3, 4, 5]

    if Choice in RangeChoices:

        ChoiceType = {2 : "Price", 3 : "Tier", 4 : "Guests", 5 : "Floor"}
        print("Enter 'NA' to ignore one value or the other")
        Min = input(f"Enter minimum {ChoiceType[Choice]} Value: ")
        Max = input(f"Enter maximum {ChoiceType[Choice]} Value: ")
        if Min.isdecimal() and Max.isdecimal():
            Min, Max = int(Min), int(Max)
            Crit = (Min, Max)
            Limit = None
        elif Max.isdecimal():
            Crit = int(Max)
            Limit = "<="
        elif Min.isdecimal():
            Crit = int(Min)
            Limit = ">="

    if Choice == 1: # If the user wants to view all available rooms
        Rooms = RoomTable.fetch(check_in_date, check_out_date, Unavailable=UnavailableRooms)
    elif Choice == 2: # If the user wants to view rooms by price
        Rooms = RoomTable.fetch(check_in_date, check_out_date, Cost=Crit, Unavailable=UnavailableRooms, limit=Limit)
    elif Choice == 3: # If the user wants to view rooms by tier (correlated with price so this is a little unnecessary)
        Rooms = RoomTable.fetch(check_in_date, check_out_date, RoomTier=Crit, Unavailable=UnavailableRooms, limit=Limit)
    elif Choice == 4: # If the user wants to view by number of guests
        Rooms = RoomTable.fetch(check_in_date, check_out_date, Guests=Crit, Unavailable=UnavailableRooms, limit=Limit)
    elif Choice == 5: # if the user wants to view by floor
        Rooms = RoomTable.fetch(check_in_date, check_out_date, Floor=Crit, Unavailable=UnavailableRooms, limit=Limit)
    elif Choice == 6: # if the user wants to view by room name
        Rooms = RoomTable.fetch(check_in_date, check_out_date, Unavailable=UnavailableRooms)
        RoomDict = {}
        RoomNames = []
        n = 1
        for i in range(len(Rooms)):

            if Rooms[i][2] not in RoomNames:

                RoomDict[n] = Rooms[i][2]
                RoomNames.append(Rooms[i][2])
                n += 1
        RoomNameChoice = displayDictionaryChoices(RoomDict)
        Rooms = RoomTable.fetch(check_in_date, check_out_date, RoomName=RoomDict[RoomNameChoice], Unavailable=UnavailableRooms)
    if Rooms:
        RoomChoiceDict = printRooms(Rooms)
        print(f"There are {len(list(RoomChoiceDict.keys()))} Options")
        RoomSelection = displayDictionaryChoices(RoomChoiceDict)
        if RoomSelection not in RoomChoiceDict.keys():
            error = f"{RoomSelection} is not available during the selected date range!"
            return error
    else:
        print("Your search returned no results...")

    DailyCost = getRoomDataByIndex(Rooms, RoomSelection, 5)
    Name = getRoomDataByIndex(Rooms, RoomSelection, 2)
    Floor = getRoomDataByIndex(Rooms, RoomSelection, 1)
    
    Number = getRoomDataByIndex(Rooms, RoomSelection, 3)
    MaxGuests = getRoomDataByIndex(Rooms, RoomSelection, 6)
    Cost = DailyCost*len(date_list)
    Desired_Guests = input(f"How many guests? (Max. = {MaxGuests}): ")
    if Desired_Guests.isnumeric():
        if int(Desired_Guests) > int(MaxGuests):
            error = f"This room cannot support {Desired_Guests} number of guests! Please make separate reservations or reduce party size."
            return error
    else:
        error = f"Please enter a valid number."
        return error

    Butlers = GetAvailableButlers(EmployeeTable.fetch(Floor=Floor), EmployeeTable)
    if len(Butlers) > 0:
        Butler = Butlers[random.randint(0, len(Butlers)-1)]
        ButlerName = Butler[1]
    else:
        print("Cannot find a butler for the assigned reservation. Please call maanagement for special arrangements.")
        ButlerName = "Default"
        
    print(ButlerName)
    print(f"You selected {Name} (RM {Number})")
    print("This has a nightly cost of: ${:.2f}".format(DailyCost))
    print(f"For a {len(date_list)}-night stay this amounts to a total of "+"${:.2f}".format(Cost) + ", not including additional charges incurred by room service, damage, special services, etc.")
    Confirm = input("Confirm Reservation? (Y/N): ")
    if 'y' in Confirm.lower():
        ReservationConfirmation(ReservationNumber, date_list, Name, Number, DailyCost, Cost, Username, Desired_Guests, ButlerName)
        for i, date in enumerate(date_list):
            ReservationTable.add(RoomSelection, ReservationNumber, Username, Desired_Guests, date.strftime("%m/%d/%Y"), "ACTIVE", ButlerName)

class Reservation():
    def __init__(self, start, end, ID, RoomNumber, Owner):
        self.check_in = start
        self.check_out = end
        self.ID = ID
        self.room_number = RoomNumber
        self.owner = Owner
    def update_checkincheckout(self, check_in, check_out):
        if check_in < self.check_in:
            self.check_in = check_in
        if check_out > self.check_out:
            self.check_out = check_out
    def info(self, index=None):
        if index != None:
            print(f"[{index}]", "\t", "{:03d}".format(int(self.room_number)), "\t",self.owner, "\t",self.check_in, "\t",self.check_out)
        else:
            print("{:07d}".format(int(self.ID)), "\t", "{:03d}".format(int(self.room_number)), "\t",self.owner, "\t",self.check_in, "\t",self.check_out)
        return self.ID, self.room_number, self.owner, self.check_in, self.check_out

def PullReservations(Username, ReservationTable, pullAll=False, show=True):
    print("-------------------YOUR RESERVATIONS-------------------")
    reserved_room, reserve_number, reserved_owner, reserved_dates, reserved_statuses, reserved_guests = ReservationTable.taken()

    unique_IDs = []
    for i, ID in enumerate(reserve_number):
        if ID not in unique_IDs:
            if (pullAll or reserved_owner[i] == Username) and reserved_statuses[i] == "ACTIVE":
                unique_IDs.append(ID)
    Reservations = []

    print("ID","\t\t\tRoom", "\tUsername", "\t\t\tCheck-In","\t\t\t\tCheck-Out")
    for i, reservation_ID in enumerate(unique_IDs):
        index = reserve_number.index(reservation_ID)
        date = datetime.datetime.strptime(reserved_dates[index], "%m/%d/%Y")
        instance = Reservation(date, date, reserve_number[index], reserved_room[index], reserved_owner[index])
        for j, res in enumerate(reserve_number):
            if reserve_number[j] == reservation_ID:
                date = datetime.datetime.strptime(reserved_dates[j], "%m/%d/%Y")
                instance.update_checkincheckout(date, date)
        if show:
            instance.info()
        Reservations.append(instance)
    print("--------------------------------------------------------")
    return Reservations

def disableReservations(file_path, X, col=1):
    lines = []

    # Read the CSV file and update the row if necessary
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header
        for row in reader:
            if row[col] == X:
                row[5] = "CANCELLED"
            lines.append(row)

    # Write the updated rows back to the CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header back
        writer.writerows(lines)  # Write the updated rows
    print(f"Successfully Disabled Reservation {X}")
    return 0

def DeleteReservations(Username, ReservationTable, pullAll=False):
    print("-------------------DELETING RESERVATIONS MENU-------------------")
    Reservations = PullReservations(Username, ReservationTable, show=False, pullAll=pullAll)
    ResNumbers = {}
    CheckIn, CheckOut, Rooms = [], [], []
    n = len(Reservations)
    for i, Res in enumerate(Reservations):
        ID, room_number, owner, check_in, check_out = Res.info(index=i)
        ResNumbers[i] = ID
        CheckIn.append(check_in)
        CheckOut.append(check_out)
        Rooms.append(room_number)
    j = input("Select one of the above reservations for deletion by entering its corresponding number option: ")
    j = int(j) if j.isnumeric() else None
    if j == None or j >= n:
        return "Invalid input: Selection must be an integer in the approved range ({0}-{n})!"
    confirm = input(f"Delete reservation {j} for room {Rooms[j]}, scheduled from {CheckIn[j]} to {CheckOut[j]}? \n(Y/N): ")
    if 'y' in confirm.lower():
        ReservationTable.update(ResNumbers[j], "CANCELLED")
    print("-----------------------------------------------------------------")



def ModifyReservations(HotelUserBase, RoomTable, ReservationTable):
    actionOptions = {
        1 : "Delete a reservation",
        2 : "Edit Reservation Information",
        3 : "Change Room Statuses"
        }
    actionKeys = {
        1 : "ID",
        2 : "RoomNumber",
        3 : "ResNumber",
        4 : "Resowner",
        5 : "ResGuests",
        6 : "ResDate",
        7 : "ResStatus"
        }
    statuses = {
        1 : "ACTIVE",
        2 : "CANCELLED",
        3 : "MOVED"
        }
    Choice = displayDictionaryChoices(actionOptions)
    if Choice == 1:
        DeleteReservations("", ReservationTable, pullAll=True)
    elif Choice == 2:
        taken = ReservationTable.fetch()
        print("\t Res#\t Rm#\t User\t Date\t Status")
        for i, line in enumerate(taken):
            print(f"[{i}]\t\t {line[2]}\t {line[3]}\t {line[5]}\t {line[6]}")
        selected = input("Select an entry to update: ")
        actionKey = displayDictionaryChoices(actionKeys)
        if actionKey in [1, 2, 3, 5]:
            value = int(input("Please enter a number: "))
        elif actionKey in [4]:
            users = HotelUserBase.fetch()
            for i, user in enumerate(users):

                print(f"[{i}]", user)
            print(len(taken))
            value = input("Please select a user: ")
            if value.isdecimal():
                value = int(value)

                value = users[value][1]

            else:
                return "Please input an integer next time :("
        elif actionKey in [7]:
            choice = displayDictionaryChoices(statuses)
            value = statuses[choice]
        elif actionKey in [6]:
            date = datetime.datetime.strptime(input("Enter a check-out date (MM/DD/YYYY): "), "%m/%d/%Y")
            value = date.strftime("%m/%d/%Y")

        if selected.isdecimal():
            selected = int(selected)
            ID = taken[selected][0]
            ReservationTable.update(KeyValue=ID, ChangeValue=value, KeyColumn="ID", ChangeColumn=actionKeys[actionKey])
    elif Choice == 3:
        roomStatuses = {1 : "AVAILABLE", 2 : "CLOSED", 3 : "DESTROYED"}
        print("Please select a room:")
        Rooms = RoomTable.fetchall()
        for i, Room in enumerate(Rooms):
            print(f"[{i}]", Room[2] + f"({Room[3]}) [{Room[-1]}]")
        roomChoice = int(input("Enter an integer from the table above: "))
        roomChoice = Rooms[roomChoice][0]
        
        choice = displayDictionaryChoices(roomStatuses)
        choice = roomStatuses[choice]
        
        RoomTable.update(KeyValue=roomChoice, ChangeValue=choice)
        

# Start of Modifying Employment
def ModifyEmployment(HotelUserBase, EmployeeTable):
    print("-------------------EMPLOYMENT MENU-------------------")
    taken = EmployeeTable.fetch()
    print("\t EmployeeID\t Username\t Salary\t Floor_Served\t Position\t DOB\t Status")
    for i, line in enumerate(taken):
        print(f"[{i}]\t\t {line[0]}\t {line[1]}\t {line[2]}\t {line[3]} \t {line[4]} \t {line[5]} \t {line[6]}")
    choice = input("Enter the bracketed [number] of the employee you would like to modify: ")
    try:
        index = int(choice)
        if index < 0 or index >= len(taken):
            raise ValueError("Please enter a valid employee number. ")
        username = taken[index][1]
        field = input("Enter the field you want to modify (Username, Salary, Floor_Served, Position, Status): ").upper()
        modified_value = input(f"Enter the new value for {field}: ")

        updateDB = f"UPDATE {EmployeeTable} SET {field} = ? WHERE Username = ?"
        EmployeeTable.update(KeyValue=username, ChangeValue=modified_value, KeyColumn="Username", ChangeColumn=field)
    except Exception as e:
        print(e)


def ActionMenuDisplay(Username, Password, Role, HotelUserBase, RoomTable, ReservationTable, EmployeeTable):
    actionOptions = {
        1 : "Make a reservation.",
        2 : "See current reservations.",
        3 : "Cancel a reservation.",
        4 : "Change my password.",
        5 : "Delete my account"
        }

    if Role == "Employee" or Role == "Administrator":
        actionOptions[6] = "(Employees) Modify Reservation Information"
        if Role == "Administrator":
            actionOptions[7] = "(Admin) Modify Salary or Other Employment Information"

            actionOptions[8] = "(Admin) Modify account statuses"
            actionOptions[9] = "(Admin) Perform system reset"
    actionOptions[0] = "Log Out"
    while True:
        Choice = displayDictionaryChoices(actionOptions)
        if Choice == 1:
            MakeReservation(Username, Password, HotelUserBase, RoomTable, ReservationTable, EmployeeTable)
        if Choice == 2:
            PullReservations(Username, ReservationTable)
        if Choice == 3:
            DeleteReservations(Username, ReservationTable)
        if Choice == 4:
            ChangeMyPassword(Username, Password, HotelUserBase, RoomTable, ReservationTable)
        if Choice == 5:
            Confirmed = DeleteMyAccount(Username, HotelUserBase, RoomTable, ReservationTable)
            if Confirmed:
                break
        if Choice == 6 and (Role == "Administrator" or Role == "Employee"):
            ModifyReservations(HotelUserBase, RoomTable, ReservationTable)
        if Choice == 7 and (Role == "Administrator"):
            ModifyEmployment(HotelUserBase, EmployeeTable) # Change to modify Employee
        if Choice == 8 and Role == "Administrator":
            ModifyAccountStatuses(HotelUserBase, RoomTable, ReservationTable, EmployeeTable)
        elif Choice == 9 and Role == "Administrator":
            performSystemReset(HotelUserBase, RoomTable, ReservationTable, EmployeeTable)
        elif (Choice == 7 or Choice == 8 or Choice == 9) and Role != "Administrator":
            print("You are not an administrator!")
        elif Choice == 0:
            print("Logging Out!")
            break

def system_hard_reset():
    HotelUserBase = HotelUsers("Hotel.sqlite")
    HotelUserBase.reset_or_create_db()
    RoomTable.reset_or_create_db()
    ReservationTable.reset_or_create_db()
    EmployeeTable.reset_or_create_db()





RoomTable = HotelRooms("Hotel.sqlite")
HotelUserBase = LoginDetails("Hotel.sqlite")
ReservationTable = HotelReservations("Hotel.sqlite")
EmployeeTable = HotelEmployees("Hotel.sqlite")


Admitted, Username, Password, Role = LoginSystem(HotelUserBase)
#Admitted, Username, Password, Role = True, "TylerWallentine", "Password1", "Administrator"
if Admitted:
    ActionMenuDisplay(Username, Password, Role, HotelUserBase, RoomTable, ReservationTable, EmployeeTable)

