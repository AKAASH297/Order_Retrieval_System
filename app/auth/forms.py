import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

# Password must contain at least one uppercase, one lowercase, one digit,
# and one special character.
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{}|;:,.<>?/~`]).+$')
PASSWORD_MESSAGE = (
    'Password must contain at least one uppercase letter, one lowercase '
    'letter, one digit, and one special character.'
)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(PASSWORD_REGEX, message=PASSWORD_MESSAGE),
    ])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')]
    )
    submit = SubmitField('Change Password')
