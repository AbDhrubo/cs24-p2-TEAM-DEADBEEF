from flask import Flask, Blueprint, render_template, session, url_for, jsonify
import requests

from models import User

all_users = Blueprint("all_users", __name__, static_folder="static", template_folder="templates")


@all_users.route('/')
def all_users_view():
    # session_cookie = {'session': 'eyJlbWFpbCI6ImRocnVib0BkaHJ1Ym8uY29tIiwicGVybWlzc2lvbnMiOlsxLDIsMyw0XSwicm9sZSI6MX0.ZgbErA.ccvY3OEWBbxtw8loc_LSZBwvlSg'}
    # response = requests.get('http://localhost:5000//users', cookies=session_cookie)
    print(session['role'])
    response = requests.get('http://localhost:5000/users')

    if response.status_code == 200:
        users_data = response.json()
        return render_template('all_users.html', users=users_data)
    else:
        return render_template('error.html', code=response.status_code)


@all_users.route('/create_user')
def create_new_user():
    if session['role'] == 1:
        return render_template('create_user.html')


@all_users.route('/view/<int:userId>')
def view_user(userId: int):

    link = f'http://localhost:5000/users/{userId}'
    response = requests.get(link)

    user_data = response.json()
    if response.status_code == 200:
        return render_template('dashboard.html', session_role=session['role'], session_id=session['id'], user=user_data)
    else:
        return render_template('error.html', code=response.status_code)


@all_users.route('/edit/<int:userId>')
def edit_user(userId: int):
    user = User.query.filter_by(id=userId).first()
    if user:
        user_data = {'id': user.id, 'name': user.name, 'email': user.email, 'contact': user.contact,
                     'role': user.role_id}
    return render_template('edit_user.html', session_role=session['role'], user=user_data)

