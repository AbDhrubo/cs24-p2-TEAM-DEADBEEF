from flask import Flask, Blueprint, render_template, session, redirect

from models import User,db,Sts_info,Sts_manager_info,Landfill_info,Landfill_manager_info

dashboard = Blueprint("dashboard", __name__, static_folder="static", template_folder="templates")


@dashboard.route('/')
def dashboard_view():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            if user.role_id == 1:
                user_data = {'id': user.id, 'name': user.name, 'email': user.email, 'contact': user.contact,
                             'role': user.role_id}

                return render_template('dashboard.html', session_role=session['role'], session_id=session['id'], user=user_data)


            elif user.role_id == 2:

                sts_manager = db.session.query(Sts_manager_info, User).join(User,
                                                                            Sts_manager_info.id == User.id).filter(
                    User.id == user.id).first()

                if sts_manager:
                    sts_manager_info, user = sts_manager

                    user_data = {

                        'id': user.id,

                        'name': user.name,

                        'email': user.email,

                        'contact': user.contact,

                        'role': user.role_id,

                        'ward_id': sts_manager_info.ward_id

                    }

                    sts_info = Sts_info.query.filter_by(ward_id=sts_manager_info.ward_id).first()

                    if sts_info:
                        sts_data = {
                            'id': sts_info.ward_id,
                            'name': sts_info.name
                        }

                    else:
                        sts_data = {
                            'id': 'unassigned',
                            'name': 'unassigned'
                        }

                    return render_template('dashboard.html', session_role=session['role'], session_id=session['id'],

                                           user=user_data, sts=sts_data)


            elif user.role_id == 3:

                lf_manager = db.session.query(Landfill_manager_info, User).join(User,
                                                                            Landfill_manager_info.id == User.id).filter(
                    User.id == user.id).first()

                if lf_manager:
                    landfill_manager_info, user = lf_manager

                    user_data = {

                        'id': user.id,

                        'name': user.name,

                        'email': user.email,

                        'contact': user.contact,

                        'role': user.role_id,

                        'lf_id': landfill_manager_info.landfill_id

                    }

                    lf_info = Landfill_info.query.filter_by(landfill_id=landfill_manager_info.landfill_id).first()

                    if lf_info:
                        lf_data = {
                            'id': lf_info.landfill_id,
                            'name': lf_info.name
                        }

                    else:
                        lf_data = {
                            'id': 'unassigned',
                            'name': 'unassigned'
                        }

                    return render_template('dashboard.html', session_role=session['role'], session_id=session['id'],

                                           user=user_data, lf=lf_data)


    else:
        return redirect('/')

