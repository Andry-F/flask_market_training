from flask import render_template, redirect, url_for, flash, request
from market import app, db
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['POST', 'GET'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    if request.method == 'POST':
        purchase_item = request.form.get('purchased_item')
        p_item = Item.query.filter_by(name=purchase_item).first()
        if p_item:
            if current_user.can_purchase(p_item):
                p_item.buy(current_user)
                flash(f"Congratulations! You purchased {p_item.name} for {p_item.price}$",
                      category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item.name}!", category='danger')
        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        return render_template('market.html', items=items, purchase_form=purchase_form)


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
