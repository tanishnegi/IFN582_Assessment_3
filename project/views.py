from flask import Blueprint, render_template, request, session, flash, redirect, url_for, abort
from .db import (
    get_properties,
    search_properties,
    create_user,
    user_exists,
    check_for_user,
    get_preferences,
    calculate_compatibility,
    save_user_preferences,
    get_user_preferences,
    get_user_enquiries,
    get_user_offers,
    get_property_details,
    create_enquiry,
    delete_user,
    get_users,
    get_management_properties,
    get_property_interactions,
    get_property_offers,
    create_property,
    update_property,
    delete_property,
    get_bookmarks,
    get_bookmark,
    get_offer,
    save_bookmark,
    remove_bookmark,
    create_offer,
    update_offer_status,
)
from .forms import SearchForm, RegisterForm, LoginForm, EnquiryForm, AdminUserForm, PropertyForm, BookmarkForm, OfferForm
from hashlib import sha256

bp = Blueprint('main', __name__)


def require_login(*roles):
    if not session.get("logged_in"):
        flash("Please log in to continue.", "warning")
        return redirect(url_for("main.login"))

    if roles and session["user"]["role"] not in roles:
        abort(403)

    return None

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


@bp.route('/bookmarks', methods=['GET'])
def bookmarks():
    access = require_login('buyer')
    if access:
        return access

    user_id = session['user']['id']
    return render_template(
        'bookmarks.html',
        bookmarks=get_bookmarks(user_id),
        bookmark_form=BookmarkForm()
    )


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    access = require_login('buyer')
    if access:
        return access

    user_id = session['user']['id']
    preferences = get_preferences()
    user_preferences = get_user_preferences(user_id)

    return render_template(
        'dashboard.html',
        preferences=preferences,
        user_preferences=user_preferences,
        enquiries=get_user_enquiries(user_id),
        offers=get_user_offers(user_id),
    )


@bp.route('/enquiries', methods=['GET'])
def enquiries():
    access = require_login('buyer')
    if access:
        return access

    user_id = session['user']['id']
    user_preferences = get_user_preferences(session["user"]["id"])
    return render_template(
        'enquiries.html',
        enquiries=get_user_enquiries(user_id),
        user_preferences=user_preferences,
    )


@bp.route('/property/<int:property_id>/bookmark', methods=['POST'])
def save_property_bookmark(property_id):
    access = require_login('buyer')
    if access:
        return access

    property = get_property_details(property_id)
    if not property:
        abort(404)

    note = request.form.get('note', '').strip()
    save_bookmark(session['user']['id'], property_id, note)
    flash("Bookmark saved.", "success")
    return redirect(request.referrer or url_for('main.bookmarks'))


@bp.route('/property/<int:property_id>/bookmark/remove', methods=['POST'])
def remove_property_bookmark(property_id):
    access = require_login('buyer')
    if access:
        return access

    remove_bookmark(session['user']['id'], property_id)
    flash("Bookmark removed.", "info")
    return redirect(request.referrer or url_for('main.bookmarks'))


@bp.route('/admin', methods=['GET'])
def admin_dashboard():
    access = require_login('admin')
    if access:
        return access

    return render_template(
        'admin.html',
        user_form=AdminUserForm(),
        users=get_users(),
        properties=get_management_properties(),
        interactions=get_property_interactions(),
    )


@bp.route('/admin/users/create', methods=['POST'])
def create_admin_user():
    access = require_login('admin')
    if access:
        return access

    form = AdminUserForm()
    if form.validate_on_submit():
        form.password.data = sha256(form.password.data.encode()).hexdigest()
        if user_exists(form.email.data):
            flash("That email is already registered.", "danger")
            return redirect(url_for('main.admin_dashboard'))

        create_user(form)
        flash("User account created successfully!", "success")
    else:
        flash("Please complete all user fields.", "danger")

    return redirect(url_for('main.admin_dashboard'))


@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def remove_admin_user(user_id):
    access = require_login('admin')
    if access:
        return access

    if session['user']['id'] == user_id:
        flash("You cannot delete your own account while logged in.", "warning")
        return redirect(url_for('main.admin_dashboard'))

    delete_user(user_id)
    flash("User account removed.", "info")
    return redirect(url_for('main.admin_dashboard'))


@bp.route('/listings', methods=['GET'])
def listings():
    access = require_login('admin', 'seller')
    if access:
        return access

    owner_id = None if session['user']['role'] == 'admin' else session['user']['id']
    return render_template(
        'listings.html',
        properties=get_management_properties(owner_id),
        interactions=get_property_interactions(owner_id),
        offers=get_property_offers(owner_id),
        role=session['user']['role']
    )


def _can_manage_offer(offer_id):
    offer = None
    offers = get_property_offers()
    for row in offers:
        if row['id'] == offer_id:
            offer = row
            break

    if not offer:
        abort(404)

    if session['user']['role'] != 'admin':
        property = get_property_details(offer['property_id'])
        if not property or property.seller_id != session['user']['id']:
            abort(403)

    return offer


@bp.route('/offers/<int:offer_id>/accept', methods=['POST'])
def accept_offer(offer_id):
    access = require_login('admin', 'seller')
    if access:
        return access

    _can_manage_offer(offer_id)
    update_offer_status(offer_id, 'accepted')
    flash("Offer accepted.", "success")
    return redirect(url_for('main.listings'))


@bp.route('/offers/<int:offer_id>/reject', methods=['POST'])
def reject_offer(offer_id):
    access = require_login('admin', 'seller')
    if access:
        return access

    _can_manage_offer(offer_id)
    update_offer_status(offer_id, 'rejected')
    flash("Offer rejected.", "info")
    return redirect(url_for('main.listings'))


@bp.route('/property/create', methods=['GET', 'POST'])
def create_property_listing():
    access = require_login('admin', 'seller')
    if access:
        return access

    form = PropertyForm()
    if request.method == 'POST' and form.validate_on_submit():
        create_property(form, session['user']['id'])
        flash("Property listing created successfully!", "success")
        return redirect(url_for('main.listings'))

    return render_template(
        'property_form.html',
        form=form,
        heading='Create Listing',
        submit_label='Create Listing'
    )


@bp.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
def edit_property_listing(property_id):
    access = require_login('admin', 'seller')
    if access:
        return access

    property = get_property_details(property_id)
    if not property:
        abort(404)

    if session['user']['role'] != 'admin' and property.seller_id != session['user']['id']:
        abort(403)

    form = PropertyForm(obj=property)
    if request.method == 'POST' and form.validate_on_submit():
        update_property(property_id, form)
        flash("Property listing updated successfully!", "success")
        if session['user']['role'] == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.listings'))

    return render_template(
        'property_form.html',
        form=form,
        heading='Edit Listing',
        submit_label='Update Listing'
    )


@bp.route('/property/<int:property_id>/delete', methods=['POST'])
def remove_property_listing(property_id):
    access = require_login('admin', 'seller')
    if access:
        return access

    property = get_property_details(property_id)
    if not property:
        abort(404)

    if session['user']['role'] != 'admin' and property.seller_id != session['user']['id']:
        abort(403)

    delete_property(property_id)
    flash("Property listing removed.", "info")
    if session['user']['role'] == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.listings'))

@bp.route('/save-preferences', methods=['POST'])
def save_preferences():

    user_id = session['user']['id']
    selected_preferences = request.form.getlist('preferences')
    save_user_preferences(user_id, selected_preferences)
    flash("Preferences updated successfully!", "success")
    if session.get("logged_in") and session.get("user", {}).get("role") == "buyer":
        return redirect(request.referrer or url_for('main.dashboard'))
    return redirect(url_for('main.index'))


def _property_details_context(property_id, enquiry_form=None, offer_form=None):
    property = get_property_details(property_id)
    if not property:
        abort(404)

    enquiry_form = enquiry_form or EnquiryForm()
    offer_form = offer_form or OfferForm()
    bookmark_form = BookmarkForm()
    preferences = get_preferences()
    user_preferences = []
    bookmark = None
    offer = None
    document_links = []

    if session.get("logged_in") and session["user"]["role"] == "buyer":
        user_id = session["user"]["id"]
        user_preferences = get_user_preferences(user_id)
        bookmark = get_bookmark(user_id, property_id)
        offer = get_offer(user_id, property_id)
        property.compatibility = calculate_compatibility(property.id, user_id)
        if offer:
            offer_form.offered_price.data = offer['offered_price']

    if property.property_type in ("Shared Apartment", "Shared House", "Private Room"):
        document_links = [
            {"label": "Rental application checklist", "description": "Documents to prepare before applying."},
            {"label": "Condition report", "description": "Useful for shared housing move-in checks."},
        ]
    else:
        document_links = [
            {"label": "Contract of sale", "description": "Review the standard contract before making an offer."},
            {"label": "Seller disclosure", "description": "Check the vendor disclosure details for this property."},
            {"label": "Appraisal and reports", "description": "Request supporting valuation or inspection documents."},
        ]

    return render_template(
        'property_details.html',
        property=property,
        enquiry_form=enquiry_form,
        offer_form=offer_form,
        bookmark_form=bookmark_form,
        bookmark=bookmark,
        offer=offer,
        preferences=preferences,
        user_preferences=user_preferences,
        document_links=document_links,
    )

@bp.route('/property/<int:property_id>', methods=['GET', 'POST'])
def property_details(property_id):
    enquiry_form = EnquiryForm()
    if session.get("logged_in") and session["user"]["role"] == "buyer":
        if request.method == 'POST' and enquiry_form.validate_on_submit():
            create_enquiry(property_id, session["user"]["id"], enquiry_form)
            flash("Enquiry sent successfully!", "success")
            return redirect(url_for('main.property_details', property_id=property_id))
    elif request.method == 'POST':
        flash("Please log in as a tenant to send an enquiry.", "warning")
        return redirect(url_for('main.login'))

    return _property_details_context(property_id, enquiry_form=enquiry_form)


@bp.route('/property/<int:property_id>/offer', methods=['POST'])
def submit_property_offer(property_id):
    access = require_login('buyer')
    if access:
        return access

    offer_form = OfferForm()
    if offer_form.validate_on_submit():
        create_offer(property_id, session['user']['id'], offer_form.offered_price.data)
        flash("Offer submitted successfully!", "success")
        return redirect(url_for('main.property_details', property_id=property_id))

    flash("Please correct the offer details and try again.", "danger")
    return _property_details_context(property_id, offer_form=offer_form)