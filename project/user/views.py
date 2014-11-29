# project/user/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required

from project.models import User
from project.token import ts
# from project.email import send_email
from project import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm


################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('You registered and are now logged in. Welcome!', 'success')

        return redirect(url_for('user.login'))

    return render_template('user/register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            flash('Welcome.')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email and/or password.')
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile')
@login_required
def profile():
    form = ChangePasswordForm(request.form)
    return render_template('user/profile.html', form=form)


@user_blueprint.route('/confirm/<token>')
def confirm_email(token, max_age=86400):
    try:
        email = ts.loads(token, max_age, salt="email-confirm-key")
    except:
        flash('The confirmation link is invalid or has expired.')
    user = User.query.filter_by(email=email).first_or_404()
    if user.email_confirmed:
        flash('Account already confirmed. Please login.')
    else:
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    return redirect(url_for('user.login'))
