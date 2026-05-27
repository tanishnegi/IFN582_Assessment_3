from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    PasswordField,
    TextAreaField,
    IntegerField,
    DecimalField,
)
from wtforms.validators import email, InputRequired, Length, NumberRange


class RegisterForm(FlaskForm):
    """Form for user registry."""

    firstname = StringField("Your first name", validators=[InputRequired()])
    lastname = StringField("Your surname", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), email()])
    password = PasswordField("Password", validators=[InputRequired()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    role = SelectField(
        "Select Role", choices=[("buyer", "Tenant"), ("seller", "Listing Owner")]
    )
    submit = SubmitField("Make Account")


class AdminUserForm(FlaskForm):
    """Form for admin-created user accounts."""

    firstname = StringField("First name", validators=[InputRequired()])
    lastname = StringField("Last name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), email()])
    password = PasswordField("Password", validators=[InputRequired()])
    phone = StringField("Phone number", validators=[InputRequired()])
    role = SelectField(
        "Role",
        choices=[
            ("admin", "Admin"),
            ("seller", "Listing Owner"),
            ("buyer", "Tenant"),
        ],
    )
    submit = SubmitField("Create Account")


class PropertyForm(FlaskForm):
    """Form for creating and editing property listings."""

    title = StringField("Title", validators=[InputRequired()])
    property_type = SelectField(
        "Property type",
        choices=[
            ("Shared Apartment", "Shared Apartment"),
            ("Private Room", "Private Room"),
            ("Shared House", "Shared House"),
            ("Studio", "Studio"),
            ("Entire Apartment", "Entire Apartment"),
        ],
    )
    price = DecimalField(
        "Weekly rent",
        validators=[
            InputRequired(),
            NumberRange(min=0.01),
        ],
        places=2,
    )
    suburb = StringField("Suburb", validators=[InputRequired()])
    city = StringField("City", validators=[InputRequired()])
    postcode = StringField(
        "Postcode",
        validators=[
            InputRequired(),
            Length(min=4, max=4),
        ],
    )
    bedrooms = IntegerField(
        "Bedrooms",
        validators=[InputRequired(), NumberRange(min=1)],
    )
    bathrooms = IntegerField(
        "Bathrooms",
        validators=[InputRequired(), NumberRange(min=1)],
    )
    occupants = IntegerField(
        "Occupants",
        validators=[InputRequired(), NumberRange(min=1)],
    )
    status = SelectField(
        "Status",
        choices=[
            ("available", "Available"),
            ("unavailable", "Unavailable"),
        ],
    )
    latitude = DecimalField(
        "Latitude",
        validators=[
            InputRequired(),
            NumberRange(min=-90, max=90),
        ],
        places=8,
    )
    longitude = DecimalField(
        "Longitude",
        validators=[
            InputRequired(),
            NumberRange(min=-180, max=180),
        ],
        places=8,
    )
    description = TextAreaField("Description", validators=[InputRequired()])
    preferences = SelectMultipleField("Lifestyle preferences", coerce=int)
    submit = SubmitField("Save Listing")


class LoginForm(FlaskForm):
    """Form for user login."""

    email = StringField("Email", validators=[InputRequired(), email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class EnquiryForm(FlaskForm):
    """Form for property enquiries."""

    subject = StringField("Subject", validators=[InputRequired()])
    message = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send Enquiry")


class OfferForm(FlaskForm):
    """Form for submitting an offer or rental intent."""

    offered_price = DecimalField(
        "Offer amount",
        validators=[
            InputRequired(),
            NumberRange(min=0.01, message="Enter an offer above $0."),
        ],
        places=2,
    )
    submit = SubmitField("Submit Offer")


class BookmarkForm(FlaskForm):
    """Form for saving a property bookmark note."""

    note = TextAreaField("Personal note")
    submit = SubmitField("Save Bookmark")


class SearchForm(FlaskForm):

    location = StringField("Suburb or Postcode")

    property_type = SelectField(
        "Type",
        choices=[
            ("Any Type", "Any Type"),
            ("Shared Apartment", "Shared Apartment"),
            ("Private Room", "Private Room"),
            ("Shared House", "Shared House"),
            ("Studio", "Studio"),
            ("Entire Apartment", "Entire Apartment"),
        ],
    )

    price_range = SelectField(
        "Weekly Rent",
        choices=[
            ("Any Price", "Any Price"),
            ("Under $300", "Under $300"),
            ("$300 - $500", "$300 - $500"),
            ("$500 - $800", "$500 - $800"),
            ("$800+", "$800+"),
        ],
    )

    bedrooms = SelectField(
        "Bedrooms",
        choices=[
            ("Any Room", "Any Room"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4+", "4+"),
        ],
    )

    sort_by = SelectField(
        "Sort By",
        choices=[
            ("default", "Sort by - Recently Added"),
            ("price_low", "Sort by - Price (Low to High)"),
            ("price_high", "Sort by - Price (High to Low)"),
        ],
    )

    submit = SubmitField("Apply")
