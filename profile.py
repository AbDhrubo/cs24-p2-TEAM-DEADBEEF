from flask import Blueprint, jsonify, session, request, render_template, redirect, make_response
from models import User, Role, db

profile = Blueprint("profile", __name__, static_folder="static", template_folder="templates")


@profile.route('/', methods=['GET', 'PUT'])
def user_profile():
    if request.method == 'GET':
        if 'id' in session:
            user = User.query.filter_by(id=session['id']).first()
            user_data = {'id': user.id,
                         'name': user.name,
                         'email': user.email,
                         'contact': user.contact,
                         'role': user.role_id}

            if request.headers.get('accept') == 'application/json':
                return jsonify(user_data), 201
            else:
                return render_template('profile.html', user=user_data, session_role=session['role'], session_id=session['id'])

        else:
            response_data = {
                "success": "False",
                "message": "Update Failed: Method Not Allowed"
            }
            return jsonify(response_data), 500

    if request.method == 'PUT':
        if 'id' in session:
            existing_user = User.query.filter_by(id=session['id']).first()

            data = request.json
            email = data.get('email')
            name = data.get('name')
            contact = data.get('contact')

            if existing_user:
                existing_user.email = email
                existing_user.name = name
                existing_user.contact = contact

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




