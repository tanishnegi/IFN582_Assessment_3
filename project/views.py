from flask import Blueprint, render_template, request, session, flash

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    properties = [
        {
            "id": 1,
            "title": "Room in Brisbane CBD",
            "price": 220,
            "location": "Brisbane, QLD",
            "occupants": 2,
            "bathrooms": 1,
            "compatibility": "High Compatibility",
            "badge": "success",
            "image": "img/pexels-artbovich-7019026.jpg"
        },
        {
            "id": 2,
            "title": "Bright & Airy Shared Apartment",
            "price": 240,
            "location": "Brisbane, QLD",
            "occupants": 2,
            "bathrooms": 2,
            "compatibility": "High Compatibility",
            "badge": "success",
            "image": "img/pexels-pixabay-271618.jpg"
        },
        {
            "id": 3,
            "title": "City View Apartment",
            "price": 280,
            "location": "Brisbane, QLD",
            "occupants": 3,
            "bathrooms": 3,
            "compatibility": "Moderate Compatibility",
            "badge": "warning",
            "image": "img/pexels-fotoaibe-1571453.jpg"
        }
    ]
    return render_template('home.html', properties=properties)