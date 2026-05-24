from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import email,InputRequired

class RegisterForm(FlaskForm):
    """Form for user registry."""
    firstname = StringField("Your first name", validators = [InputRequired()])
    lastname = StringField("Your surname", validators = [InputRequired()])
    email = StringField("Email", validators = [InputRequired(), email()])
    password = PasswordField("Password", validators = [InputRequired()])
    phone = StringField("Your phone number", validators = [InputRequired()])
    role = SelectField(
        "Select Role",
        choices=[
            ("buyer", "Tenant"),
            ("seller", "Listing Owner")
        ]
    )
    submit = SubmitField("Make Account")

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField("Email", validators = [InputRequired(), email()])
    password = PasswordField("Password", validators = [InputRequired()])
    submit = SubmitField("Login")

class EnquiryForm(FlaskForm):
    """Form for property enquiries."""
    subject = StringField("Subject", validators=[InputRequired()])
    message = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send Enquiry")


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
            ("Entire Apartment", "Entire Apartment")
        ]
    )

    price_range = SelectField(
        "Weekly Rent",
        choices=[
            ("Any Price", "Any Price"),
            ("Under $300", "Under $300"),
            ("$300 - $500", "$300 - $500"),
            ("$500 - $800", "$500 - $800"),
            ("$800+", "$800+")
        ]
    )

    bedrooms = SelectField(
        "Bedrooms",
        choices=[
            ("Any Room", "Any Room"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4+", "4+")
        ]
    )

    sort_by = SelectField(
    "Sort By",
    choices=[
        ("default", "Sort by - Recently Added"),
        ("price_low", "Sort by - Price (Low to High)"),
        ("price_high", "Sort by - Price (High to Low)"),
    ]
)

    submit = SubmitField("Apply")
