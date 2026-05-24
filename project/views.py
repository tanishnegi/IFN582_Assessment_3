from flask import Blueprint, render_template, request, session, flash,redirect, url_for, abort
from .db import get_properties, search_properties , create_user, user_exists, check_for_user,get_preferences,calculate_compatibility,save_user_preferences,get_user_preferences, get_property_details, create_enquiry
from .forms import SearchForm, RegisterForm, LoginForm, EnquiryForm
from hashlib import sha256

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    properties = get_properties()
    preferences = get_preferences()
    user_preferences = []
    if session.get("logged_in") and session["user"]["role"] == "buyer":
        form.sort_by.choices.append(("compatibility", "Sort by - Compatibility"))
        user_preferences = get_user_preferences(session["user"]["id"])
        for property in properties:
            property.compatibility = calculate_compatibility(property.id,session["user"]["id"])
            if property.compatibility >= 80:
                property.badge = "success"
            elif property.compatibility >= 50:
                property.badge = "warning"
            else:
                property.badge = "danger"
        if form.sort_by.data == "compatibility":
            properties.sort(key=lambda x: x.compatibility,reverse=True)
        
    return render_template('home.html', form=form, properties=properties, preferences=preferences, user_preferences=user_preferences)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    user_preferences = []

    if session.get("logged_in") and session["user"]["role"] == "buyer":
        form.sort_by.choices.append(("compatibility", "Sort by - Compatibility"))
        user_preferences = get_user_preferences(session["user"]["id"])

    selected_preferences = request.form.getlist('preferences')

    if form.validate_on_submit():
        properties = search_properties(form,selected_preferences)
    else:
        properties = get_properties()

    if session.get("logged_in") and session["user"]["role"] == "buyer":
        for property in properties:
            property.compatibility = calculate_compatibility(property.id,session["user"]["id"])
        if form.sort_by.data == "compatibility":
            properties.sort(key=lambda x: x.compatibility,reverse=True)

    preferences = get_preferences()
    return render_template(
        'home.html',
        form=form,
        properties=properties,
        preferences=preferences,
        user_preferences=user_preferences
    )

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        form.password.data = sha256(form.password.data.encode()).hexdigest()
        user = user_exists(form.email.data)
        if user:
            flash("Username or email already exists. Please choose another.", "danger")
            return redirect(url_for('main.register'))
        create_user(form)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        form.password.data = sha256(form.password.data.encode()).hexdigest()
        user = check_for_user(form.email.data, form.password.data)
        if not user:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('main.login'))
        print(user)
        session["user"]={
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "phone": user.phone,
            "is_admin": user.role == "admin",
            "role": user.role
        }
        session["logged_in"] = True
        flash("Logged in successfully!", "success")
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    flash('You have been logged out.','info')
    return redirect(url_for('main.index'))

@bp.route('/save-preferences', methods=['POST'])
def save_preferences():

    user_id = session['user']['id']
    selected_preferences = request.form.getlist('preferences')
    save_user_preferences(user_id, selected_preferences)
    flash("Preferences updated successfully!", "success")
    return redirect(url_for('main.index'))

@bp.route('/property/<int:property_id>', methods=['GET', 'POST'])
def property_details(property_id):
    property = get_property_details(property_id)

    if not property:
        abort(404)

    enquiry_form = EnquiryForm()
    preferences = get_preferences()
    user_preferences = []

    if session.get("logged_in") and session["user"]["role"] == "buyer":
        user_preferences = get_user_preferences(session["user"]["id"])
        property.compatibility = calculate_compatibility(
            property.id,
            session["user"]["id"]
        )
        if request.method == 'POST' and enquiry_form.validate_on_submit():
            create_enquiry(property.id, session["user"]["id"], enquiry_form)
            flash("Enquiry sent successfully!", "success")
            return redirect(url_for('main.property_details', property_id=property.id))
    elif request.method == 'POST':
        flash("Please log in as a tenant to send an enquiry.", "warning")
        return redirect(url_for('main.login'))

    return render_template(
        'property_details.html',
        property=property,
        enquiry_form=enquiry_form,
        preferences=preferences,
        user_preferences=user_preferences
    )