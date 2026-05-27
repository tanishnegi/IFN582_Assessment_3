from flask import session
from . import mysql
from .models import Preference, Property, User

FALLBACK_PROPERTY_IMAGES = [
    'img/property/rental-cover-17.jpg',
    'img/property/rental-kitchen-07.jpg',
    'img/property/rental-bedroom-01.jpg',
    'img/property/rental-bathroom-01.jpg',
]

FALLBACK_PROPERTY_DOCUMENTS = [
    'documents/Condition Report.pdf',
    'documents/House Agreement.pdf',
    'documents/Offer and Enquiry Guide.pdf',
]

ENQUIRY_STATUSES = {'new', 'responded', 'closed'}
OFFER_STATUSES = {'pending', 'accepted', 'rejected'}


def _ensure_fallback_property_assets(cur, property_id):
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM property_images
        WHERE property_id = %s
    """, (property_id,))
    image_count = cur.fetchone()['total']

    if image_count == 0:
        for display_order, image in enumerate(FALLBACK_PROPERTY_IMAGES, start=1):
            cur.execute("""
                INSERT INTO property_images (property_id, image, display_order)
                VALUES (%s, %s, %s)
            """, (property_id, image, display_order))

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM property_documents
        WHERE property_id = %s
    """, (property_id,))
    document_count = cur.fetchone()['total']

    if document_count == 0:
        for file_path in FALLBACK_PROPERTY_DOCUMENTS:
            cur.execute("""
                INSERT INTO property_documents (property_id, file_path)
                VALUES (%s, %s)
            """, (property_id, file_path))


def create_user(form):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (
            firstname,
            lastname,
            email,
            password,
            phone,
            role
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        form.firstname.data,
        form.lastname.data,
        form.email.data,
        form.password.data,
        form.phone.data,
        form.role.data
    ))
    mysql.connection.commit()
    cur.close()


def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()


def get_users():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, firstname, lastname, email, phone, role, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    users = cur.fetchall()
    cur.close()
    return users


def check_for_user(email, password):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM users
        WHERE email = %s AND password = %s
    """, (email, password))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(
            row['id'],
            row['firstname'],
            row['lastname'],
            row['email'],
            row['password'],
            row['phone'],
            row['role']
        )
    return None

def user_exists(email):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM users
        WHERE email = %s
    """, (email,))
    row = cur.fetchone()
    cur.close()
    return row is not None


def get_properties():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            p.*,
            pi.image AS cover_image
        FROM properties p
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
        WHERE p.status = 'available'
        ORDER BY p.created_at DESC
    """)
    properties = cur.fetchall()
    cur.close()
    return [
        Property(
            row['id'],
            row['title'],
            row['property_type'],
            float(row['price']),
            row['suburb'],
            row['city'],
            row['postcode'],
            row['bedrooms'],
            row['bathrooms'],
            row['occupants'],
            row['seller_id'],
            row['cover_image'],
            row['status'],
            row['description'],
            row['created_at']
        )
        for row in properties
    ]


def get_management_properties(owner_id=None):
    query = """
        SELECT
            p.id,
            p.seller_id,
            p.title,
            p.property_type,
            p.price,
            p.suburb,
            p.city,
            p.postcode,
            p.latitude,
            p.longitude,
            p.bedrooms,
            p.bathrooms,
            p.occupants,
            p.status,
            pi.image AS cover_image,
            p.description,
            p.created_at,
            u.firstname AS seller_firstname,
            u.lastname AS seller_lastname,
            COALESCE(ec.enquiry_count, 0) AS enquiry_count
        FROM properties p
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN (
            SELECT property_id, COUNT(*) AS enquiry_count
            FROM enquiries
            GROUP BY property_id
        ) ec ON p.id = ec.property_id
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
    """
    params = []

    if owner_id is not None:
        query += " WHERE p.seller_id = %s"
        params.append(owner_id)

    query += " ORDER BY p.created_at DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    properties = cur.fetchall()
    cur.close()
    return properties


def get_property_interactions(owner_id=None):
    query = """
        SELECT
            e.enquiry_id,
            e.property_id,
            e.subject,
            e.message,
            e.status,
            e.created_at,
            p.title AS property_title,
            p.seller_id,
            u.firstname AS buyer_firstname,
            u.lastname AS buyer_lastname,
            u.email AS buyer_email
        FROM enquiries e
        JOIN properties p ON e.property_id = p.id
        JOIN users u ON e.buyer_id = u.id
    """
    params = []

    if owner_id is not None:
        query += " WHERE p.seller_id = %s"
        params.append(owner_id)

    query += " ORDER BY e.created_at DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    interactions = cur.fetchall()
    cur.close()
    return interactions


def get_user_enquiries(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            e.enquiry_id,
            e.property_id,
            e.subject,
            e.message,
            e.status,
            e.created_at,
            p.title AS property_title,
            p.property_type,
            p.price,
            p.suburb,
            p.city,
            p.postcode,
            pi.image AS cover_image,
            u.firstname AS seller_firstname,
            u.lastname AS seller_lastname
        FROM enquiries e
        JOIN properties p ON e.property_id = p.id
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
        WHERE e.buyer_id = %s
        ORDER BY e.created_at DESC
    """, (user_id,))
    enquiries = cur.fetchall()
    cur.close()
    return enquiries


def get_user_offers(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            o.id,
            o.property_id,
            o.offered_price,
            o.status,
            o.created_at,
            p.title AS property_title,
            p.property_type,
            p.price,
            p.suburb,
            p.city,
            p.postcode,
            pi.image AS cover_image,
            u.firstname AS seller_firstname,
            u.lastname AS seller_lastname
        FROM offers o
        JOIN properties p ON o.property_id = p.id
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
        WHERE o.buyer_id = %s
        ORDER BY o.created_at DESC
    """, (user_id,))
    offers = cur.fetchall()
    cur.close()
    return offers


def get_property_offers(owner_id=None):
    query = """
        SELECT
            o.id,
            o.property_id,
            o.buyer_id,
            o.offered_price,
            o.status,
            o.created_at,
            p.title AS property_title,
            u.firstname AS buyer_firstname,
            u.lastname AS buyer_lastname,
            u.email AS buyer_email
        FROM offers o
        JOIN properties p ON o.property_id = p.id
        JOIN users u ON o.buyer_id = u.id
    """
    params = []

    if owner_id is not None:
        query += " WHERE p.seller_id = %s"
        params.append(owner_id)

    query += " ORDER BY o.created_at DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    offers = cur.fetchall()
    cur.close()
    return offers


def create_property(form, seller_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO properties (
            seller_id,
            title,
            property_type,
            price,
            suburb,
            city,
            postcode,
            latitude,
            longitude,
            bedrooms,
            bathrooms,
            occupants,
            status,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        seller_id,
        form.title.data,
        form.property_type.data,
        form.price.data,
        form.suburb.data,
        form.city.data,
        form.postcode.data,
        form.latitude.data,
        form.longitude.data,
        form.bedrooms.data,
        form.bathrooms.data,
        form.occupants.data,
        form.status.data,
        form.description.data,
    ))

    property_id = cur.lastrowid
    _save_property_preferences(cur, property_id, form.preferences.data)
    _ensure_fallback_property_assets(cur, property_id)

    mysql.connection.commit()
    cur.close()


def update_property(property_id, form):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE properties
        SET title = %s,
            property_type = %s,
            price = %s,
            suburb = %s,
            city = %s,
            postcode = %s,
            latitude = %s,
            longitude = %s,
            bedrooms = %s,
            bathrooms = %s,
            occupants = %s,
            status = %s,
            description = %s
        WHERE id = %s
    """, (
        form.title.data,
        form.property_type.data,
        form.price.data,
        form.suburb.data,
        form.city.data,
        form.postcode.data,
        form.latitude.data,
        form.longitude.data,
        form.bedrooms.data,
        form.bathrooms.data,
        form.occupants.data,
        form.status.data,
        form.description.data,
        property_id,
    ))

    _save_property_preferences(cur, property_id, form.preferences.data)
    _ensure_fallback_property_assets(cur, property_id)

    mysql.connection.commit()
    cur.close()


def delete_property(property_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM properties WHERE id = %s", (property_id,))
    mysql.connection.commit()
    cur.close()


def get_property_owner(property_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT seller_id FROM properties WHERE id = %s", (property_id,))
    row = cur.fetchone()
    cur.close()
    return row['seller_id'] if row else None


def get_property_details(property_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            p.id,
            p.title,
            p.property_type,
            p.price,
            p.suburb,
            p.city,
            p.postcode,
            p.latitude,
            p.longitude,
            p.bedrooms,
            p.bathrooms,
            p.occupants,
            p.seller_id,
            p.status,
            u.firstname AS seller_firstname,
            u.lastname AS seller_lastname,
            u.email AS seller_email,
            u.phone AS seller_phone,
            p.description,
            p.created_at,
            pi.image AS property_image,
            pd.file_path AS document_path,
            pref.name AS preference_name
        FROM properties p
        JOIN users u
            ON p.seller_id = u.id
        LEFT JOIN property_images pi
            ON p.id = pi.property_id
        LEFT JOIN property_documents pd
            ON p.id = pd.property_id
        LEFT JOIN property_preferences pp
            ON p.id = pp.property_id
        LEFT JOIN preferences pref
            ON pp.preference_id = pref.id
        WHERE p.id = %s
        ORDER BY pi.display_order ASC, pd.created_at ASC, pref.name ASC
    """, (property_id,))

    rows = cur.fetchall()
    cur.close()

    if not rows:
        return None

    first_row = rows[0]

    property = Property(
        first_row['id'],
        first_row['title'],
        first_row['property_type'],
        float(first_row['price']),
        first_row['suburb'],
        first_row['city'],
        first_row['postcode'],
        first_row['bedrooms'],
        first_row['bathrooms'],
        first_row['occupants'],
        first_row['seller_id'],
        first_row['property_image'],
        first_row['status'],
        first_row['description'],
        first_row['created_at']
    )

    images = []
    documents = []
    host_preferences = []
    property.seller_firstname = first_row['seller_firstname']
    property.seller_lastname = first_row['seller_lastname']
    property.seller_email = first_row['seller_email']
    property.seller_phone = first_row['seller_phone']
    property.latitude = first_row['latitude']
    property.longitude = first_row['longitude']

    for row in rows:
        if row['property_image'] and row['property_image'] not in images:
            images.append(row['property_image'])

        if row['document_path'] and row['document_path'] not in documents:
            documents.append(row['document_path'])

        if row['preference_name'] and row['preference_name'] not in host_preferences:
            host_preferences.append(row['preference_name'])

    property.images = images
    property.documents = documents
    property.host_preferences = host_preferences

    return property

def search_properties(form, selected_preferences=None):
    query = """
        SELECT
            p.*,
            pi.image AS cover_image
        FROM properties p
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
        WHERE p.status = 'available'
    """
    params = []

    if form.location.data:
        query += """
        AND (
            p.suburb LIKE %s
            OR p.postcode LIKE %s
            OR p.city LIKE %s
        )
        """

        data = form.location.data.strip()
        params.append(f"%{data}%")
        params.append(f"%{data}%")
        params.append(f"%{data}%")

    if form.property_type.data and form.property_type.data != "Any Type":
        query += " AND p.property_type = %s"
        params.append(form.property_type.data)

    if form.bedrooms.data and form.bedrooms.data != "Any Room":
        if form.bedrooms.data == "4+":
            query += " AND p.bedrooms >= %s"
            params.append(4)
        else:
            query += " AND p.bedrooms = %s"
            params.append(int(form.bedrooms.data))

    if form.price_range.data and form.price_range.data != "Any Price":
        if form.price_range.data == "Under $300":
            query += " AND p.price < 300"
        elif form.price_range.data == "$300 - $500":
            query += " AND p.price BETWEEN 300 AND 500"
        elif form.price_range.data == "$500 - $800":
            query += " AND p.price BETWEEN 500 AND 800"
        elif form.price_range.data == "$800+":
            query += " AND p.price > 800"

    if selected_preferences:
        placeholders = ','.join(['%s'] * len(selected_preferences))
        query += f"""
        AND p.id IN (
            SELECT property_id
            FROM property_preferences
            WHERE preference_id IN ({placeholders})
        )"""
        params.extend(selected_preferences)

    if form.sort_by.data == "price_low":
        query += " ORDER BY p.price ASC"
    elif form.sort_by.data == "price_high":
        query += " ORDER BY p.price DESC"
    else:
        query += " ORDER BY p.created_at DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    properties = cur.fetchall()
    cur.close()

    return [
        Property(
            row['id'],
            row['title'],
            row['property_type'],
            float(row['price']),
            row['suburb'],
            row['city'],
            row['postcode'],
            row['bedrooms'],
            row['bathrooms'],
            row['occupants'],
            row['seller_id'],
            row['cover_image'],
            row['status'],
            row['description'],
            row['created_at']
        )
        for row in properties
    ]   

def get_preferences():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preferences")
    preferences = cur.fetchall()
    cur.close()
    return [
        Preference(
            row['id'],
            row['name']
        )
        for row in preferences
    ]


def get_property_preferences(property_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT preference_id
        FROM property_preferences
        WHERE property_id = %s
    """, (property_id,))
    preferences = cur.fetchall()
    cur.close()
    return [row['preference_id'] for row in preferences]


def _save_property_preferences(cur, property_id, selected_preferences):
    cur.execute("""
        DELETE FROM property_preferences
        WHERE property_id = %s
    """, (property_id,))

    for pref_id in selected_preferences or []:
        cur.execute("""
            INSERT INTO property_preferences
            (property_id, preference_id)
            VALUES (%s, %s)
        """, (property_id, pref_id))


def calculate_compatibility(property_id, user_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT COUNT(*) AS match_count
        FROM property_preferences pp
        JOIN user_preferences up
            ON pp.preference_id = up.preference_id
        WHERE pp.property_id = %s
        AND up.user_id = %s
    """, (property_id, user_id))

    matches_result = cur.fetchone()

    matches = matches_result['match_count'] if matches_result else 0

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM user_preferences
        WHERE user_id = %s
    """, (user_id,))

    total_result = cur.fetchone()

    total = total_result['total'] if total_result else 0

    cur.close()

    if total == 0:
        return 0

    compatibility = int((matches / total) * 100)

    return compatibility

def save_user_preferences(user_id, selected_preferences):
    if session.get("logged_in") and session["user"]["role"] == "buyer":
        cur = mysql.connection.cursor()

        cur.execute("""
            DELETE FROM user_preferences
            WHERE user_id = %s
        """, (user_id,))

        for pref_id in selected_preferences:

            cur.execute("""
                INSERT INTO user_preferences
                (user_id, preference_id)
                VALUES (%s, %s)
            """, (user_id, pref_id))

        mysql.connection.commit()

        cur.close()

def get_user_preferences(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT preference_id
        FROM user_preferences
        WHERE user_id = %s
    """, (user_id,))
    preferences = cur.fetchall()
    cur.close()
    return [row['preference_id'] for row in preferences]

def create_enquiry(property_id, buyer_id, form):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO enquiries (
            property_id,
            buyer_id,
            subject,
            message
        )
        VALUES (%s, %s, %s, %s)
    """, (
        property_id,
        buyer_id,
        form.subject.data,
        form.message.data
    ))
    mysql.connection.commit()
    cur.close()


def get_enquiry(enquiry_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            e.enquiry_id,
            e.property_id,
            e.buyer_id,
            e.subject,
            e.message,
            e.status,
            e.created_at,
            p.seller_id,
            p.title AS property_title
        FROM enquiries e
        JOIN properties p ON e.property_id = p.id
        WHERE e.enquiry_id = %s
    """, (enquiry_id,))
    row = cur.fetchone()
    cur.close()
    return row


def update_enquiry_status(enquiry_id, status):
    if status not in ENQUIRY_STATUSES:
        raise ValueError("Invalid enquiry status")

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE enquiries
        SET status = %s
        WHERE enquiry_id = %s
    """, (status, enquiry_id))
    mysql.connection.commit()
    cur.close()


def get_offer(user_id, property_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, buyer_id, property_id, offered_price, status, created_at
        FROM offers
        WHERE buyer_id = %s AND property_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT 1
    """, (user_id, property_id))
    row = cur.fetchone()
    cur.close()
    return row


def create_offer(property_id, buyer_id, offered_price):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id
        FROM offers
        WHERE buyer_id = %s AND property_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT 1
    """, (buyer_id, property_id))
    existing_offer = cur.fetchone()

    if existing_offer:
        cur.execute("""
            UPDATE offers
            SET offered_price = %s,
                status = 'pending',
                created_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (offered_price, existing_offer['id']))
    else:
        cur.execute("""
            INSERT INTO offers (buyer_id, property_id, offered_price, status)
            VALUES (%s, %s, %s, 'pending')
        """, (buyer_id, property_id, offered_price))

    mysql.connection.commit()
    cur.close()


def update_offer_status(offer_id, status):
    if status not in OFFER_STATUSES:
        raise ValueError("Invalid offer status")

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE offers
        SET status = %s
        WHERE id = %s
    """, (status, offer_id))
    mysql.connection.commit()
    cur.close()


def get_bookmark(user_id, property_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, user_id, property_id, note, created_at
        FROM bookmarks
        WHERE user_id = %s AND property_id = %s
    """, (user_id, property_id))
    row = cur.fetchone()
    cur.close()
    return row


def get_bookmarks(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            b.id AS bookmark_id,
            b.user_id,
            b.property_id,
            b.note,
            b.created_at AS bookmarked_at,
            p.title,
            p.property_type,
            p.price,
            p.suburb,
            p.city,
            p.postcode,
            pi.image AS cover_image,
            p.description,
            p.seller_id,
            u.firstname AS seller_firstname,
            u.lastname AS seller_lastname
        FROM bookmarks b
        JOIN properties p ON b.property_id = p.id
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN property_images pi
            ON pi.id = (
                SELECT pi2.id
                FROM property_images pi2
                WHERE pi2.property_id = p.id
                ORDER BY pi2.display_order ASC, pi2.id ASC
                LIMIT 1
            )
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    """, (user_id,))
    bookmarks = cur.fetchall()
    cur.close()
    return bookmarks


def save_bookmark(user_id, property_id, note):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO bookmarks (user_id, property_id, note)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            note = VALUES(note),
            created_at = CURRENT_TIMESTAMP
    """, (user_id, property_id, note))
    mysql.connection.commit()
    cur.close()


def remove_bookmark(user_id, property_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE FROM bookmarks
        WHERE user_id = %s AND property_id = %s
    """, (user_id, property_id))
    mysql.connection.commit()
    cur.close()
