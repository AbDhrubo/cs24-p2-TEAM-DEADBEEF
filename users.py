import requests
from flask import Blueprint, jsonify, session, request, render_template, redirect, make_response, url_for
from auth import send_mail
from datetime import datetime

# import app
from models import User, Role, db, Verification, Sts_manager_info, Landfill_manager_info

users = Blueprint("users", __name__, static_folder="static", template_folder="templates")


permissions = ['Create User', 'Edit Own Information', 'Edit other peoples information', 'Get own information',
               'Get other users\' information', 'Delete User']


@users.route('/', methods=['GET', 'POST'])
def show_ar_add_users():

    if request.method == 'GET':

        if session['role'] == 1:
            all_users = User.query.all()
            users_data = [{'id': user.id, 'name': user.name, 'email': user.email, 'contact': user.contact, 'role': user.role_id} for user in all_users]

            if request.headers.get('accept') == 'application/json':
                return jsonify(users_data), 201
            else:
                return render_template('all_users.html', users=users_data)

        else:
            response_data = {
                "success": "False",
                "message": "Update Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

    if request.method == 'POST':
        if 1 in session['permissions']:
            data = request.json
            email = data.get('email')
            role = data.get('role')
            name = data.get('name')
            contact = data.get('contact')
            password = "12345678"

            new_user = User(email=email, password=password, role_id=role, name=name, contact=contact)

            existing_user = User.query.filter_by(email=new_user.email).first()

            if existing_user:
                response_data = {
                    "success": "False",
                    "message": "Registration Failed: User Already Exists"
                }

                return jsonify(response_data), 500
            else:
                endpoint2_url = url_for('auth.send_mail', _external=True)
                response = requests.post(endpoint2_url, json={'email': email})
                if response.status_code // 100 == 2:
                    data = response.json()
                    code = data.get('code')
                    otp = Verification.query.filter_by(email=email).first()
                    if otp:
                        otp.update_code(code, datetime.now())
                        db.session.commit()
                    else:
                        otp = Verification(email, code, datetime.now())
                        db.session.add(otp)
                        db.session.commit()
                    # otp = Verification(email, code, datetime.now())
                    # db.session.add(otp)
                    db.session.add(new_user)
                    db.session.commit()

                    print(334)
                    if role == '2':
                        added_user = User.query.filter_by(email=new_user.email).first()
                        new_sts_manager = Sts_manager_info(id=added_user.id)
                        db.session.add(new_sts_manager)
                        db.session.commit()

                    if role == '3':
                        print(456)
                        added_user = User.query.filter_by(email=new_user.email).first()
                        new_lf_manager = Landfill_manager_info(id=added_user.id)
                        db.session.add(new_lf_manager)
                        db.session.commit()

                    response_data = {
                        "success": "True",
                        "message": "Registration Success: Please Ask User To Check Email"
                    }
                    return jsonify(response_data), 201
                else:
                    return jsonify({"success": False, "message": "Failed to send email"}), response.status_code

        else:
            response_data = {
                "success": "False",
                "message": "Registration Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


@users.route('/<int:userId>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_info(userId: int):
    if request.method == 'GET':
        if session['role'] == 1:
            user = User.query.filter_by(id=userId).first()
            if user:
                user_data = {'id': user.id, 'name': user.name, 'email': user.email, 'contact': user.contact, 'role': user.role_id}
                if request.headers.get('accept') == 'application/json':
                    return jsonify(user_data), 201
                else:
                    return render_template('others_profile.html', session_role=session['role'], session_id=session['id'], user=user_data)

        else:
            response_data = {
                "success": "False",
                "message": "Update Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


    if request.method == 'PUT':
        if 2 in session['permissions'] or 3 in session['permissions']:
            changed = False
            existing_user = User.query.filter_by(id=userId).first()

            data = request.json
            email = data.get('email')
            role = data.get('role')
            name = data.get('name')
            contact = data.get('contact')

            if existing_user:

                if existing_user.role_id != role:
                    changed = True

                existing_user.email = email
                existing_user.role_id = role
                existing_user.name = name
                existing_user.contact = contact

                db.session.commit()

                if changed:
                    added_user = User.query.filter_by(id=userId).first()

                    if role == '2':
                        new_sts_manager = Sts_manager_info(id=added_user.id)
                        db.session.add(new_sts_manager)
                        db.session.commit()

                    if role == '3':
                        new_lf_manager = Landfill_manager_info(id=added_user.id)
                        db.session.add(new_lf_manager)
                        db.session.commit()


                response_data = {
                    "success": "True",
                    "message": "Edit Success: User Info Is Updated"
                }
                return jsonify(response_data), 201

            else:
                response = jsonify({"success": "False", "message": "No User Found"})
                response.status_code = 404
                return response

        else:
            response_data = {
                "success": "False",
                "message": "Update Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

    if request.method == 'DELETE':
        # if 'id' in session:
        if 6 in session['permissions']:
            user = User.query.get(userId)
            if user:
                db.session.delete(user)
                db.session.commit()

                response_data = {
                    "success": "True",
                    "message": "Deletion Success: User Removed"
                }
                return jsonify(response_data), 201

            else:
                response = jsonify({"success": "False", "message": "No User Found"})
                response.status_code = 404
                return response

        else:
            response_data = {
                "success": "False",
                "message": "Deletion Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500


def get_permissions(arr):
    print(arr)
    list = []
    for i in arr:
        print(i)
        list.append(permissions[i-1])
    return list


@users.route('/roles')
def show_all_roles():
    if request.method == 'GET':
        if 1:
            all_roles = Role.query.all()
            # print(all_roles)
            if all_roles:
                # role_data = [{'Role Id': role.id, 'Role Name': role.name,
                #               'Permissions': get_permissions(role.get_permissions())} for role in all_roles]

                role_data = [{'id': role.id, 'name': role.name} for role in all_roles]
                response = make_response(jsonify(role_data), 200)
            else:
                response = make_response(jsonify({"success": "False", "message": "No Roles Found"}), 404)

            return response


@users.route('/<int:userId>/roles', methods=['PUT'])
def set_role(userId: int):
    user = User.query.filter_by(id=userId).first()
    if user:
        data = request.json
        role_id = data.get('role_id')
        role = Role.query.filter_by(id=role_id).first()
        if role:
            user.role_id = role_id
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "User Role updated"}), 201)
        else:
            response = make_response(jsonify({"success": "False", "message": "No Role Found"}), 403)

    else:
        response = make_response(({"success": "False", "message": "No User Found"}), 404)

    return response

