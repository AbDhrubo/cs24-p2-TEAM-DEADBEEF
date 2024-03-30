from flask import Blueprint, jsonify, session, request, render_template, redirect, make_response, url_for
import requests
from models import User, Role, db
import re
import json

rbac = Blueprint("rbac", __name__, static_folder="static", template_folder="templates")


def is_valid_format(input_string):
    # Define a regular expression pattern to match the format
    pattern = r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\](?<!,)"

    # Check if the input string matches the pattern
    match = re.match(pattern, input_string)

    # Return True if the format matches, False otherwise
    return bool(match)


def remove_inverted_commas(s):
    # Use regular expression to replace single and double quotes with an empty string
    return re.sub(r"['\"]", "", s)


@rbac.route('/roles', methods=['GET', 'POST'])
def roles_create_manage():
    if request.method == 'GET':
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

    elif request.method == 'POST':
        data = request.json
        role_name = data.get('role_name')
        permissions = data.get('permissions')
        role_match = Role.objects.filter(name=role_name).first()
        if not role_match:
            print(permissions)
            permissions = remove_inverted_commas(permissions)
            if is_valid_format(permissions):
                print(permissions)
                role = Role(role_name, json.loads(permissions))
                db.session.add(role)
                db.session.commit()
                print('a')
                response = make_response(jsonify({"success": "True", "message": "User Role created"}), 201)
                return response
            else:
                response = make_response(jsonify({"success": "False", "message": "Invalid Permissions"}), 401)
                return response

        else:
            response = make_response(jsonify({"success": "False", "message": "Role already exits"}), 401)
            return response
    else:
        return "invalid method"


@rbac.route('/roles/<int:roleID>/permissions', methods=['POST'])
def role_permissions(roleID: int):
    if request.method == 'POST':
        data = request.json
        permission_id = data.get('permission_id')
        operation = data.get('operation')
        role = Role.query.filter_by(id=roleID).first()
        if role:
            if operation == "add":
                if permission_id in role.get_permissions():
                    response = make_response(jsonify({"success": "False", "message": "Permission already exists"}), 401)
                else:
                    role.add_permissions(permission_id)
                    db.session.commit()
                    response = make_response(jsonify({"success": "True", "message": "Permission added"}), 201)
            elif operation == "remove":
                if permission_id not in role.get_permissions():
                    response = make_response(jsonify({"success": "False", "message": "Permission does not exist"}), 401)
                else:
                    role.remove_permissions(permission_id)
                    db.session.commit()
                    response = make_response(jsonify({"success": "True", "message": "Permission removed"}), 200)

            else:
                response = make_response(jsonify({"success": "False", "message": "invalid operation"}), 401)

        else:
            response = make_response(jsonify({"success": "False", "message": "Role not found"}), 201)

        return response


@rbac.route('/update-role', methods=['POST'])
def update_role():
    data = request.json
    role_name = data.get('role_name')
    permissions = data.get('permissions')
    role_match = Role.query.filter_by(name=role_name).first()
    if role_match:
        permissions = remove_inverted_commas(permissions)
        if is_valid_format(permissions):
            role_match.permissions = permissions
            db.session.commit()
            response = make_response(jsonify({"success": "True", "message": "User Role created"}), 201)
            return response
        else:
            response = make_response(jsonify({"success": "False", "message": "Invalid Permissions"}), 401)
            return response

    else:
        response = make_response(jsonify({"success": "False", "message": "Role already exits"}), 401)
        return response

