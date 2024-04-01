from datetime import datetime
from models import Landfill_info


from flask import Flask, render_template, make_response, jsonify, Blueprint, request, session, redirect
from models import Sts_info, db, Vehicle, User, Role, Sts_manager_info, Sts_records

sts = Blueprint("sts", __name__, static_folder="static", template_folder="templates")


@sts.route('/', methods=['GET', 'POST'])
def create_sts():
    if request.method == 'GET':
        if 9 in session['permissions']:
            all_sts = Sts_info.query.all()
            sts_data = [
                {
                 'id': sts.id,
                 'ward_id': sts.ward_id,
                 'name': sts.name,
                 'capacity': sts.station_capacity,
                 'long': sts.longitude,
                 'lat': sts.latitude
                 }
                for sts in all_sts]

            if request.headers.get('accept') == 'application/json':
                return jsonify(sts_data), 201
            else:
                return render_template('all_sts.html', stss=sts_data)

        else:
            response_data = {
                "success": "False",
                "message": "Request Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

    if request.method == 'POST':
        if 10 in session['permissions']:
            data = request.json
            name = data.get('name')
            ward_id = data.get('ward_id')
            station_capacity = data.get('capacity')
            latitude = data.get('lat')
            longitude = data.get('long')

            new_sts = Sts_info(name, ward_id, station_capacity, latitude, longitude)
            db.session.add(new_sts)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "New STS created"}), 201)
        else:
            response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@sts.route('/add_sts')
def add_sts():
    if 9 in session['permissions']:
        return render_template('create_sts.html')

@sts.route('/edit/<int:stsId>')
def view_sts(stsId: int):
    sts = Sts_info.query.filter_by(id=stsId).first()
    if sts:
        sts_data ={
             'id': sts.id,
             'name': sts.name,
             'ward_id': sts.ward_id,
             'capacity': sts.station_capacity,
             'lat': sts.latitude,
             'long': sts.longitude
             }

        all_vehicles = Vehicle.query.filter_by(ward_id=sts.ward_id).all()
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

        return render_template('sts_profile.html', sts=sts_data, vehicles=vehicles_data)

    else:
        response = make_response(jsonify({"success": "False", "message": "No STS Found"}), 401)
        return response

@sts.route('/assign/<int:wardId>')
def assign_sts(wardId: int):
    if 10 in session['permissions']:
        all_vehicles = Vehicle.query.filter_by(ward_id=-1).all()

        vehicles_data = [
                {
                 'id': vehicle.vehicle_id,
                 'ward': vehicle.ward_id,
                 'reg': vehicle.reg_num,
                 'type': vehicle.vehicle_type,
                 'capacity': vehicle.vehicle_capacity,
                 'loaded': vehicle.fcpk_loaded,
                 'unloaded': vehicle.fcpk_unloaded
                }
                for vehicle in all_vehicles]

        return render_template('unassigned_vehicles.html', vehicles=vehicles_data, ward_no=wardId)


    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@sts.route('/manager_list', methods=['GET'])
def get_sts_manager_list():
    if 5 in session['permissions']:
        all_managers = db.session.query(Sts_manager_info, User).join(User, Sts_manager_info.id == User.id).all()

        managers_data = [
            {
                'id': manager.Sts_manager_info.id,
                'name': manager.User.name,
                'email': manager.User.email,
                'contact': manager.User.contact,
                'sts': manager.Sts_manager_info.ward_id
            }
            for manager in all_managers]

        all_sts = db.session.query(Sts_info).all()
        sts_data = [
            {
                'ward_no': sts.ward_id,
                'name': sts.name,
            }
            for sts in all_sts]

        return render_template('all_sts_managers.html', managers=managers_data, stss=sts_data)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@sts.route('/assign_m/<int:wardId>')
def assign_m_sts(wardId: int):
    if 10 in session['permissions']:
        # Perform a join operation between Sts_manager_info and User tables
        query = db.session.query(Sts_manager_info, User).join(User, Sts_manager_info.id == User.id).filter(Sts_manager_info.ward_id == -1)

        all_managers = query.all()


        managers_data = [
                {
                 'id': manager.Sts_manager_info.id,
                 'name': manager.User.name,
                 'email': manager.User.email,
                 'contact': manager.User.contact
                }
                for manager in all_managers]

        return render_template('unassigned_managers.html', managers=managers_data, ward_no=wardId)

        # else:
        #     response = make_response(jsonify({"success": "False", "message": "No manager available for assigning"}), 401)
        #     return response


    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response




@sts.route('/add-vehicle/<int:ward_no>/<int:vehicle_id>', methods=['PUT'])
def assign_vehicle(ward_no: int, vehicle_id: int):
    if 13 in session['permissions']:

        sts_match = Sts_info.query.filter_by(ward_id=ward_no).first()
        vehicle_match = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()

        if sts_match and vehicle_match:
            print('a')
            vehicle_match.assign(ward_no)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "Vehicle added"}), 201)

            all_vehicles = Vehicle.query.filter_by(ward_id=-1).all()
            vehicles_data = [
                {
                    'id': vehicle.vehicle_id,
                    'ward': vehicle.ward_id,
                    'reg': vehicle.reg_num,
                    'type': vehicle.vehicle_type,
                    'capacity': vehicle.vehicle_capacity,
                    'loaded': vehicle.fcpk_loaded,
                    'unloaded': vehicle.fcpk_unloaded
                }
                for vehicle in all_vehicles]

            return render_template('unassigned_vehicles.html', vehicles=vehicles_data, ward_no=ward_no)

        else:
            response = make_response(jsonify({"success": "False", "message": "STS or vehicle not found"}), 403)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)

    return response


@sts.route('/add-manager/<int:ward_no>/<int:manager_id>', methods=['PUT'])
def assign_manager(ward_no: int, manager_id: int):
    if 13 in session['permissions']:

        sts_match = Sts_info.query.filter_by(ward_id=ward_no).first()
        manager_match = Sts_manager_info.query.filter_by(id=manager_id).first()

        if sts_match and manager_match:
            print('a')
            manager_match.assign(ward_no)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "Manager Assigned"}), 201)

            query = db.session.query(Sts_manager_info, User).join(User, Sts_manager_info.id == User.id).filter(
                Sts_manager_info.ward_id == -1)

            all_managers = query.all()

            managers_data = [
                {
                    'id': manager.Sts_manager_info.id,
                    'name': manager.User.name,
                    'email': manager.User.email,
                    'contact': manager.User.contact
                }
                for manager in all_managers]

            return render_template('unassigned_managers.html', managers=managers_data, ward_no=ward_no)

        else:
            response = make_response(jsonify({"success": "False", "message": "STS or vehicle not found"}), 403)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)

    return response



@sts.route('/add-record/<int:ward_id>', methods=['GET', 'POST'])
def add_record_sts(ward_id: int):
    if request.method == 'POST':
        data = request.json
        vehicle_id = data.get('vehicle_id')
        vehicle_match = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
        if vehicle_match and vehicle_match.ward_id == ward_id:
            weight = data.get('weight')
            arrival_date = data.get('arrival_date')
            arrival_month = data.get('arrival_month')
            arrival_year = data.get('arrival_year')
            arrival_time_hh = data.get('arrival_time_hh')
            arrival_time_mm = data.get('arrival_time_mm')

            arr_time_hh = int(arrival_time_hh)
            arr_time_mm = int(arrival_time_mm)
            arr_year = int(arrival_year)
            arr_date = int(arrival_date)
            arr_month = int(arrival_month)

            arrival_time = datetime(arr_year, arr_month, arr_date, arr_time_hh, arr_time_mm)
            departure_time = datetime.now()
            new_record = Sts_records(vehicle_id, ward_id, weight, arrival_time, departure_time)
            db.session.add(new_record)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "Record Added"}), 201)
        else:
            response = make_response(jsonify({"success": "False", "message": "Invalid Vehicle"}), 403)

        return response

    if request.method == 'GET':
        vehicles = Vehicle.query.filter_by(ward_id=ward_id).all()
        vehicle_ids = [vehicle.vehicle_id for vehicle in vehicles]
        return render_template('sts_add_record.html', ward_id=ward_id, vehicle_ids=vehicle_ids)


@sts.route('/route/<int:ward_id>/<int:landfill_id>')
def route_show(ward_id:int, landfill_id:int):

    sts = Sts_info.query.filter_by(ward_id=ward_id).first()
    lf = Landfill_info.query.filter_by(landfill_id=landfill_id).first()

    response = {
        'source_lat': sts.latitude,
        'source_long': sts.longitude,
        'dest_lat': lf.latitude,
        'dest_long': lf.longitude
    }

    return jsonify(response)


@sts.route('/route/<int:ward_id>', methods=['GET', 'POST'])
def route_sts(ward_id: int):
    if request.method == 'GET':
        lfs = Landfill_info.query.all()
        lf_ids = [lf.landfill_id for lf in lfs]
        return render_template('sts_route.html', ward_id=ward_id, lf_ids=lf_ids)


