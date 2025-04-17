from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from db import get_user_by_email, get_user_by_username

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])

class TripForm(FlaskForm):
    title = StringField('Trip Title', validators=[DataRequired()])
    destination_id = SelectField('Destination', validators=[DataRequired()])
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    budget = DecimalField('Budget (USD)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    is_public = BooleanField('Make this trip public', default=False)

class ActivityForm(FlaskForm):
    name = StringField('Activity Name', validators=[DataRequired()])
    time = StringField('Time', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    cost = DecimalField('Cost', validators=[Optional()])

class ExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('accommodation', 'Accommodation'),
        ('transportation', 'Transportation'),
        ('food', 'Food & Drinks'),
        ('activities', 'Activities & Entertainment'),
        ('shopping', 'Shopping'),
        ('other', 'Other')
    ])
    description = StringField('Description', validators=[Optional()])
    date = StringField('Date', validators=[DataRequired()])
    currency = StringField('Currency', default='USD', validators=[Optional()])

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])