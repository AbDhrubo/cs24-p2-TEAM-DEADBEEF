from datetime import time

from flask import Flask, render_template, make_response, jsonify, Blueprint, request, session
from models import Sts_info, db, Vehicle, User, Role, Sts_manager_info, Landfill_info, Landfill_manager_info

landfill = Blueprint("landfill", __name__, static_folder="static", template_folder="templates")


def is_valid_time(hour, minute, second=0):
    try:
        # Attempt to create a time object
        time(hour=hour, minute=minute, second=second)
        return True  # Time is valid
    except ValueError:
        return False


@landfill.route('/', methods=['GET', 'POST'])
def create_landfill():
    if request.method == 'GET':
        if 15 in session['permissions']:
            all_lf = Landfill_info.query.all()
            lf_data = [
                {
                    'id': lf.landfill_id,
                    'capacity': lf.site_capacity,
                    'name': lf.name,
                    'lat': lf.latitude,
                    'long': lf.longitude,
                    'open': lf.opening_time,
                    'close': lf.closing_time
                }
                for lf in all_lf]

            if request.headers.get('accept') == 'application/json':
                return jsonify(lf_data), 201
            else:
                return render_template('all_lf.html', lfs=lf_data)

        else:
            response_data = {
                "success": "False",
                "message": "Request Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


    if request.method == 'POST':
        if 15 in session['permissions']:
            data = request.json
            name = data.get('name')
            site_capacity = data.get('capacity')
            latitude = data.get('lat')
            longitude = data.get('long')
            opening_time_hh = data.get('opening_hour')
            opening_time_mm = data.get('opening_minute')
            closing_time_hh = data.get('closing_hour')
            closing_time_mm = data.get('closing_minute')

            opening_time_mm = int(opening_time_mm)
            opening_time_hh = int(opening_time_hh)
            closing_time_mm = int(closing_time_mm)
            closing_time_hh = int(closing_time_hh)

            if is_valid_time(opening_time_hh, opening_time_mm) and is_valid_time(closing_time_hh, closing_time_mm):
                opening_time = time(opening_time_hh, opening_time_mm)
                closing_time = time(closing_time_hh, closing_time_mm)
                if closing_time > opening_time:
                    new_landfill = Landfill_info(name, site_capacity, latitude, longitude, opening_time, closing_time)
                    db.session.add(new_landfill)
                    db.session.commit()
                    response = make_response(jsonify({"success": "True", "message": "New landfill created"}), 201)

                else:
                    response = make_response(jsonify({"success": "False", "message": "Closing time must be after opening time"}), 401)

            else:
                response = make_response(jsonify({"success": "False", "message": "Invalid Time"}), 401)
        else:
            response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@landfill.route('/add_lf')
def add_lf():
    if 15 in session['permissions']:
        return render_template('create_lf.html')

@landfill.route('/edit/<int:lfId>')
def view_lf(lfId: int):
    lf = Landfill_info.query.filter_by(landfill_id=lfId).first()
    if lf:
        lf_data ={
                    'id': lf.landfill_id,
                    'capacity': lf.site_capacity,
                    'name': lf.name,
                    'lat': lf.latitude,
                    'long': lf.longitude,
                    'open': lf.opening_time,
                    'close': lf.closing_time
                 }

        return render_template('lf_profile.html', lf=lf_data)

    else:
        response = make_response(jsonify({"success": "False", "message": "No Landfill Site Found"}), 401)
        return response


@landfill.route('/assign_m/<int:lfId>')
def assign_m_lf(lfId: int):
    if 16 in session['permissions']:
        # Perform a join operation between Sts_manager_info and User tables
        query = db.session.query(Landfill_manager_info, User).join(User, Landfill_manager_info.id == User.id).filter(Landfill_manager_info.landfill_id == -1)

        all_managers = query.all()


        managers_data = [
                {
                 'id': manager.Landfill_manager_info.id,
                 'name': manager.User.name,
                 'email': manager.User.email,
                 'contact': manager.User.contact
                }
                for manager in all_managers]

        return render_template('unassigned_l_managers.html', managers=managers_data, lf_no=lfId)


    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@landfill.route('/manager_list', methods=['GET'])
def get_lf_manager_list():
    if 5 in session['permissions']:
        all_managers = db.session.query(Landfill_manager_info, User).join(User, Landfill_manager_info.id == User.id).all()

        managers_data = [
            {
                'id': manager.Landfill_manager_info.id,
                'name': manager.User.name,
                'email': manager.User.email,
                'contact': manager.User.contact,
                'lf': manager.Landfill_manager_info.landfill_id
            }
            for manager in all_managers]

        all_lf = db.session.query(Landfill_info).all()
        lf_data = [
            {
                'landfill_no': lf.landfill_id,
                'name': lf.name,
            }
            for lf in all_lf]

        return render_template('all_lf_managers.html', managers=managers_data, lfs=lf_data)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)
        return response


@landfill.route('/add-manager/<int:lf_no>/<int:manager_id>', methods=['PUT'])
def assign_manager(lf_no: int, manager_id: int):
    if 16 in session['permissions']:

        lf_match = Landfill_info.query.filter_by(landfill_id=lf_no).first()
        manager_match = Landfill_manager_info.query.filter_by(id=manager_id).first()

        if lf_match and manager_match:
            print('a')
            manager_match.assign(lf_no)
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "Manager Assigned"}), 201)

            query = db.session.query(Landfill_manager_info, User).join(User, Landfill_manager_info.id == User.id).filter(
                Landfill_manager_info.landfill_id == -1)

            all_managers = query.all()

            managers_data = [
                {
                    'id': manager.Landfill_manager_info.id,
                    'name': manager.User.name,
                    'email': manager.User.email,
                    'contact': manager.User.contact
                }
                for manager in all_managers]

            return render_template('unassigned_l_managers.html', managers=managers_data)

        else:
            response = make_response(jsonify({"success": "False", "message": "STS or vehicle not found"}), 403)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient permissions"}), 401)

    return response