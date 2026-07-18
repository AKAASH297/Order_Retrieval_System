from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

# Shared password complexity pattern (same as auth/forms.py)
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{}|;:,.<>?/~`]).+$'
PASSWORD_MESSAGE = (
    'Password must contain at least one uppercase letter, one lowercase '
    'letter, one digit, and one special character.'
)


class CreateUserForm(FlaskForm):
    username = StringField('Username (Customer ID)', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(PASSWORD_REGEX, message=PASSWORD_MESSAGE),
    ])
    submit = SubmitField('Create User')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(PASSWORD_REGEX, message=PASSWORD_MESSAGE),
    ])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')]
    )
    submit = SubmitField('Reset Password')
