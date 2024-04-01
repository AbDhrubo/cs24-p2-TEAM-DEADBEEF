from flask import Flask, render_template, make_response, jsonify, Blueprint, request, session
from models import Sts_info, db, Vehicle

vehicle = Blueprint("vehicle", __name__, static_folder="static", template_folder="templates")


@vehicle.route('/', methods=['GET', 'POST'])
def create_vehicle():
    if request.method == 'GET':
        if 11 in session['permissions']:
            all_vehicles = Vehicle.query.all()
            vehicles_data = [
                {'id': vehicle.vehicle_id,
                 'ward': vehicle.ward_id,
                 'reg': vehicle.reg_num,
                 'type': vehicle.vehicle_type,
                 'capacity': vehicle.vehicle_capacity,
                 'loaded': vehicle.fcpk_loaded,
                 'unloaded': vehicle.fcpk_unloaded
                 }
                for vehicle in all_vehicles]

            if request.headers.get('accept') == 'application/json':
                return jsonify(vehicles_data), 201
            else:
                return render_template('all_vehicles.html', vehicles=vehicles_data)

        else:
            response_data = {
                "success": "False",
                "message": "Request Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

    if request.method == 'POST':
        if 12 in session['permissions']:
            data = request.json
            reg_num = data.get('reg_num')
            vehicle_type = data.get('vehicle_type')
            print(vehicle_type)
            fcpk_ul = data.get('fcpk_ul')
            fcpk_l = data.get('fcpk_l')

            new_vehicle = Vehicle(reg_num, vehicle_type, fcpk_ul, fcpk_l)
            db.session.add(new_vehicle)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "Vehicle Created"}), 201)

        else:
            response = make_response(jsonify({"success": "False", "message": "Insufficient Permissions"}), 401)
        return response


@vehicle.route('/add_truck')
def add_truck():
    if 12 in session['permissions']:
        return render_template('create_truck.html')


@vehicle.route('/<int:truckId>', methods=['DELETE'])
def delete_truck(truckId: int):
    if request.method == 'DELETE':
        if 13 in session['permissions']:
            print('a')
            truck = Vehicle.query.get(truckId)
            print('b')
            if truck:
                db.session.delete(truck)
                db.session.commit()

                response_data = {
                    "success": "True",
                    "message": "Deletion Success: Truck Removed"
                }
                return jsonify(response_data), 201

            else:
                response = jsonify({"success": "False", "message": "No Truck Found"})
                response.status_code = 404
                return response

        else:
            response_data = {
                "success": "False",
                "message": "Deletion Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


@vehicle.route('/edit/<int:truckId>')
def edit_truck(truckId: int):
    vehicle = Vehicle.query.filter_by(vehicle_id=truckId).first()
    if vehicle:
        truck_data ={
             'id': vehicle.vehicle_id,
             'ward': vehicle.ward_id,
             'reg': vehicle.reg_num,
             'type': vehicle.vehicle_type,
             'capacity': vehicle.vehicle_capacity,
             'loaded': vehicle.fcpk_loaded,
             'unloaded': vehicle.fcpk_unloaded
             }
        return render_template('truck_data.html', truck=truck_data)



