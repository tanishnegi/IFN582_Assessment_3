from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    firstname: str
    lastname: str
    email: str
    password: str
    phone: str
    role: str


@dataclass
class Property:
    id: int
    title: str
    property_type: str
    price: float
    suburb: str
    city: str
    postcode: str
    bedrooms: int
    bathrooms: int
    occupants: int
    image: str
    description: str
    created_at: datetime

    compatibility: int = 0
    images: list = None
    host_preferences: list = None

@dataclass
class Preference:
    id: int
    name: str   

@dataclass
class PropertyPreference:
    property_id: int
    preference_id: int

@dataclass
class UserPreference:
    user_id: int
    preference_id: int

@dataclass
class Enquiry:
    enquiry_id: int
    property_id: int
    buyer_id: int
    subject: str
    message: str
    created_at: datetime
