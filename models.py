from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, time
import json
import re

# from app import db
db = SQLAlchemy()


def remove_int(input_string, integer_to_remove):
    # Define a regular expression pattern to find integers within square brackets
    pattern = r"\[(\d+),(\d+),(\d+)\]"

    # Find all integers within square brackets
    matches = re.findall(pattern, input_string)

    # If matches are found, remove the specified integer
    if matches:
        # Loop through all matches
        for match in matches:
            # Convert match to integers
            integers = [int(x) for x in match]
            # Check if specified integer is present
            if integer_to_remove in integers:
                # Remove the specified integer from the list
                integers.remove(integer_to_remove)
                # Reconstruct the modified string
                modified_string = "[" + ",".join(str(x) for x in integers) + "]"
                # Replace the original string with the modified one
                modified_string = re.sub(pattern, modified_string, input_string)
                # Return the modified string
                return modified_string
    # If no matches are found or the specified integer is not present, return the original string
    return input_string


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    permissions = db.Column(db.String)

    def __init__(self, name, permissions):
        self.name = name
        self.permissions = json.dumps(permissions)

    def get_permissions(self):
        return json.loads(self.permissions)

    def add_permissions(self, permission_id):
        modified_string = self.permissions[:-1]
        modified_string += f", {permission_id}]"
        self.permissions = modified_string

    def remove_permissions(self, permission_id):
        modified_string = remove_int(self.permissions, permission_id)
        self.permissions = modified_string


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    name = db.Column(db.String)
    contact = db.Column(db.String)
    verified = db.Column(db.Integer)

    def __init__(self, email, password, role_id, name="Shreya", contact="01552393972"):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id
        self.name = name
        self.contact = contact
        self.verified = 0

    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    code = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, email, code, timestamp=datetime.now()):
        self.email = email
        self.code = code
        self.timestamp = timestamp

    def update_code(self, code, timestamp=datetime.now()):
        self.code = code
        self.timestamp = timestamp

#  additional classes
# vehicle (vehicle ID(pk) , regnum , type , capacity , fuel cost per km(fully loaded) , fcpk (unloaded), ward ID (pk,fk))
# STStation information (ward id (pk) , capacity in tonnes, gps co-ordinate)
# STStation operation between vehicles and STS (vehicle id (pk, fk), ward id(pk,fk) , weight , time of arrival, time of departure, record id(pk) , bill) //entry put by sts managers, bill will be calculated and added to the column
# STS managers information (Id(pk), name , contact , email, role , ward ID(pk,fk))


# Cost of journey = Cost of unloaded ( fcpk empty + (weight/ capacity) * fcpk loaded )
# landfill manager can download pdf of the bill


# Landfill station information
# Landfill station operations between vehicles and stations
# Landfill managers information

class Sts_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ward_id = db.Column(db.Integer, unique=True)
    station_capacity = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


    def __init__(self, name, ward_id, capacity, latitude=23.78457, longitude=90.33013):
        self.ward_id = ward_id
        self.name = name
        self.station_capacity = capacity
        self.latitude = latitude
        self.longitude = longitude


class Sts_manager_info(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('sts_info.ward_id'), nullable=False)

    def __init__(self, id, ward_id=-1):
        self.id = id
        self.ward_id = ward_id

    def assign(self, ward_no):
        self.ward_id = ward_no


class Vehicle(db.Model):
    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('sts_info.ward_id'))
    reg_num = db.Column(db.String(100), unique=True)
    vehicle_type = db.Column(db.Integer)
    vehicle_capacity = db.Column(db.Float)
    fcpk_unloaded = db.Column(db.Float)
    fcpk_loaded = db.Column(db.Float)

    def __init__(self, reg_num="unregistered", vehicle_type=1, fcpk_ul=10, fcpk_l=5, ward_id=-1):
        self.reg_num = reg_num
        self.vehicle_type = vehicle_type
        print(type(vehicle_type))

        if vehicle_type == '1':
            self.vehicle_capacity = 3  # defining fixed capacity according to the  4 types
        elif vehicle_type == '2':
            self.vehicle_capacity = 5
        elif vehicle_type == '3':
            self.vehicle_capacity = 7
        else:
            self.vehicle_capacity = 15

        self.fcpk_unloaded = fcpk_ul
        self.fcpk_loaded = fcpk_l
        self.ward_id = ward_id

    def assign(self, ward_no):
        self.ward_id = ward_no



class Sts_records(db.Model):
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'))
    ward_id = db.Column(db.Integer)
    weight = db.Column(db.Float)
    arrival_time = db.Column(db.DateTime)
    departure_time = db.Column(db.DateTime)
    bill = db.Column(db.Float)

    def __init__(self, vehicle_id, ward_id, weight, arrival_time,
                 departure_time, bill=0):
        self.vehicle_id = vehicle_id
        self.ward_id = ward_id
        self.weight = weight
        self.arrival_time = arrival_time
        self.departure_time = departure_time


class Landfill_info(db.Model):
    landfill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    site_capacity = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)

    def __init__(self, name, capacity, latitude=23.78457, longitude=90.33013, opening_time=time(9, 0), closing_time=time(5, 0)):
        self.site_capacity = capacity
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.opening_time = opening_time
        self.closing_time = closing_time


class Landfill_records(db.Model):
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'), nullable=False)
    landfill_id = db.Column(db.Integer, db.ForeignKey('landfill_info.landfill_id'), nullable=False)
    weight = db.Column(db.Float)
    arrival_time = db.Column(db.DateTime)
    departure_time = db.Column(db.DateTime)
    bill = db.Column(db.Float)

    def __init__(self, vehicle_id, landfill_id, weight, arrival_time=time(9, 0),
                 departure_time=time(9, 0), bill=0):
        self.vehicle_id = vehicle_id
        self.landfill_id = landfill_id
        self.weight = weight
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.bill = bill


class Landfill_manager_info(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    landfill_id = db.Column(db.Integer, db.ForeignKey('landfill_info.landfill_id'), nullable=False)

    def __init__(self, id, landfill_id=-1):
        self.id = id
        self.landfill_id = landfill_id

    def assign(self, lf_no):
        self.landfill_id = lf_no


