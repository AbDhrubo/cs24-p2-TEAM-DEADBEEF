from flask import Blueprint, jsonify, session, request, render_template, redirect, make_response, url_for
import requests
from models import User, Role

roles = Blueprint("roles", __name__, static_folder="static", template_folder="templates")


@roles.route('/')
def all_roles_view():
    # print(session['role'])
    # response = requests.get('http://localhost:5000/users/roles')
    endpoint2_url = url_for('users.show_all_roles', _external=True)
    response = requests.get(endpoint2_url)
    # print(response)
    if response.status_code == 200:
        role_data = response.json()
        print(role_data)
        return render_template('all_roles.html', roles=role_data)
    else:
        return render_template('error.html', code=response.status_code)


@roles.route('/view-users/<int:roleId>', methods=['GET'])
def role_users_view(roleId: int):
    users = User.query.filter_by(role_id=roleId)
    role = Role.query.filter_by(id=roleId).first()
    if users and role:
        user_data = users.all()
        print(role)

        return render_template('role_users.html', users=user_data, role_name=role.name)
    else:
        return render_template('error.html', code=response.status_code)


@roles.route('/create-role', methods=['GET'])
def create_role_view():
    count = 9
    titles = ['Create User', 'Update own information',
              "Update other users' information", "Get own information",
              "Get other users' information", "Delete User",
              "Create/ Remove Roles", "Add/ Assign Permissions",
              "Assign Roles"]

    return render_template('create_role.html', count=count, titles=titles)


@roles.route('/edit-permissions/<int:role_id>', methods=['GET'])
def edit_role_view(role_id: int):
    count = 9
    titles = ['Create User', 'Update own information',
              "Update other users' information", "Get own information",
              "Get other users' information", "Delete User",
              "Create/ Remove Roles", "Add/ Assign Permissions",
              "Assign Roles"]
    role = Role.query.filter_by(id=role_id).first()
    return render_template('edit_role.html', count=count, titles=titles, role_name=role.name)
