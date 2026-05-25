from flask import Blueprint, render_template, request, session, flash,redirect, url_for, abort, current_app
from .db import get_properties, search_properties , create_user, user_exists, check_for_user,get_preferences,calculate_compatibility,save_user_preferences,get_user_preferences, get_property_details, create_enquiry, add_property, add_property_image, get_my_listings,delete_property, get_property_by_id, update_property, delete_additional_images
from .forms import SearchForm, RegisterForm, LoginForm, EnquiryForm, PropertyForm
from hashlib import sha256
import os
from werkzeug.utils import secure_filename

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


@bp.route('/listing', methods=['GET', 'POST'])
def listing():

    form = PropertyForm()

    if form.validate_on_submit():

        cover_image = form.image.data

        filename = secure_filename(cover_image.filename)

        image_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            filename
        )

        cover_image.save(image_path)

        db_image_path = f"img/{filename}"


        seller_id = session['user']['id']

        property_id = add_property(
            form,
            seller_id,
            db_image_path
        )

        add_property_image(
        property_id,
        db_image_path,
        0
        )


        additional_images = form.additional_images.data

        display_order = 1

        for image in additional_images:

            if image.filename != '':

                extra_filename = secure_filename(image.filename)

                extra_image_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    extra_filename
                )

                image.save(extra_image_path)

                db_extra_path = f"img/{extra_filename}"

                add_property_image(
                    property_id,
                    db_extra_path,
                    display_order
                )

                display_order += 1

        flash('Property has been added successfully')

        return redirect(url_for('main.my_listings'))

    return render_template(
        'listing.html',
        form=form
    )

@bp.route('/my-listings')
def my_listings():

    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for('main.login'))

    user_id = session['user']['id']

    properties = get_my_listings(user_id)

    return render_template(
        'my_listings.html',
        properties=properties
    )

@bp.route('/delete-property/<int:property_id>')
def delete_property_route(property_id):

    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for('main.login'))

    delete_property(property_id)

    flash("Property deleted successfully.", "success")

    return redirect(url_for('main.my_listings'))

@bp.route('/edit-property/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):

    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for('main.login'))

    property = get_property_by_id(property_id)

    if not property:
        flash("Property not found.", "danger")
        return redirect(url_for('main.my_listings'))

    form = PropertyForm(obj=property)
    

    if form.validate_on_submit():

        image_path = property.image

        if form.image.data:

            cover_image = form.image.data

            filename = secure_filename(cover_image.filename)

            upload_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                filename
            )

            cover_image.save(upload_path)

            image_path = f"img/{filename}"

            add_property_image(
                property_id,
                image_path,
                0
            )

        update_property(
            property_id,
            form,
            image_path
        )

        additional_images = form.additional_images.data

        display_order = 1

        if additional_images and additional_images[0].filename != '':

            delete_additional_images(property_id)
        
        add_property_image(
        property_id,
        image_path,
        0
        )

        for image in additional_images:

            if image.filename != '':

                filename = secure_filename(image.filename)

                upload_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    filename
                )

                image.save(upload_path)

                db_image_path = f"img/{filename}"

                add_property_image(
                    property_id,
                    db_image_path,
                    display_order
                )

                display_order += 1

        flash("Property updated successfully.", "success")

        return redirect(url_for('main.my_listings'))

    return render_template(
        'edit_property.html',
        form=form,
        property=property
    )

