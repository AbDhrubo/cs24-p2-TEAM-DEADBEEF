from flask import Flask, Blueprint, render_template, session, redirect

from models import User

dashboard = Blueprint("dashboard", __name__, static_folder="static", template_folder="templates")


@dashboard.route('/')
def dashboard_view():
    if 'id' in session:
        user = User.query.filter_by(id=session['id']).first()
        if user:
            user_data = {'id': user.id, 'name': user.name, 'email': user.email, 'contact': user.contact,
                         'role': user.role_id}

            return render_template('dashboard.html', session_role=session['role'], session_id=session['id'], user=user_data)
    else:
        return redirect('/login')

