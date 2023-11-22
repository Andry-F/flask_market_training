from flask import render_template, redirect, url_for, flash
from market import app, db
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        try:
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash('User created', category='success')
            return redirect(url_for('market_page'))
        except:
            db.session.rollback()
            flash(f'Error adding user to the DB', category='error')
            return render_template('register.html', form=form)
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(f'There was an error {error_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = db.session.scalars(db.select(User).filter_by(username=form.username.data)).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout_page():
    logout_user()
    flash('You are Logout', category='info')
    return redirect(url_for('home_page'))
