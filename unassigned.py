from flask import Flask, render_template, make_response, jsonify, Blueprint, request, session, redirect
from models import Sts_info, db, Vehicle, User, Role, Sts_manager_info, Landfill_manager_info

unassigned = Blueprint("unassigned", __name__, static_folder="static", template_folder="templates")

@unassigned.route('/', methods=['GET'])
def access_unassigned():
    if request.method == 'GET':
        if 5 in session['permissions']:
            all_un = User.query.filter_by(role_id=4).all()

            un_data = [
                {
                    'id': un.id,
                    'name': un.name,
                    'email': un.email,
                    'contact': un.contact
                }
                for un in all_un]

            if request.headers.get('accept') == 'application/json':
                return jsonify(un_data), 201
            else:
                return render_template('all_unassigned.html', uns=un_data)

        else:
            response_data = {
                "success": "False",
                "message": "Request Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

@unassigned.route('/choose_role/<int:userId>')
def choose_role(userId: int):
    if session['role'] == 1:
        return render_template('choose_un_role.html', id=userId)
    else:
        response_data = {
            "success": "False",
            "message": "Request Failed: Method Not Allowed"
        }
        return jsonify(response_data), 500


@unassigned.route('/assign/<int:userId>', methods=['PUT'])
def assign_uns(userId: int):
    if request.method == 'PUT':
        if session['role']==1:
            existing_user = User.query.filter_by(id=userId).first()
            print('a')
            data = request.json
            role = data.get('selection')

            if existing_user:
                print('b')
                existing_user.role_id = role

                db.session.commit()


                if role == '2':
                    print(334)
                    added_user = User.query.filter_by(id=userId).first()
                    new_sts_manager = Sts_manager_info(id=added_user.id)
                    db.session.add(new_sts_manager)
                    db.session.commit()

                if role == '3':
                    print(456)
                    added_user = User.query.filter_by(id=userId).first()
                    new_lf_manager = Landfill_manager_info(id=added_user.id)
                    db.session.add(new_lf_manager)
                    db.session.commit()


                response_data = {
                    "success": "True",
                    "message": "Edit Success: User Info Is Updated"
                }
                return jsonify(response_data), 201
            else:
                response_data = {
                    "success": "False",
                    "message": "Request Failed: Method Not Allowed"
                }
                return jsonify(response_data), 400

        else:
            response_data = {
                "success": "False",
                "message": "Request Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


