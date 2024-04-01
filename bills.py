from flask import Response, Flask, render_template, make_response, jsonify, Blueprint, request, session
from models import Sts_info, db, Vehicle, User, Role, Sts_manager_info, Sts_records, Landfill_records
from datetime import datetime, time
import pdfkit
bills = Blueprint("bills", __name__, static_folder="static", template_folder="templates")


# @bills.route('/', methods=['GET', 'POST'])
# def create_bill():
#     return "bill"


@bills.route('/generate-bill', methods=['POST'])
def calculate_bill():
    print("a")
    # if 1 or 18 in session['permissions']:
    if 1:
        data = request.json
        vehicle_id = data.get('vehicle_id')
        weight = data.get('weight')
        distance = data.get('distance')
        landfill_id = data.get('landfill_id')
        arrival_time = data.get('arrival_time')
        departure_time = data.get('departure_time')

        vehicle_match = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
        # print(vehicle_match.vehicle_id)
        weight = float(weight)
        capacity = float(vehicle_match.vehicle_capacity)
        if weight <= capacity:

            bill = distance * (vehicle_match.fcpk_unloaded +
                               (weight / capacity)
                               * (vehicle_match.fcpk_loaded - vehicle_match.fcpk_unloaded))

            arrival_date_time = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M:%S")
            departure_date_time = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S")

            record = Landfill_records(vehicle_id, landfill_id, weight, arrival_date_time, departure_date_time, bill)
            db.session.add(record)
            db.session.commit()

            bill_id = record.record_id
            response = make_response(jsonify({"success": "True",
                                              "bill": bill,
                                              "bill_id": bill_id}), 201)

        else:
            response = make_response(jsonify({"success": "False", "message": "Insufficient Capacity"}), 401)

    else:
        response = make_response(jsonify({"success": "False", "message": "Insufficient Permissions"}), 401)
    return response


