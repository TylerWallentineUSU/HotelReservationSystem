import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

import db_base as db
import csv
import time
import datetime 

class UserData:
    def __init__(self, row):
        self.Username = row[1]
        self.Password = row[2]
        self.Type = row[3]
        self.Email = row[4]
        

class ReservationData:
    def __init__(self, row):
        self.RoomNumber = row[0]
        self.Resnumber = row[1]
        self.ResOwner = row[2]
        self.ResGuests = row[3]
        self.ResDate = row[4]
        self.ResStatus = row[5]
        self.Butler = "Default"
    
class RoomData:
    def __init__(self, row):
        self.Floor = row[1]
        self.RoomName = row[2]
        self.RmNo = row[3]
        self.RoomTier = row[4]
        self.CostPerNight = row[5]
        self.MaxGuests = row[6]
        self.Status = row[7]

class EmployeeData:
    def __init__(self, row):
        self.ID = row[0]
        self.Username = row[1]
        self.Salary = row[2]
        self.Floor_Served = row[3]
        self.Position = row[4]
        self.Address = row[5]
        self.DOB = row[6]
        self.Status = row[7]


class HotelReservations(db.DBbase):
    def reset_or_create_db(self, defaults=True):
        try:
            sql = """
                DROP TABLE IF EXISTS HotelReservations;
                CREATE TABLE HotelReservations (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RoomNumber INTEGER,
                    ResNumber INTEGER,
                    ResOwner TEXT,
                    ResGuests INTEGER,
                    ResDate DATE,
                    ResStatus TEXT,
                    Butler TEXT
                );
            """
            super().execute_script(sql)
            if defaults==True:
                self.load_default_reservations("DefaultReservations.csv")
                self.save_to_database()
        except Exception as e:
            print(e)
    def load_default_reservations(self, file_name):
        self.default_ress = []
        try:
            with open(file_name, 'r') as record:
                csv_contents = csv.reader(record)
                next(csv_contents)
                for i, row in enumerate(csv_contents):
                    Res = ReservationData(row)
                    self.default_ress.append(Res)
        except Exception as e:
            print(e)
    def save_to_database(self):
        #print("Number of records to save: ", len(self.default_users))
        save = 'y' if True else input("Continue? ").lower()
        if save == "y":
            for item in self.default_ress:
                try:
                    super().get_cursor.execute("""INSERT INTO HotelReservations
                    (RoomNumber, Resnumber, ResOwner, ResGuests, ResDate, ResStatus, Butler)
                        VALUES(?,?,?,?,?,?,?)""", 
                        (item.RoomNumber, item.Resnumber, item.ResOwner, item.ResGuests, item.ResDate, item.ResStatus, item.Butler))
                    super().get_connection.commit()
                except Exception as e:
                    print(e)
        else:
            print("Save to DB aborted.")
    def delete(self, key, value):
        try:
            super().get_cursor.execute(f"DELETE FROM HotelReservations where {key} = ?;", (value,))
            super().get_connection.commit()
            print(f"Deleted instances where {key} = {value} successfully")
            return True
        except Exception as e:
            print("Error:", e)
            return False
    def update(self, KeyValue="", ChangeValue="", KeyColumn="ResNumber", ChangeColumn="ResStatus"):
        # Update HotelUsers set [NewMetric] = "NewValue" where [TargetMetric] = "TargetValue"
        # Update HotelUsers set [Type] = "Administrator" where [Username] = "TargetValue"
        try:
            query = f"UPDATE HotelReservations SET {ChangeColumn} = ? WHERE {KeyColumn} = ?;"

            print(query, "TargetValue = ", ChangeValue, "; KeyValue = ", KeyValue)
            super().get_cursor.execute(query, (ChangeValue, KeyValue))
            super().get_connection.commit()
            print(f"Updated record to {ChangeValue} successfully")
        except Exception as e:
            print("An error has occurred.", e)
            
    def fetch(self, ID=None, ResNumber=None, ResOwner=None, RoomNumber=None, ResGuests=None, ResStatus=None):
        try:
            if ResNumber is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE ResNumber = ?", (ResNumber,)).fetchall()
            elif ID is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE ID = ?", (ID,)).fetchone()
            elif ResOwner is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE ResOwner = ?", (ResOwner,)).fetchall()
            elif RoomNumber is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE RoomNumber = ?", (RoomNumber,)).fetchall()
            elif ResGuests is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE ResGuests = ?", (ResGuests,)).fetchall()
            elif ResStatus is not None:
                return super().get_cursor.execute("SELECT * FROM HotelReservations WHERE ResStatus = ?", (ResStatus,)).fetchall()
            else:
                return super().get_cursor.execute("SELECT * FROM HotelReservations").fetchall()
        except Exception as e:
            print("An error has occurred.", e)
            
    def add(self, RoomNumber, Resnumber, ResOwner, ResGuests, ResDate, ResStatus, Butler):
        try:
            super().get_cursor.execute("insert or ignore into HotelReservations (RoomNumber, Resnumber, ResOwner, ResGuests, ResDate, ResStatus, Butler) values(?, ?, ?, ?, ? ,?, ?);", (RoomNumber, Resnumber, ResOwner, ResGuests, ResDate, ResStatus, Butler))
            super().get_connection.commit()
            print(f"Added Reservation #{Resnumber} successfully")
        except Exception as e:
            print("Error:", e)
    def listResults(self):
        Info = self.fetch()
        return Info
    def taken(self):
        Info = self.fetch()
        TakenRooms, TakenNumber, TakenOwner, TakenDates, TakenStatuses, TakenGuests = [], [], [], [], [], []
        for bit in Info:
            TakenRooms.append(bit[1])
            TakenNumber.append(bit[2])
            TakenOwner.append(bit[3])
            TakenDates.append(bit[5])
            TakenGuests.append(bit[4])
            TakenStatuses.append(bit[6])
        return TakenRooms, TakenNumber, TakenOwner, TakenDates, TakenStatuses, TakenGuests

class HotelUsers(db.DBbase):
    def reset_or_create_db(self, defaults=True):
        try:
            sql = """
                DROP TABLE IF EXISTS HotelUsers;
                
                CREATE TABLE HotelUsers (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT,
                    Password TEXT,
                    Type TEXT,
                    Email TEXT
                );
            """
            super().execute_script(sql)
            if defaults==True:
                self.read_default_users("DefaultUsers.csv")
                self.save_to_database()
        except Exception as e:
            print(e)
            
    def read_default_users(self, file_name):
        self.default_users = []
        try:
            with open(file_name, 'r') as record:
                csv_contents = csv.reader(record)
                next(csv_contents)
                for i, row in enumerate(csv_contents):
                    User = UserData(row)
                    self.default_users.append(User)
        except Exception as e:
            print(e)
            
    def delete(self, Username):
        try:
            super().get_cursor.execute("DELETE FROM HotelUsers where Username = ?;", (Username,))
            super().get_connection.commit()
            print(f"Deleted {Username} successfully")
            return True
        except Exception as e:
            print("Error:", e)
            return False
        
    def save_to_database(self):
        #print("Number of records to save: ", len(self.default_users))
        save = 'y' if True else input("Continue? ").lower()
        if save == "y":
            for item in self.default_users:
                try:
                    super().get_cursor.execute("""INSERT INTO HotelUsers
                    (Username, Password, Type, Email)
                        VALUES( ?,?,?,?)""", 
                        (item.Username, item.Password, item.Type, item.Email))
                    super().get_connection.commit()
                except Exception as e:
                    print(e)
        else:
            print("Save to DB aborted.")
            
    def update(self, KeyColumn="Username", KeyValue="", ChangeColumn="Password", ChangeValue=""):
        # Update HotelUsers set [NewMetric] = "NewValue" where [TargetMetric] = "TargetValue"
        # Update HotelUsers set [Type] = "Administrator" where [Username] = "TargetValue"
        try:
            query = f"UPDATE HotelUsers SET {ChangeColumn} = ? WHERE {KeyColumn} = ?;"

            print(query, "TargetValue = ", ChangeValue, "; KeyValue = ", KeyValue)
            super().get_cursor.execute(query, (ChangeValue, KeyValue))
            super().get_connection.commit()
            print(f"Updated record to {ChangeValue} successfully")
        except Exception as e:
            print("An error has occurred.", e)
            
    def fetch(self, ID=None, Username=None, Email=None, Role=None):
        try:
            if ID is not None:
                return super().get_cursor.execute("SELECT * FROM HotelUsers WHERE ID = ?", (ID,)).fetchone()
            elif Username is not None:
                return super().get_cursor.execute("SELECT * FROM HotelUsers WHERE Username = ?", (Username,)).fetchone()
            elif Email is not None:
                return super().get_cursor.execute("SELECT * FROM HotelUsers WHERE Email = ?", (Email,)).fetchone()
            elif Role is not None:
                return super().get_cursor.execute("SELECT * FROM HotelUsers WHERE Type = ?", (Role,)).fetchall()
            else:
                return super().get_cursor.execute("SELECT * FROM HotelUsers").fetchall()
        except Exception as e:
            print("An error has occurred.", e)
            
    def add(self, Username, Password, Email):
        try:
            super().get_cursor.execute("insert or ignore into HotelUsers (Username, Password, Type, Email) values(?, ?, ?, ?);", (Username, Password, "User", Email))
            super().get_connection.commit()
            print(f"Added {Username} successfully")
        except Exception as e:
            print("Error:", e)

class HotelRooms(db.DBbase):
    def reset_or_create_db(self, defaults=True):
        try:
            sql = """
                DROP TABLE IF EXISTS HotelRooms;
                CREATE TABLE HotelRooms (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Floor INTEGER,
                    RoomName TEXT,
                    RmNo INTEGER,
                    RoomTier INTEGER,
                    CostPerNight DECIMAL(10, 2),
                    MaxGuests INTEGER,
                    Status TEXT
                );
            """
            super().execute_script(sql)
            if defaults:
                self.read_default_rooms("DefaultRooms.csv")
                self.save_to_database()
        except Exception as e:
            print(e)
    def read_default_rooms(self, file_name):
        self.default_rooms = []
        try:
            with open(file_name, 'r') as record:
                csv_contents = csv.reader(record)
                next(csv_contents)
                for i, row in enumerate(csv_contents):
                    Room = RoomData(row)
                    self.default_rooms.append(Room)
        except Exception as e:
            print(e)
    
    def update(self, KeyValue="", ChangeValue="", KeyColumn="ID", ChangeColumn="Status"):
        try:
            query = f"UPDATE HotelRooms SET {ChangeColumn} = ? WHERE {KeyColumn} = ?;"

            print(query, "TargetValue = ", ChangeValue, "; KeyValue = ", KeyValue)
            super().get_cursor.execute(query, (ChangeValue, KeyValue))
            super().get_connection.commit()
            print(f"Updated record to {ChangeValue} successfully")
        except Exception as e:
            print("An error has occurred.", e)
            
    def save_to_database(self):
        #print("Number of records to save: ", len(self.default_users))
        save = 'y' if True else input("Continue? ").lower()
        if save == "y":
            for item in self.default_rooms:
                try:
                    super().get_cursor.execute("""INSERT INTO HotelRooms
                    (Floor, RoomName, RmNo, RoomTier, CostPerNight, MaxGuests, Status)
                        VALUES( ?,?,?,?, ?, ?, ?)""", 
                        (item.Floor, item.RoomName, item.RmNo, item.RoomTier, item.CostPerNight, item.MaxGuests, item.Status))
                    super().get_connection.commit()
                except Exception as e:
                    print(e)
        else:
            print("Save to DB aborted.")
    def fetchall(self, Status=None):
        if Status is not None:
            return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE NOT Status = ?", (Status, )).fetchall()
        else:
            return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE 1=1").fetchall()
    def fetch(self, check_in_date, check_out_date, ID=None, Username=None, Floor=None, RoomTier=None, RoomName=None, Guests=None, Cost=None, Unavailable = [], limit="<"):
        check_in_str = check_in_date.strftime('%Y-%m-%d')
        check_out_str = check_out_date.strftime('%Y-%m-%d')
        
        Base_Query = "SELECT * FROM HotelRooms WHERE "
        
        
        
        if len(Unavailable) > 0:
            UnavailableString = ','.join(['?'] * len(Unavailable))
            and_available = f" AND ID NOT IN ({UnavailableString})"
        else:
            and_available = ""
        try:
            if ID is not None:
                return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE ID = ?{and_available}", (ID, *Unavailable)).fetchall()
            elif Username is not None:
                return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE ReservedBy = ?{and_available}", (Username,*Unavailable)).fetchall()
            elif Floor is not None:
                if type(Floor) == int:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE Floor {limit} ?{and_available}", (Floor,*Unavailable)).fetchall()
                elif len(Floor) == 2:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE Floor BETWEEN ? AND ?{and_available}", (Floor[0], Floor[1], *Unavailable)).fetchall()
            elif Guests is not None:
                if type(Guests) == int:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE MaxGuests {limit} ?{and_available}", (Guests,*Unavailable)).fetchall()
                elif len(Guests) == 2:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE MaxGuests BETWEEN ? AND ?{and_available}", (Guests[0], Guests[1], *Unavailable)).fetchall()
            elif RoomTier is not None:
                if type(RoomTier) == int:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE RoomTier {limit} ?{and_available}", (RoomTier,*Unavailable)).fetchall()
                elif len(RoomTier) == 2:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE RoomTier BETWEEN ? AND ?{and_available}", (RoomTier[0], RoomTier[1], *Unavailable)).fetchall()
            elif Cost is not None:
                if type(Cost) == float or type(Cost) == int:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE CostPerNight {limit} ?{and_available}", (Cost,*Unavailable)).fetchall()
                elif len(Cost) == 2:
                    return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE CostPerNight BETWEEN ? AND ?{and_available}", (Cost[0], Cost[1], *Unavailable)).fetchall()
            elif RoomName is not None:
                return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE RoomName = ?{and_available}", (RoomName,*Unavailable)).fetchall()
            else:
                return super().get_cursor.execute(f"SELECT * FROM HotelRooms WHERE 1=1{and_available}", (*Unavailable,)).fetchall()
        except Exception as e:
            print("An error has occurred.", e)

#### Joe Code
class HotelEmployees(db.DBbase):
    def reset_or_create_db(self, defaults=True):
        try:
            sql = """
                DROP TABLE IF EXISTS HotelEmployees;
                CREATE TABLE HotelEmployees (
                    EmployeeID INTEGER,
                    Username TEXT PRIMARY KEY,
                    Salary REAL,
                    Floor_Served INTEGER,
                    Position TEXT NOT NULL,
                    Address TEXT,
                    DOB DATE, 
                    Status INTEGER
                );
            """
            super().execute_script(sql)
            if defaults==True:
                self.load_default_employees("DefaultEmployees.csv")
                self.save_to_database()
        except Exception as e:
            print(e)

    def load_default_employees(self, file_name):
        self.default_employees = []
        try:
            with open(file_name, 'r') as record:
                csv_contents = csv.reader(record)
                next(csv_contents)
                for i, row in enumerate(csv_contents):
                    Res = EmployeeData(row)
                    self.default_employees.append(Res)
        except Exception as e:
            print(e)

    def save_to_database(self):
        #print("Number of records to save: ", len(self.default_users))
        save = 'y' if True else input("Continue? ").lower()
        if save == "y":
            for item in self.default_employees:
                try:
                    super().get_cursor.execute("""INSERT INTO HotelEmployees
                    (EmployeeID, Username, Salary, Floor_Served, Position, Address, DOB, Status)
                        VALUES(?,?,?,?,?,?,?,?)""",
                        (item.ID, item.Username, item.Salary, item.Floor_Served, item.Position, item.Address, item.DOB, item.Status))
                    super().get_connection.commit()
                except Exception as e:
                    print(e)
        else:
            print("Save to DB aborted.")

    def delete(self, key, value):
        try:
            super().get_cursor.execute(f"DELETE FROM HotelEmployees where {key} = ?;", (value,))
            super().get_connection.commit()
            print(f"Deleted instances where {key} = {value} successfully")
            return True
        except Exception as e:
            print("Error:", e)
            return False

    def update(self, KeyValue="", ChangeValue="", KeyColumn="Username", ChangeColumn="Address"):
        # Update HotelEmployees set [NewMetric] = "NewValue" where [TargetMetric] = "TargetValue"
        # Update HotelEmployees set [Type] = "Administrator" where [Username] = "TargetValue"
        try:
            query = f"UPDATE HotelEmployees SET {ChangeColumn} = ? WHERE {KeyColumn} = ?;"

            print(query, "TargetValue = ", ChangeValue, "; KeyValue = ", KeyValue)
            super().get_cursor.execute(query, (ChangeValue, KeyValue))
            super().get_connection.commit()
            print(f"Updated record to {ChangeValue} successfully")
        except Exception as e:
            print("An error has occurred.", e)

    def read_default_employees(self, file_name):
        self.default_rooms = []
        try:
            with open(file_name, 'r') as record:
                csv_contents = csv.reader(record)
                next(csv_contents)
                for i, row in enumerate(csv_contents):
                    Room = RoomData(row)
                    self.default_rooms.append(Room)
        except Exception as e:
            print(e)

    def fetch(self, Username=None, Position=None, Address=None, Status=None, Floor=None, FetchAll=False):
        try:
            if Username is not None:
                return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Username = ?", (Username,)).fetchone()
            elif Position is not None:
                if FetchAll:
                    return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Position = ?", (Position,)).fetchall()
                else:
                    return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Position = ?", (Position,)).fetchone()
            elif Address is not None:
                return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Address = ?", (Address,)).fetchone()
            elif Status is not None:
                return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Status = ?", (Status,)).fetchall()
            elif Floor is not None:
                return super().get_cursor.execute("SELECT * FROM HotelEmployees WHERE Floor_Served = ?", (Floor,)).fetchall()
            else:
                return super().get_cursor.execute("SELECT * FROM HotelEmployees").fetchall()
        except Exception as e:
            print("An error has occurred.", e)
    def add(self, Username, Salary, Floor_Served, Position, Address, DOB, Status):
        try:
            super().get_cursor.execute("insert or ignore into HotelEmployees (Username, Salary, Floor_Served, Position, Address, DOB, Status) values(?, ?, ?, ?, ?, ?, ?);", (Username, Salary, Floor_Served, Position, Address, DOB, Status))
            super().get_connection.commit()
            print(f"Added {Username} successfully")
        except Exception as e:
            print("Error:", e)